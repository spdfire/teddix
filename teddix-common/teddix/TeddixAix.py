#!/usr/bin/env python

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


class TeddixAix:

    def __init__(self,syslog):
        self.syslog = syslog
        
        self.system     = platform.system()
        self.arch       = platform.architecture()
        self.machine    = platform.machine()
        self.name       = 'IBM AIX'
        self.ver        = parser.readstdout('oslevel')
        self.detail     = self.name + self.ver 
        self.kernel     = platform.release()
        self.manufacturer= 'IBM'
        self.serial     = ''

        self.syslog.info("Detected: %s (%s) arch: %s" % (self.system,self.kernel,self.machine))


    # Get PCI devices 
    def getpci(self):
        self.syslog.debug("Detecting PCI devices " )
        parser = TeddixParser.TeddixStringParser() 

        lines       = parser.readstdout('lsdev -p pci0')
        pcidev = {}
        for i in range(len(lines)):
            if parser.strsearch('^([^ ]+)[ ]+\w+[ ]+[^ ]+[ ]+.+',lines[i]):
                path    = parser.strsearch('^[^ ]+[ ]+\w+[ ]+([^ ]+)[ ]+.+',lines[i])
                devtype = parser.strsearch('^[^ ]+[ ]+\w+[ ]+[^ ]+[ ]+(.+)',lines[i]) 
                vendor  = ''
                model   = ''
                revision= ''

                pcidev[i]   = [path,devtype,vendor,model,revision] 

        return pcidev


    # Get Block devices 
    def getblock(self):
        self.syslog.debug("Detecting block devices " )
        parser = TeddixParser.TeddixStringParser() 
    
        lines       = parser.readstdout('lsdev -Ccdisk')
        blockdev = {}
        for i in range(len(lines)):
            if parser.strsearch('^([^ ]+)[ ]+\w+[ ]+.+',lines[i]):
                name        = parser.strsearch('^([^ ]+)[ ]+\w+[ ]+.+',lines[i])
                devtype     = parser.strsearch('^[^ ]+[ ]+\w+[ ]+(.+)',lines[i])
                vendor      = ''
                model       = ''
                nr_sectors  = '' 
                sect_size   = ''
                rotational  = ''
                readonly    = ''
                removable   = ''
                major       = ''
                minor       = ''

                blockdev[i] = [name,devtype,vendor,model,nr_sectors,sect_size,rotational,readonly,removable,major,minor]

        return blockdev



    # Get installed packages
    def getpkgs(self):
        self.syslog.debug("Getting package list " )
        parser = TeddixParser.TeddixStringParser()
        #lslpp -Lc
        #Package Name:Fileset:Level:State:PTF Id:Fix State:Type:Description:Destination Dir.:Uninstaller:Message Catalog:Message Set:Message Number:Parent:Automatic:EFIX Locked:Install Path:Build Date
        #sudo:sudo-1.6.7p5-2:1.6.7p5-2: : :C:R:Allows restricted root access for specified users.: :/bin/rpm -e sudo: : : : :0: :/opt/freeware:Tue Apr 27 18:35:51 WET 2004
        packages = { }
        lines       = parser.readstdout('lslpp -Lc')
        for i in range(len(lines)):
             name        = parser.strsearch('(.+):.+:.+:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*',lines[i])
             ver         = parser.strsearch('.+:.+:(.+):.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*:.*',lines[i])
             pkgsize     = '' 
             instalsize  = ''
             section     = ''
             status      = ''
             info        = parser.strsearch('.+:.+:.+:.*:.*:.*:.*:(.*):.*:.*:.*:.*:.*:.*:.*:.*:.*:.*',lines[i])
             homepage    = ''
             signed      = ''
             files       = ''
             arch        = ''
             publisher   = ''
             release     = ''
           
             packages[i] = [name,ver,pkgsize,instalsize,section,status,info,homepage,signed,files,arch] 

        return packages

    # Get updates
    def getupdates(self):
        self.syslog.debug("Listing available updates")
        parser = TeddixParser.TeddixStringParser() 
        
        # suma -x -a Action=Preview
        updates = { }
        return updates


    # Get partitions
    def getpartitions(self):
        self.syslog.debug("Getting filesystem list ")
        parser = TeddixParser.TeddixStringParser()
        
        # no support from psutil 
        disks = { }
        output  = parser.readstdout('df')
        lines   = parser.arrayfilter('^([^ ]+)[ ]+[\d\-]+[ ]+[\d\-]+[ ]+[\d\%\-]+[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+.+',output)
        for i in range(len(lines)):
            fstotal = parser.strsearch('^[^ ]+[ ]+([\d\-]+)[ ]+[\d\-]+[ ]+[\d\%\-]+[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+.+',lines[i]) 
            fsfree  = parser.strsearch('^[^ ]+[ ]+[\d\-]+[ ]+([\d\-]+)[ ]+[\d\%\-]+[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+.+',lines[i])
            fsused  = unicode(parser.str2int(fstotal) - parser.str2int(fsfree))
            fspercent = parser.strsearch('^[^ ]+[ ]+[\d\-]+[ ]+[\d\-]+[ ]+([\d\%\-]+)[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+.+',lines[i])
    
            fsdev = parser.strsearch('^([^ ]+)[ ]+[\d\-]+[ ]+[\d\-]+[ ]+[\d\%\-]+[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+.+',lines[i])
            fsmount = parser.strsearch('^[^ ]+[ ]+[\d\-]+[ ]+[\d\-]+[ ]+[\d\%\-]+[ ]+[\d\-]+[ ]+[\d\-\%]+[ ]+(.+)',lines[i])
            fstype = ''
            fsopts = ''

            disks[i] = [fsdev,fsmount,fstype,fsopts,fstotal,fsused,fsfree,fspercent]

        return disks


    # Get swap 
    def getswap(self):
        self.syslog.debug("Reading swap filesystems")
        parser = TeddixParser.TeddixStringParser()
        
        output  = parser.readstdout('lsps -ac')
        lines   = parser.arrayfilter('.*:(.*):.*:.*:.*:.*:.*:.*',output)

        swaps = { }
        for i in range(len(lines)):
            dev         = parser.strsearch('.*:(.*):.*:.*:.*:.*:.*:.*',lines[i])
            swaptype    = parser.strsearch('.*:.*:.*:.*:.*:.*:.*:(.*)',lines[i])
            total       = parser.strsearch('.*:.*:.*:(.*):.*:.*:.*:.*',lines[i])
            used        = ''
            free        = ''
                  
            swaps[i] = [dev,swaptype,total,used,free] 
                  
        return swaps


    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")
        parser = TeddixParser.TeddixStringParser()
        lines  = parser.readstdout('lsdev -Cc if')
        
        nics = {}
        for i in range(len(lines)):
            name        = parser.strsearch('^([^ ]+)[ ]+\w+[ ]+[^ ]+',lines[i])

            lines2      = parser.readstdout("entstat -d " + name)
            macaddr     = parser.arraysearch('Hardware Address: ([\w:.-]+)',lines2)
            description = parser.strsearch('^[^ ]+[ ]+\w+[ ]+([^ ]+)',lines[i])
            status      = parser.strsearch('^[^ ]+[ ]+(\w+)[ ]+[^ ]+',lines[i])

            # TODO: 
            rx_packets  = ''
            rx_bytes    = ''
            tx_packets  = ''
            tx_bytes    = ''
            
            driver      = '' 
            kernmodule  = ''
            drvver      = ''
            nictype     = ''
            driver      = ''
            firmware    = ''

            nics[i] = [name,description,nictype,status,rx_packets,tx_packets,rx_bytes,tx_bytes,driver,drvver,firmware,kernmodule,macaddr]
        
        return nics



    # Get ipv4 address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser()
        
        lines  = parser.readstdout("lsattr -El " + nic)
        ipv4    = parser.arraysearch('netaddr[ ]+(\d+\.\d+\.\d+\.\d+)[ ]+',lines[i])
        mask    = parser.arraysearch('netmask[ ]+(\d+\.\d+\.\d+\.\d+)[ ]+',lines[i])
        bcast   = ''
        ips = { }
        ips[0] = [ipv4,mask,bcast]
      
        return ips



    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 
        
        lines  = parser.readstdout("lsattr -El " + nic)
        ipv4    = parser.arraysearch('netaddr6[ ]+(\d+\.\d+\.\d+\.\d+)[ ]+',lines[i])
        mask    = parser.arraysearch('prefixlen[ ]+(\d+\.\d+\.\d+\.\d+)[ ]+',lines[i])
        bcast   = ''
        ips6 = { }
        ips6[0] = [ipv4,mask,bcast]
      
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
        
        output  = parser.readstdout("netstat -rn -f inet")
        lines   = parser.arrayfilter('^(.+)[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',output)
     
        routes = { }
        for i in range(len(lines)):
            destination = parser.strsearch('^(.+)[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            mask        = ''
            gateway     = parser.strsearch('^.+[ ]+([\d\.])+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            interface   = parser.strsearch('^.+[ ]+[\d\.]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+([^ ]+)[ ]+',lines[i])
            flags       = parser.strsearch('^.+[ ]+[\d\.]+[ ]+(\w+)[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            metric      = ''
            routes[i] = [destination,gateway,mask,flags,metric,interface] 
            i += 1

        return routes


    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")
        parser = TeddixParser.TeddixStringParser() 
        output  = parser.readstdout("netstat -rn -f inet6")
        lines   = parser.arrayfilter('^([:a-zA-Z\d]+)[ ]+[:a-zA-Z\d]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',output)
     
        routes6 = { }
        for i in range(len(lines)):
            destination = parser.strsearch('^([:a-zA-Z\d]+)[ ]+[:a-zA-Z\d]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            mask        = ''
            gateway     = parser.strsearch('^[:a-zA-Z\d]+[ ]+([:a-zA-Z\d]+)[ ]+\w+[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            interface   = parser.strsearch('^[:a-zA-Z\d]+[ ]+[:a-zA-Z\d]+[ ]+\w+[ ]+\d+[ ]+\d+[ ]+([^ ]+)[ ]+',lines[i])
            flags       = parser.strsearch('^[:a-zA-Z\d]+[ ]+[:a-zA-Z\d]+[ ]+(\w+)[ ]+\d+[ ]+\d+[ ]+[^ ]+[ ]+',lines[i])
            metric      = ''
            routes6[i] = [destination,gateway,mask,flags,metric,interface] 

        return routes6

   
    # Get groups 
    def getgroups(self):
        self.syslog.debug("Reading system groups")
        parser = TeddixParser.TeddixStringParser()
        return {} 

    # Get users 
    def getusers(self):
        self.syslog.debug("Reading system users")
        parser = TeddixParser.TeddixStringParser() 
        return {} 

    # Get procs 
    def getprocs(self):
        self.syslog.debug("Listing system procs")
        parser = TeddixParser.TeddixStringParser() 
        return {} 

    # Get services
    def getsvcs(self):
        self.syslog.debug("Getting system services")
        parser = TeddixParser.TeddixStringParser() 
        return {} 



