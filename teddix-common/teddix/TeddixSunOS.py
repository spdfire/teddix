#!/usr/bin/env python
#

import os
import re
import sys
import time
import psutil
import platform
import subprocess

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile
import TeddixParser 


class TeddixSunOS:

    def __init__(self,syslog):
        self.syslog = syslog
        
        self.system = platform.system()
        self.arch = platform.architecture()
        self.machine = platform.machine()
        self.release = platform.release()

        self.syslog.info("Detected: %s (%s) arch: %s" % (self.system,self.release,self.machine))

    # Get PCI devices 
    def getpci(self):
        self.syslog.debug("Detecting PCI devices " )
        parser = TeddixParser.TeddixStringParser() 

        lines       = parser.readstdout('scanpci')
        pcidev = {}
        k = 0 
        for i in range(len(lines)):
            if parser.strsearch('^pci bus 0x(\d+) cardnum 0x\d+',lines[i]):

                bus     = parser.strsearch('^pci bus 0x(\d+) cardnum 0x\d+',lines[i])
                nr      = parser.strsearch('^pci bus 0x\d+ cardnum 0x(\d+)',lines[i])
                path    = bus + ':' + nr 
                devtype = parser.strsearch('^pci bus 0x\d+ cardnum 0x\d+ function 0x(\d+)',lines[i])
                vendor  = parser.strsearch('^pci bus 0x\d+ cardnum 0x\d+ function 0x\d+: vendor 0x(\d+)',lines[i])
                j = i + 1
                model   = lines[j]
                revision= ''

                pcidev[k]   = [path,devtype,vendor,model,revision] 
                k += 1

        return pcidev

    # Get Block devices 
    def getblock(self):
        self.syslog.debug("Detecting block devices " )
        parser = TeddixParser.TeddixStringParser() 

        lines       = parser.readstdout('iostat -Enr')
        blockdev = {}
        for i in range(len(lines)):
            if parser.strsearch('^(\w+),Soft Errors:[ \d]+,Hard Errors:[ \d]+,Transport Errors:[ \d]+',lines[i]):
                name        = parser.strsearch('^(\w+),Soft Errors:[ \d]+,Hard Errors:[ \d]+,Transport Errors:[ \d]+',lines[i])
                
                lines2      = parser.readstdout('fdisk -GR ' + name + 'p0')
                sect_size   = parser.arraysearch('\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+(\d+)',lines2)
                ncyl        = parser.arraysearch('\d+[ ]+(\d+)[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+',lines2)
                nhead       = parser.arraysearch('\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+(\d+)[ ]+\d+[ ]+\d+',lines2)
                nsect       = parser.arraysearch('\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+(\d+)[ ]+\d+',lines2)
                nr_sectors  = unicode(parser.str2int(ncyl) * parser.str2int(nhead) * parser.str2int(nsect))

                lines2      = parser.readstdout('iostat -Enr ' + name ) 
                model       = parser.arraysearch('Model:(.+),',lines2)
                rotational  = ''
                readonly    = ''
                removable   = ''
                vendor      = parser.arraysearch('Vendor:(.+),',lines2)

                major       = ''
                minor       = ''
                devtype     = ''

                blockdev[i] = [name,devtype,vendor,model,nr_sectors,sect_size,rotational,readonly,removable,major,minor]
                i += 1

        return blockdev

    # Get installed packages
    def getpkgs(self):
        self.syslog.debug("Getting package list " )
        parser = TeddixParser.TeddixStringParser() 
        
        packages = { }
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        if parser.checkexec('pkg'):
            self.syslog.debug("System %s (%s) is IPS based " % (self.system,self.release))
            lines       = parser.readstdout('pkg list')
            for i in range(len(lines)):
                name        = parser.strsearch('^([^ ]+)[ ]+',lines[i])

                lines2      = parser.readstdout('pkg info ' + name )
                ver         = parser.strsearch('Version: (.+)',lines2[i])
                pkgsize     = parser.strsearch('Size: (.+)',lines2[i])
                instalsize  = ''
                section     = parser.strsearch('Category: (.+)',lines2[i])
                status      = parser.strsearch('State: (.+)',lines2[i])
                info        = parser.strsearch('Summary: (.+)',lines2[i])
                homepage    = ''
                signed      = ''
                files       = ''
                arch        = ''
                publisher   = parser.strsearch('Publisher: (.+)',lines2[i])
                release     = parser.strsearch('Build Release: (.+)',lines2[i])
            
                packages[i] = [name,var,pkgsize,instalsize,section,status,info,homepage,signed,files,arch] 
                i += 1
        else:
            self.syslog.warn("Unknown pkg system for %s " % self.dist[0])

        return packages


    # Get partitions
    def getpartitions(self):
        self.syslog.debug("Getting filesystem list ")
        parser = TeddixParser.TeddixStringParser() 

        disks = { }
        mounts = psutil.disk_partitions() 
        for part in psutil.disk_partitions():
            
            # get addtional info 
            if part.mountpoint:
                usage = psutil.disk_usage(part.mountpoint)

                fstotal = parser.str2uni(usage.total)
                fsused = parser.str2uni(usage.used)
                fsfree = parser.str2uni(usage.free)
                fspercent = parser.str2uni(usage.percent)
    
            fsdev = parser.str2uni(part.device)
            fsmount = parser.str2uni(part.mountpoint)
            fstype = parser.str2uni(part.fstype)
            fsopts = parser.str2uni(part.opts)

            disks[i] = [fsdev,fsmount,fstype,fsopts,fstotal,fsused,fsfree,fspercent]
            i += 1

        return disks


    # Get swap 
    def getswap(self):
        self.syslog.debug("Reading swap filesystems")
        parser = TeddixParser.TeddixStringParser() 

        output  = parser.readstdout("swap -l")
        lines   = parser.arrayfilter('^[^ ]+\W+[^ ]+\W+\d+\W+\d+\W+\d+',output)

        swaps = { }
        for i in range(len(lines)):
            dev         = parser.strsearch('^([^ ]+)\W+[^ ]+\W+\d+\W+\d+\W+\d+',lines[i])
            swaptype    = ''
            total       = parser.strsearch('^[^ ]+\W+[^ ]+\W+\d+\W+(\d+)\W+\d+',lines[i])
            used        = parser.strsearch('^[^ ]+\W+[^ ]+\W+\d+\W+\d+\W+(\d+)',lines[i])
            free        = unicode(parser.str2int(total) - parser.str2int(used))
                  
            swaps[i] = [dev,swaptype,total,used,free] 
            i += 1
                  
        return swaps

 
    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")
        parser = TeddixParser.TeddixStringParser()
        
        # netstat -inf inet 
        output  = parser.readstdout('netstat -inf inet')
        lines   = parser.arrayfilter('^\w+[ ]+\d+[ ]+[\d\.]+[ ]+[\d\.]+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+',output)
        
        nics = {}
        for i in range(len(lines)):
            name        = parser.strsearch('^(\w+)[ ]+\d+[ ]+[\d\.]+[ ]+[\d\.]+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+[ ]+\d+',lines[i])

            lines2      = parser.readstdout("ifconfig " + name)
            macaddr     = parser.arraysearch('ether ([\w:.-]+)',lines2)

            lines2      = parser.readstdout("kstat -c net -n " + name)
            rx_packets  = parser.arraysearch('ipackets[ ]+(\d+)',lines2)
            rx_bytes    = parser.arraysearch('ibytes[ ]+(\d+)',lines2)
            tx_packets  = parser.arraysearch('opackets[ ]+(\d+)',lines2)
            tx_bytes    = parser.arraysearch('obytes[ ]+(\d+)',lines2)
            
            lines       = parser.readstdout("modinfo " + driver)
            description = parser.arraysearch('^description:\W+(.+)',lines)
            drvver      = parser.arraysearch('^version:\W*(.+)',lines)
            
            # TODO: 
            nictype     = ''
            status      = ''
            driver      = ''
            firmware    = ''
            kernmodule  = ''


            nics[i] = [name,description,nictype,status,rx_packets,tx_packets,rx_bytes,tx_bytes,driver,drvver,firmware,kernmodule,macaddr]
            i += 1
        
        return nics

    # Get ipv4 address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser()

        output  = parser.readstdout("ifconfig " + nic)
        lines   = parser.arrayfilter('inet[ ]+\d+\.\d+\.\d+\.\d+[ ]+netmask[ ]+\w+[ ]+(broadcast[ ]+\d+\.\d+\.\d+\.\d+|)',output)
      
        ips = { }
        for i in range(len(lines)):
            ipv4    = parser.strsearch('inet[ ]+(\d+\.\d+\.\d+\.\d+)[ ]+netmask[ ]+\w+[ ]+(broadcast[ ]+\d+\.\d+\.\d+\.\d+|)',lines[i])
            mask    = parser.strsearch('inet[ ]+\d+\.\d+\.\d+\.\d+[ ]+netmask[ ]+(\w+)[ ]+(broadcast[ ]+\d+\.\d+\.\d+\.\d+|)',lines[i])
            bcast   = parser.strsearch('inet[ ]+\d+\.\d+\.\d+\.\d+[ ]+netmask[ ]+\w+[ ]+(broadcast[ ]+(\d+\.\d+\.\d+\.\d+)|)',lines[i])
       
            ips[i] = [ipv4,mask,bcast]
            i += 1

        return ips

    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

        # XXX: rtls0:1, rtls0:2
        output  = parser.readstdout("ifconfig " + nic)
        lines   = parser.arrayfilter('inet6[ \t]+([a-fA-F\d\:]+)/(\d+)',output)
      
        ips6 = { }
        for i in range(len(lines)):
            ipv6    = parser.strsearch('inet6[ \t]+([a-fA-F\d\:]+)/\d+',lines[i])
            mask    = parser.strsearch('inet6[ \t]+[a-fA-F\d\:]+/(\d+)',lines[i])
            bcast   = ''
       
            ips6[i] = [ipv6,mask,bcast]
            i += 1

        return ips6


    # Get dnsservers 
    def getdns(self):
        self.syslog.debug("Reading DNS configuration")
        parser = TeddixParser.TeddixStringParser() 
        lines       = parser.readlines('/etc/resolv.conf')

        i = 0
        j = 0
        dns = { }
        for i in range(len(lines)):
            nameserver   = parser.strsearch('^nameserver[ \t]+(.+)',lines[i])
            domain       = parser.strsearch('^domain[ \t]+(.+)',lines[i])
            search       = parser.strsearch('^search[ \t]+(.+)',lines[i])
            if nameserver:
                dns[j] = ['nameserver',nameserver]
                j += 1
            elif domain:
                dns[j] = ['domain',domain]
                j += 1
            elif search:
                dns[j] = ['search',search]
                j += 1
                  
            i += 1
 
        return dns


    # Get routes 
    def getroutes(self):
        self.syslog.debug("Reading routing table for ipv4 ")
        parser = TeddixParser.TeddixStringParser() 
 
        output  = parser.readstdout("netstat -rnv -f inet")
        lines   = parser.arrayfilter('[\w\.]+[ ]+[\d\.]+[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',output)
     
        routes = { }
        for i in range(len(lines)):
            destination = parser.strsearch('([\w\.]+)[ ]+[\d\.]+[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            mask        = parser.strsearch('[\w\.]+[ ]+([\d\.]+)[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            gateway     = parser.strsearch('[\w\.]+[ ]+[\d\.]+[ ]+([\d\.]+)[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            interface   = parser.strsearch('[\w\.]+[ ]+[\d\.]+[ ]+[\d\.]+[ ]+(\w+)[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            flags       = parser.strsearch('[\w\.]+[ ]+[\d\.]+[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+(\w+)[ ]+\d+[ ]+\d+',lines[i])
            metric      = ''
            routes[i] = [destination,gateway,mask,flags,metric,interface] 
            i += 1

        return routes


    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")
        parser = TeddixParser.TeddixStringParser() 
        
        output  = parser.readstdout("netstat -rnv -f inet6")
        lines   = parser.arrayfilter('[\w:]+/\d+[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',output)
     
        routes6 = { }
        for i in range(len(lines)):
            destination = parser.strsearch('([\w:]+)/\d+[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            mask        = parser.strsearch('[\w:]+/(\d+)[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            gateway     = parser.strsearch('[\w:]+/\d+[ ]+([\w:]+)[ ]+\w+[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            interface   = parser.strsearch('[\w:]+/\d+[ ]+[\w:]+[ ]+(\w+)[ ]+\d+[ ]+\d+[ ]+\w+[ ]+\d+[ ]+\d+',lines[i])
            flags       = parser.strsearch('[\w:]+/\d+[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+(\w+)[ ]+\d+[ ]+\d+',lines[i])
            metric      = ''
            routes6[i] = [destination,mask,gateway,flags,metric,interface] 
            i += 1

        return routes6



    # Get groups 
    def getgroups(self):
        self.syslog.debug("Reading system groups")
        parser = TeddixParser.TeddixStringParser() 
        
        lines       = parser.readlines('/etc/group')

        groups = { }
        for i in range(len(lines)):
            name        = parser.strsearch('^(.+):.+:.+:.*',lines[i])
            gid         = parser.strsearch('^.+:.+:(.+):.*',lines[i])
            members     = parser.strsearch('^.+:.+:.+:(.*)',lines[i])
            
            groups[i]   = [name,gid,members]
            i += 1

        return groups


    # Get users 
    def getusers(self):
        self.syslog.debug("Reading system users")
        parser = TeddixParser.TeddixStringParser() 

        pwlines       = parser.readlines('/etc/passwd')
        swlines       = parser.readlines('/etc/shadow')
        gplines       = parser.readlines('/etc/group')

        users = {}
        for i in range(len(pwlines)):
            login       = parser.strsearch('^(.+):.+:.+:.+:.*:.+:.*',pwlines[i])
            uid         = parser.strsearch('^.+:.+:(.+):.+:.*:.+:.*',pwlines[i])
            gid         = parser.strsearch('^.+:.+:.+:(.+):.*:.+:.*',pwlines[i])
            comment     = parser.strsearch('^.+:.+:.+:.+:(.*):.+:.*',pwlines[i])
            home        = parser.strsearch('^.+:.+:.+:.+:.*:(.+):.*',pwlines[i])
            shell       = parser.strsearch('^.+:.+:.+:.+:.*:.+:(.*)',pwlines[i])
            locked      = ''
            hashtype    = ''
            groups      = ''
            
            for j in range(len(swlines)):
                login2   = parser.strsearch('^(.+):.*:.*:.*:.*:.*:.*:.*:.*',swlines[j])
                if login == login2:
                    hashdata   = parser.strsearch('^.+:(.*):.*:.*:.*:.*:.*:.*:.*',swlines[j])
                    if hashdata == '*LK*':
                        locked = 'True'
                    elif hashdata == 'NP': # nopasswd -> locked? 
                        locked = 'True'
                    else:
                        match = parser.strsearch('(\$\d)\$.+',hashdata)
                        if match:
                            if match == '$1':
                                hashtype = 'md5'
                                locked = 'False'
                            if match == '$2':
                                hashtype = 'blowfish'
                                locked = 'False'
                            if match == '$5':
                                hashtype = 'sha256'
                                locked = 'False'
                            if match == '$6':
                                hashtype = 'sha512'
                                locked = 'False'
                            else:
                                hashtype = 'des'
                                locked = 'False'

            for k in range(len(gplines)):
                login3   = parser.strsearch('^(.+):.+:.+:.*',gplines[k])
                if login == login3:
                    groups = parser.strsearch('.+:.+:.+:(.*)',gplines[k])

            users[i] = [login,uid,gid,comment,home,shell,locked,hashtype,groups]
            i += 1
 
        return users


    # Get procs 
    def getprocs(self):
        self.syslog.debug("Listing system procs")
        parser = TeddixParser.TeddixStringParser() 

        procs = {}
        i = 0
        for p in psutil.process_iter():
            ppid = parser.str2uni(p.pid)
            powner = parser.str2uni(p.username)
            
            pcputime = p.get_cpu_times()
            psystime = parser.str2uni(pcputime.system)
            pusertime = parser.str2uni(pcputime.user)

            # TODO: it takes too much time
            #pcpu = p.get_cpu_percent(interval=0.1)
            pcpu = ''
            pmem = p.get_memory_percent()
            pmem = parser.str2uni(pmem)
            ppriority = parser.str2uni(p.get_nice())
            pstatus = parser.str2uni(p.status)
            powner = parser.str2uni(p.username)
            pname = parser.str2uni(p.name)

            pcmd = ''
            for pp in p.cmdline:
                pp += ' '
                pcmd += pp  
            pcmd = parser.str2uni(pcmd)

            procs[i] = [ppid,powner,psystime,pusertime,pcpu,pmem,ppriority,pstatus,pname,pcmd]
            i += 1 

        return procs


    # Get services
    def getsvcs(self):
        self.syslog.debug("Getting system services")
        parser = TeddixParser.TeddixStringParser() 
 
        svcs = { } 
        lines   = parser.readstdout('svcs -aH -o svc,state')
        for i in range(len(lines)):
            name        = parser.strsearch('(.+)\W*\w+',lines[i])
            boot        = parser.strsearch('.+\W*(\w+)',lines[i])
            status      = boot
                    
            svcs[i] = [name,boot,status]
            i += 1
 
        return svcs


    # Get updates
    def getupdates(self):
        self.syslog.debug("Listing available updates")
        parser = TeddixParser.TeddixStringParser() 
        
        updates = { }
        if parser.checkexec('pkg'):
            lines   = parser.readstdout('pkg update -nv')
            for i in range(len(lines)):
                utype = ''
                pkg   = ''
                nver  = ''
                updates[i] = [utype,pkg,nver]
                i += 1

        return updates



