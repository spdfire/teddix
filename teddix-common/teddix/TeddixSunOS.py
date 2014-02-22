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

    # Get Block devices 
    def getblock(self):
        self.syslog.debug("Detecting block devices " )
        parser = TeddixParser.TeddixStringParser() 

    # Get installed packages
    def getpkgs(self):
        self.syslog.debug("Getting package list " )
        parser = TeddixParser.TeddixStringParser() 
        
        packages = { }
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        if parser.checkexec('pkg'):
            self.syslog.debug("Distro %s is IPS based " % self.dist[0])
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

    # Get swap 
    def getswap(self):
        self.syslog.debug("Reading swap filesystems")
        parser = TeddixParser.TeddixStringParser() 
    
    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")
        parser = TeddixParser.TeddixStringParser() 

    # Get ipv4 address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

    # Get dnsservers 
    def getdns(self):
        self.syslog.debug("Reading DNS configuration")
        parser = TeddixParser.TeddixStringParser() 

    # Get routes 
    def getroutes(self):
        self.syslog.debug("Reading routing table for ipv4 ")
        parser = TeddixParser.TeddixStringParser() 

    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")
        parser = TeddixParser.TeddixStringParser() 

    # Get groups 
    def getgroups(self):
        self.syslog.debug("Reading system groups")
        parser = TeddixParser.TeddixStringParser() 

    # Get users 
    def getusers(self):
        self.syslog.debug("Reading system users")
        parser = TeddixParser.TeddixStringParser() 

    # Get procs 
    def getprocs(self):
        self.syslog.debug("Listing system procs")
        parser = TeddixParser.TeddixStringParser() 

    # Get services
    def getsvcs(self):
        self.syslog.debug("Getting system services")
        parser = TeddixParser.TeddixStringParser() 

    # Get updates
    def getupdates(self):
        self.syslog.debug("Listing available updates")
        parser = TeddixParser.TeddixStringParser() 


