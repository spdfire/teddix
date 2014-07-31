#!/usr/bin/env python
#

import os
import re
import sys
import time
import glob
import psutil
import platform
import netifaces
import subprocess

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile
import TeddixParser 

class TeddixLinux:

    def __init__(self,syslog):
        self.syslog = syslog
        
        self.system     = platform.system()
        self.arch       = platform.architecture()
        self.machine    = platform.machine()
        self.name       = platform.linux_distribution()[0]
        self.ver        = platform.linux_distribution()[1]
        self.detail     = self.name + self.ver 
        self.kernel     = platform.release()
        self.manufacturer= ''
        self.serial     = ''

        self.syslog.info("Detected: %s (%s %s) arch: %s" % (self.system,self.name,self.ver,self.machine))

    # Get PCI devices 
    def getpci(self):
        parser = TeddixParser.TeddixStringParser() 
        
        lines = parser.readstdout('lspci -m')

        pcidev = { }
        for i in range(len(lines)):
            path        = parser.strsearch('^(.+) ".+" ".+" ".+".+\-r\w+ .+',lines[i])
            devtype     = parser.strsearch('^.+ "(.+)" ".+" ".+".+\-r\w+ .+',lines[i])
            vendor      = parser.strsearch('^.+ ".+" "(.+)" ".+".+\-r\w+ .+',lines[i])
            model       = parser.strsearch('^.+ ".+" ".+" "(.+)".+\-r\w+ .+',lines[i])
            revision    = parser.strsearch('^.+ ".+" ".+" ".+".+\-r(\w+) .+',lines[i])

            pcidev[i]   = [path,devtype,vendor,model,revision] 
            i += 1

        return pcidev 

    # Get Block devices 
    def getblock(self):
        dev_pattern = ['sd.*','hd.*','vd.*','sr.*','mmcblk*']
        self.syslog.debug("Detecting blockdevices " )
        parser = TeddixParser.TeddixStringParser() 
        
        blockdev = {}
        i = 0
        for device in glob.glob('/sys/block/*'):
            for pattern in dev_pattern:
                if re.compile(pattern).match(os.path.basename(device)):
                    nr_sectors  = parser.readline(device + '/size')
                    sect_size   = parser.readline(device+'/queue/hw_sector_size')
                    model       = parser.readline(device+'/device/model')
                    rotational  = parser.readlineyesno(device+'/queue/rotational')
                    readonly    = parser.readlineyesno(device+'/ro')
                    removable   = parser.readlineyesno(device+'/removable')
                    vendor      = parser.readline(device+'/device/vendor')

                    lines       = parser.readlines(device+'/uevent')
                    major       = parser.arraysearch('MAJOR\=(\d+)',lines)
                    minor       = parser.arraysearch('MINOR\=(\d+)',lines)
                    name        = parser.arraysearch('DEVNAME\=(.+)',lines)
                    devtype     = parser.arraysearch('DEVTYPE\=(.+)',lines)

                    blockdev[i] = [name,devtype,vendor,model,nr_sectors,sect_size,rotational,readonly,removable,major,minor]
                    i += 1

        return blockdev


    # Get installed packages
    def getpkgs(self):
        parser = TeddixParser.TeddixStringParser()
        lines = ''
        
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        if parser.checkexec('rpm'):
            self.syslog.debug("%s is RPM based" % self.system)
            cmd = "rpm -qa --queryformat '\[%{NAME}\]\[%{VERSION}-%{RELEASE}\]\[%{ARCHIVESIZE}\]\[%{SIZE}\]\[%{GROUP}\]\[installed\]\[%{SUMMARY}\]\[%{URL}\]\[\]\[\]\[%{ARCH}\]\n'"
            lines = parser.readstdout(cmd)
        if parser.checkexec('dpkg-query'):
            self.syslog.debug("%s is DEB based " % self.system)
            cmd = "dpkg-query --show --showformat='[${Package}][${Version}][][${Installed-Size}][${Section}][${Status}][${binary:Summary}][${Homepage}][][][${Architecture}]\n'"
            lines = parser.readstdout(cmd)

        packages = { }
        i = 0 
        for i in range(len(lines)):
            # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
            name        = parser.strsearch('\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            var         = parser.strsearch('\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            pkgsize     = parser.strsearch('\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            instalsize  = parser.strsearch('\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            section     = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            status      = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            info        = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]\[.*\]',lines[i])
            homepage    = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]\[.*\]',lines[i])
            signed      = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]\[.*\]',lines[i])
            files       = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]\[.*\]',lines[i])
            arch        = parser.strsearch('\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[.*\]\[(.*)\]',lines[i])

            packages[i] = [name,var,pkgsize,instalsize,section,status,info,homepage,signed,files,arch] 
            i += 1

        return packages

    # Get partitions
    def getpartitions(self):
        parser = TeddixParser.TeddixStringParser() 
        self.syslog.debug("Getting filesystem list ")

        i = 0 
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
        parser = TeddixParser.TeddixStringParser() 
        self.syslog.debug("Reading swap filesystems")

        output  = parser.readlines('/proc/swaps')
        lines   = parser.arrayfilter('^([^ ]+)[ ]+\w+\W+\d+\W+\d+',output)

        swaps = { }
        for i in range(len(lines)):
            dev         = parser.strsearch('^([^ ]+)[ ]+\w+\W+\d+\W+\d+',lines[i])
            swaptype    = parser.strsearch('^[^ ]+[ ]+(\w+)\W+\d+\W+\d+',lines[i])
            total       = parser.strsearch('^[^ ]+[ ]+\w+\W+(\d+)\W+\d+',lines[i])
            used        = parser.strsearch('^[^ ]+[ ]+\w+\W+\d+\W+(\d+)',lines[i])
            free        = unicode(parser.str2int(total) - parser.str2int(used))
                  
            swaps[i] = [dev,swaptype,total,used,free] 
            i += 1
                  
        return swaps


    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")
        parser = TeddixParser.TeddixStringParser() 

        names = netifaces.interfaces() 

        nics = {}
        i = 0
        for name in names:

            # ignore eth0:1
            match = re.search(r'.+:\d+',name)
            if match:
                continue 

            lines       = parser.readstdout("ethtool -i " + name)
            driver      = parser.arraysearch('^driver: (\w+)',lines)
            firmware    = parser.arraysearch('^firmware-version: (.+)',lines)
            
            lines       = parser.readstdout("ethtool -P " + name)
            macaddr     = parser.arraysearch('^Permanent address: ([\w:.-]+)',lines)
            
            lines       = parser.readstdout("ethtool -S " + name)
            rx_packets  = parser.arraysearch('rx_packets: (\d+)',lines)
            rx_bytes    = parser.arraysearch('rx_bytes: (\d+)',lines)
            tx_packets  = parser.arraysearch('tx_packets: (\d+)',lines)
            tx_bytes    = parser.arraysearch('tx_bytes: (\d+)',lines)
            
            lines       = parser.readstdout("modinfo " + driver)
            description = parser.arraysearch('^description:\W+(.+)',lines)
            drvver      = parser.arraysearch('^version:\W*(.+)',lines)
            
            kernmodule = driver

            # TODO: 
            nictype = ''
            status = ''

            nics[i] = [name,description,nictype,status,rx_packets,tx_packets,rx_bytes,tx_bytes,driver,drvver,firmware,kernmodule,macaddr]
            i += 1
        
        return nics
            
    # Get ipv address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

        output  = parser.readstdout("ip -4 addr list dev " + nic)
        lines   = parser.arrayfilter('inet\W+(\d+\.\d+\.\d+\.\d+)/\d+\W+(brd\W+(\d+\.\d+\.\d+\.\d+)|)',output)
      
        ips = { }
        for i in range(len(lines)):
            ipv4    = parser.strsearch('inet\W+(\d+\.\d+\.\d+\.\d+)/\d+\W+(brd\W+(\d+\.\d+\.\d+\.\d+)|)',lines[i])
            mask    = parser.strsearch('inet\W+\d+\.\d+\.\d+\.\d+/(\d+)\W+(brd\W+(\d+\.\d+\.\d+\.\d+)|)',lines[i])
            bcast   = parser.strsearch('inet\W+\d+\.\d+\.\d+\.\d+/\d+\W+brd\W+(\d+\.\d+\.\d+\.\d+)',lines[i])
       
            ips[i] = [ipv4,mask,bcast]
            i += 1

        return ips


    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

        output  = parser.readstdout("ip -6 addr list dev " + nic)
        lines   = parser.arrayfilter('inet6[ \t]+([a-fA-F\d\:]+)/(\d+)\W+',output)
      
        ips6 = { }
        for i in range(len(lines)):
            ipv6    = parser.strsearch('inet6[ \t]+([a-fA-F\d\:]+)/\d+\W+',lines[i])
            mask    = parser.strsearch('inet6[ \t]+[a-fA-F\d\:]+/(\d+)\W+',lines[i])
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

        output  = parser.readstdout("route -n -A inet")
        lines   = parser.arrayfilter('(\d+.\d+.\d+.\d+)[ ]+\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',output)
      
        routes = { }
        for i in range(len(lines)):

            destination = parser.strsearch('(\d+.\d+.\d+.\d+)[ ]+\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            gateway     = parser.strsearch('\d+.\d+.\d+.\d+[ ]+(\d+.\d+.\d+.\d+)[ ]+\d+.\d+.\d+.\d+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            mask        = parser.strsearch('\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+(\d+.\d+.\d+.\d+)[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            flags       = parser.strsearch('\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+(\w+)[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            metric      = parser.strsearch('\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\w+[ ]+(\d+)[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            interface   = parser.strsearch('\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\d+.\d+.\d+.\d+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+([\w\-\.\:]+)',lines[i])
            routes[i] = [destination,gateway,mask,flags,metric,interface] 
            i += 1

        return routes

    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")
        parser = TeddixParser.TeddixStringParser() 

        output  = parser.readstdout("route -n -A inet6")
        lines   = parser.arrayfilter('([\w:]+)/(\d+)[ ]+([\w:]+)[ ]+(\w+)[ ]+(\d+)[ ]+\w+[ ]+\w+[ ]+([\w\-\.\:]+)',output)
      
        routes6 = { }
        for i in range(len(lines)):
            destination = parser.strsearch('([\w:]+)/\d+[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            mask        = parser.strsearch('[\w:]+/(\d+)[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            gateway     = parser.strsearch('[\w:]+/\d+[ ]+([\w:]+)[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            flags       = parser.strsearch('[\w:]+/\d+[ ]+[\w:]+[ ]+(\w+)[ ]+\d+[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            metric      = parser.strsearch('[\w:]+/\d+[ ]+[\w:]+[ ]+\w+[ ]+(\d+)[ ]+\w+[ ]+\w+[ ]+[\w\-\.\:]+',lines[i])
            interface   = parser.strsearch('[\w:]+/\d+[ ]+[\w:]+[ ]+\w+[ ]+\d+[ ]+\w+[ ]+\w+[ ]+([\w\-\.\:]+)',lines[i])
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
            login       = parser.strsearch('^(.+):.+:.+:.+:.*:.+:.+',pwlines[i])
            uid         = parser.strsearch('^.+:.+:(.+):.+:.*:.+:.+',pwlines[i])
            gid         = parser.strsearch('^.+:.+:.+:(.+):.*:.+:.+',pwlines[i])
            comment     = parser.strsearch('^.+:.+:.+:.+:(.*):.+:.+',pwlines[i])
            home        = parser.strsearch('^.+:.+:.+:.+:.*:(.+):.+',pwlines[i])
            shell       = parser.strsearch('^.+:.+:.+:.+:.*:.+:(.+)',pwlines[i])
            locked      = ''
            hashtype    = ''
            groups      = ''
            
            for j in range(len(swlines)):
                login2   = parser.strsearch('^(.+):.*:.*:.*:.*:.*:.*:.*:.*',swlines[j])
                if login == login2:
                    hashdata   = parser.strsearch('^.+:(.*):.*:.*:.*:.*:.*:.*:.*',swlines[j])
                    if hashdata == '*':
                        locked = 'True'
                    elif hashdata == '!' or hashdata == '!!':
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
            pcpu = p.get_cpu_percent(interval=0.1)
            #pcpu = ''
            #pcpu = p.get_cpu_percent(interval=None)
            pcpu = str(parser.str2float(pcpu))
            pmem = p.get_memory_percent()
            pmem = str(parser.str2float(pmem))
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
        if parser.checkexec('systemctl'):
            self.syslog.debug("System %s has systemctl command" % self.system)
            output  = parser.readstdout("systemctl list-unit-files")
            lines   = parser.arrayfilter('(.+).service\W*\w+\W*',output)
            for i in range(len(lines)):
                name        = parser.strsearch('(.+).service\W*\w+\W*',lines[i])
                boot        = parser.strsearch('.+.service\W*(\w+)\W*',lines[i])
                ret         = parser.getretval('service %s status ' % name)
                if ret == 0: 
                    status = 'running'
                else:
                    status = 'stopped'
                    
                svcs[i] = [name,boot,status]
                i += 1
 
        elif parser.checkexec('chkconfig'):
            self.syslog.debug("System %s has chkconfig command" % self.system)
            output  = parser.readstdout("chkconfig --list")
            lines   = parser.arrayfilter('^(\w+).+3:\w+',output)
            for i in range(len(lines)):
                name        = parser.strsearch('^(\w+).+3:\w+',lines[i])
                boot        = parser.strsearch('^\w+.+3:(\w+)',lines[i])
                ret         = parser.getretval('service %s status ' % name)
                if ret == 0: 
                    status = 'running'
                else:
                    status = 'stopped'
                    
                svcs[i] = [name,boot,status]
                i += 1
 
        if parser.checkexec('insserv'):
            lines       = parser.readstdout("runlevel")
            runlevel    = parser.strsearch('\w+ (.+)',lines[0])
                
            self.syslog.debug("System %s has insserv command" % self.system)
            lines   = parser.readstdout("insserv --showall")
            j = 0
            for i in range(len(lines)):
                runlevels   = parser.strsearch('[SK]:\d+:(.+):.+',lines[i])
                if runlevel in runlevels.split(' '): 
                    name        = parser.strsearch('[SK]:.+:.+:(.+)',lines[i])
                
                    ret         = parser.getretval('service %s status ' % name)
                    if ret == 0: 
                        status = 'running'
                    else:
                        status = 'stopped'
                    
                    boot        = parser.strsearch('([SK]):.+:.+:.+',lines[i])
                    if boot == 'K':
                        boot = 'disabled'
                    if boot == 'S':
                        boot = 'enabled'

                    svcs[j] = [name,boot,status]
                    j += 1
                i += 1
               

        return svcs


    # Get updates
    def getupdates(self):
        self.syslog.debug("Get update list")
        parser = TeddixParser.TeddixStringParser() 
        
        updates = { }
        if parser.checkexec('apt-get'):
            ret     = parser.getretval('apt-get update -qq')
            lines   = parser.readstdout("aptitude -F'[%p][%V]' --disable-columns search '~U'")
            for i in range(len(lines)):
                utype = ''
                pkg   = parser.strsearch('\[(.+)\]\[.+\]',lines[i])
                nver  = parser.strsearch('\[.+\]\[(.+)\]',lines[i])
                updates[i] = [utype,pkg,nver]
                i += 1

        elif parser.checkexec('yum'):
            lines   = parser.readstdout("yum updateinfo list -q")
            for i in range(len(lines)):
                utype  = parser.strsearch('[\-\w]+\W+(\w+)\W+.+',lines[i])
                pkg    = parser.strsearch('[\-\w]+\W+\w+\W+(.+)',lines[i])
                nver   = pkg 
                updates[i] = [utype,pkg,nver]
                i += 1
      
        return updates


