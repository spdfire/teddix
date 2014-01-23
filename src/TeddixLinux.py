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


class TeddixLinux:

    def __init__(self,syslog):
        self.syslog = syslog
        
        self.system = platform.system()
        self.arch = platform.architecture()
        self.machine = platform.machine()
        self.dist = platform.linux_distribution()

        self.syslog.info("Detected: %s (%s %s) arch: %s" % (self.system,self.dist[0],self.dist[1],self.machine))

    # Get installed packages
    def getpkgs(self):

        t_rpm = "test -x /bin/rpm"
        t_dpkg = "test -x /usr/bin/dpkg-query"
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        if subprocess.call(t_rpm,shell=True) == 0:
            self.syslog.debug("Distro %s is RPM based " % self.dist[0])
            cmd = "/bin/rpm -qa --queryformat '%{NAME}:%{VERSION}-%{RELEASE}\n'"
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = sorted(proc.stdout.read().split('\n'))

            i = 0
            packages = { }
            for line in lines:
                columns = line.split(":")
                if columns[0]: 
                    packages[i] = columns
                    i += 1

        elif subprocess.call(t_dpkg,shell=True) == 0:
            self.syslog.debug("Distro %s is DEB based " % self.dist[0])
            cmd = "/usr/bin/dpkg-query --show --showformat='[${Package}][${Version}][unknown][${Installed-Size}][${Section}][${Status}][${binary:Summary}][${Homepage}][unknown][unknown][${Architecture}]\n'"
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = sorted(proc.stdout.read().split('\n'))

            i = 0
            packages = { }
            for line in lines:
                match = re.search(r'\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]',line)
                if match:
                    packages[i] = [match.group(1),match.group(2),match.group(3),match.group(4),match.group(5),match.group(6),match.group(7),match.group(8),match.group(9),match.group(10),match.group(11)]
                    i += 1

        else:
            self.syslog.warn("Unknown pkg system for %s " % self.dist[0])
            packages = { }

        return packages

    # Get partitions
    def getpartitions(self):
        self.syslog.debug("Getting filesystem list ")

        df_cmd = "df -hP"
        df_proc = subprocess.Popen(df_cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        df_lines = df_proc.stdout.read().split('\n')
        mount_cmd = "mount"
        mount_proc = subprocess.Popen(mount_cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        mount_lines = mount_proc.stdout.read().split('\n')

        disks = { }
        fs = { }
        i = 0
        for df_line in df_lines:
            if df_line.find ("/dev/") != -1 and not df_line.find ("tmpfs") != -1:
                columns = re.findall(r'([^ ]+)',df_line)
                fsname = columns[5]
                fsdev = columns[0]
                fssize = columns[1]
                fsused = columns[2]
                fsfree = columns[3]
                # get fstype for device
                for mount_line in mount_lines:
                    if mount_line.find (fsname + ' ') != -1:
                        columns2 = re.findall(r'([^ ]+) ',mount_line)
                        fstype = columns2[4]
                        disks[i] = [fsname,fsdev,fssize,fsused,fsfree,fstype]
                i += 1

        return disks

    # Get swap 
    def getswap(self):
        self.syslog.debug("Reading swap filesystems")

        fd = open('/proc/swaps')
        f = fd.read()
        lines = f.split('\n')
            
        swaps = []
        for line in lines:
            dev = re.findall(r'^([^ ]+)[ ]+\w+\W+\d+',line)
            typ = re.findall(r'^[^ ]+[ ]+(\w+)\W+\d+',line)
            free = re.findall(r'^[^ ]+[ ]+\w+\W+(\d+)',line)
            if dev:
                swaps.append(dev[0] + ' ' + typ[0] + ' ' + free[0])


        fd.close()
        return swaps


    # Get network interfaces
    def getnics(self):
        self.syslog.debug("Looking for available network interfaces ")

        cmd = "ifconfig -a"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ifaces = proc.stdout.read().split('\n\n')

        lines = { }
        nics = []
        i = 0
        for iface in ifaces:
            lines = iface.split('\n')
            j = 0
            k = 0
            for line in lines:
                ifname = re.findall(r'^([\w\-]+)[: ]+',line)
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
            mac = re.findall(r'.+ ether|HWaddr ([\w\d:]+) .+',line)
            if mac: 
                return mac[0]

        return ''

    # Get ipv address  
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
            if not ipv4:
                ipv4 = re.findall(r'inet addr:(\d+.\d+.\d+.\d+)',line)
            
            if not mask:
                mask = re.findall(r'netmask (\d+.\d+.\d+.\d+)',line)
            if not mask:
                mask = re.findall(r'Mask:(\d+.\d+.\d+.\d+)',line) 
        
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
            if not ipv6:
                ipv6 = re.findall(r'inet6 addr: ([\w:]+)/\d+',line)
            
            if not mask6:
                mask6 = re.findall(r'inet6 [\w:]+/(\d+)',line)
            if not mask6:
                mask6 = re.findall(r'inet6 addr: [\w:]+/(\d+)',line)
        
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

        cmd = "route -n -A inet"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        routes = []
        for line in lines:
            data = line.split(' ')
            match = re.findall(r'(\d+.\d+.\d+.\d+)[ ]+(\d+.\d+.\d+.\d+)[ ]+(\d+.\d+.\d+.\d+)[ ]+(\w+)[ ]+(\d+)[ ]+\w+[ ]+\w+[ ]+([\w\-\.\:]+)',line)
            for element in match:
                routes.append(element[0]+'/'+element[1]+'/'+element[2]+'/'+element[3]+'/'+element[4]+'/'+element[5])

        return routes

    # Get routes 
    def getroutes6(self):
        self.syslog.debug("Reading routing tables for ipv6 ")

        cmd = "route -n -A inet6"
        proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        lines = proc.stdout.read().split('\n')

        routes6 = []
        for line in lines:
            data = line.split(' ')
            match = re.findall(r'([\w:]+)/(\d+)[ ]+([\w:]+)[ ]+(\w+)[ ]+(\d+)[ ]+\w+[ ]+\w+[ ]+([\w\-\.\:]+)',line)
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

        t_systemd = "test -x /bin/systemctl || test -x /usr/bin/systemctl || test -x /usr/local/bin/systemctl"
        t_chkconfig = "test -x /sbin/chkconfig"
        t_insserv = "test -x /sbin/insserv"
        svcs = [ ]  
        if subprocess.call(t_systemd,shell=True) == 0:
            self.syslog.debug("System %s has systemctl command" % self.dist[0])
            cmd = "systemctl list-unit-files "
            state = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = state.stdout.read().split('\n')
            for line in lines:
                service = re.findall(r'(.+).service\W*(\w+)\W*',line)
                if service:
                    svcs.append(service[0][0] + '/' + service[0][1]) 

        
        if subprocess.call(t_chkconfig,shell=True) == 0:
            self.syslog.debug("System %s has chkconfig command" % self.dist[0])
            cmd = "chkconfig --list"
            state = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = state.stdout.read().split('\n')
            for line in lines:
                service = re.findall(r'(.+)[ ]+(.+)',line)
                if service:
                    svcs.append(service[0][0] + '/' + service[0][1]) 

        
        if subprocess.call(t_insserv,shell=True) == 0:
            self.syslog.debug("System %s has insserv command" % self.dist[0])
            cmd = "insserv --showall"
            state = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = state.stdout.read().split('\n')
            for line in lines:
                service = re.findall(r'([SK]):\d+:\w+:(.+)',line)
                if service:
                    if service[0][0] == 'K':
                        svcs.append(service[0][1] + '/' + 'disabled') 
                    if service[0][0] == 'S':
                        svcs.append(service[0][1] + '/' + 'enabled') 


        #else:
        #   self.syslog.warn("Unable to get service configuration ")
        #   return ''

        return svcs


