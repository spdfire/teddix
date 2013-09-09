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


class TeddixSunOS:

    def __init__(self,syslog):
        self.syslog = syslog
        
        self.system = platform.system()
        self.arch = platform.architecture()
        self.machine = platform.machine()
        self.dist = platform.linux_distribution()

        self.syslog.info("Detected: %s (%s %s) arch: %s" % (self.system,self.dist[0],self.dist[1],self.machine))


    # Get installed packages
    def getpkgs(self):

        t_pkg = "test -x /usr/bin/pkg"
        t_pkgutil = "test -x /opt/csw/bin/pkgutil"
        if subprocess.call(t_rpm,shell=True) == 0:
            self.syslog.debug("System %s is IPS based " % self.dist[0])
            cmd = "/usr/bin/pkg list "
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = sorted(proc.stdout.read().split('\n'))

            i = 0
            packages = { }
            for line in lines:
                # x11/server/xvnc               # 1.0.1-0.151                i--
                name = re.findall(r'^([^ ]+)[ ]+\w+[ ]+.+',line)
                ver = re.findall(r'^[^ ]+[ ]+(\w+)[ ]+.+',line)
                stat = re.findall(r'^[^ ]+[ ]+\w+[ ]+(.+)',line)
                if name: 
                    packages[i] = (name,ver)
                    i += 1

        else:
            self.syslog.warn("Unknown pkg system for %s " % self.system)
            packages = { }

        return packages


    # Get partitions
    def getpartitions(self):
        self.syslog.debug("Getting filesystem list ")
        return disks

    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")

        cmd = "ifconfig -a"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')
        
        nics = []
        for line in lines:
            ifname = re.findall(r'^([\w\-]+): .+',line)
            if ifname:
                nics.append(ifname[0])
            i += 1 

        return nics


    # Get mac address
    def getmac(self,nic):
        self.syslog.debug("Reading %s MAC address" % nic)

        cmd = "ifconfig " + nic
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        for line in lines:
            mac = re.findall(r'.+ ether ([\w\d:]+) .+',line)
            if mac: 
                return mac[0]

        return ''


    # Get ipv4 address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)

        cmd = "ifconfig " + nic 
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        ips = []
        ipv4 = []
        mask = []
        for line in lines:
            if not ipv4:
                ipv4 = re.findall(r'inet (\d+.\d+.\d+.\d+)',line)
            
            if not mask:
                mask = re.findall(r'netmask (\d+.\d+.\d+.\d+)',line)
        
        if not mask:
            mask = ['unknown']
        if not ipv4:
            ipv4 = ['unknown']
        ips.append(ipv4[0] + '/' + mask[0])

        return ips

    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)

        cmd = "ifconfig " + nic 
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        ips6 = []
        ipv6 = []
        mask6 = []
        for line in lines:
            if not ipv6:
                ipv6 = re.findall(r'inet6 ([\w:]+)/\d+',line)
            
            if not mask6:
                mask6 = re.findall(r'inet6 [\w:]+/(\d+)',line)
        
        if not mask6:
            mask6 = ['unknown']
        if not ipv6:
            ipv6 = ['unknown']
        ips6.append(ipv6[0] + '/' + mask6[0])

        return ips6


    # Get dnsservers 
    def getdns(self):
        self.syslog.debug("Reading DNS configuration")

        dns = []
        fd = open('/etc/resolv.conf')
        f = fd.read()
        lines = f.split('\n')
            
        for line in lines:
            data = line.split(' ')
            if data[0].lower() == 'nameserver':
                dns.append(data[0].lower() + '/' + data[1])
            if data[0].lower() == 'domain':
                dns.append(data[0].lower() + '/' + data[1])
            if data[0].lower() == 'search':
                dns.append(data[0].lower() + '/' + data[1])

        fd.close()
        return dns


    # Get routes 
    def getroutes(self):
        self.syslog.debug("Reading routing table for ipv4 ")

        cmd = "netstat -rn -f inet"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        routes = []
        for line in lines:
            data = line.split(' ')
            match = re.findall(r'^(\w+)[ ]+(\d+.\d+.\d+.\d+)[ ]+(\w+)[ ]+(\d+)[ ]+\d+[ ]+([\w\-\.\:]+)',line)
            for element in match:
                routes.append(element[0]+'/'+element[1]+'/unknown/'+element[2]+'/'+element[3]+'/'+element[4])

        return routes

    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")

        cmd = "netstat -rn -f inet6"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        routes6 = []
        for line in lines:
            data = line.split(' ')
            match = re.findall(r'([\w:]+)/(\d+)[ ]+([\w:]+)[ ]+(\w+)[ ]+(\d+)[ ]+\d+[ ]+\w+[ ]+([\w\-\.\:]+)',line)
            for element in match:
                routes6.append(element[0]+'/'+element[1]+'/'+element[2]+'/'+element[3]+'/'+element[4]+'/'+element[5])

        return routes6


    # Get groups 
    def getgroups(self):
        self.syslog.debug("Reading system groups")

        groups = []
        fd = open('/etc/group')
        f = fd.read()
        lines = f.split('\n')
            
        for line in lines:
            data = line.split(':')
            if data[0]:
                if data[3]: 
                    groups.append(data[0] + ':' + data[3])
                else:
                    groups.append(data[0] + ':')

        fd.close()
        return groups


    # Get users 
    def getusers(self):
        self.syslog.debug("Reading system users")

        users = []
        fd = open('/etc/passwd')
        f = fd.read()
        lines = f.split('\n')
            
        for line in lines:
            data = line.split(':')
            if data[0]:
                users.append(data[2] + ':' + data[0] + ':' + data[5] + ':' +data[6])

        fd.close()
        return users


    # Get procs 
    def getprocs(self):
        self.syslog.debug("Listing system procs")

        pids = psutil.get_pid_list()
        procs = []
            
        for pid in pids:
            p = psutil.Process(pid)
            if p.cmdline:
                pname = ''
                for pp in p.cmdline:
                    pp += ' '
                    pname += pp 

                procs.append(pname)

        return procs


    # Get services
    def getsvcs(self):
        self.syslog.debug("Getting system services")

        t_svcs = "test -x /usr/bin/svcs"
        if subprocess.call(t_systemd,shell=True) == 0:
            self.syslog.debug("System %s has svcs command" % self.dist[0])
            cmd = "/usr/bin/svcs"
            state = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = state.stdout.read().split('\n')
            svcs = [ ]  
            for line in lines:
                service = re.findall(r'^(.+)[ ]+\d+:\d+:\d+ \w+:(.+)',line)
                if service:
                    svcs.append(service[0][0] + '/' + service[0][1]) 

            return svcs
        
        else:
            self.syslog.warn("Unable to get service configuration ")
            return ''



