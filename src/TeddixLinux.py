#!/usr/bin/env python
#

import os
import re
import sys
import time
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
        
        self.system = platform.system()
        self.arch = platform.architecture()
        self.machine = platform.machine()
        self.dist = platform.linux_distribution()

        self.syslog.info("Detected: %s (%s %s) arch: %s" % (self.system,self.dist[0],self.dist[1],self.machine))

    # Get installed packages
    def getpkgs(self):
        parser = TeddixParser.TeddixStringParser() 

        # generate pkglist
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        t_rpm = "test -x /bin/rpm"
        t_dpkg = "test -x /usr/bin/dpkg-query"
        lines = None
        if subprocess.call(t_rpm,shell=True) == 0:
            self.syslog.debug("Distro %s is RPM based " % self.dist[0])
            #cmd = "/bin/rpm -qa --queryformat '%{NAME}:%{VERSION}-%{RELEASE}\n'"
            cmd = "/bin/rpm -qa --queryformat '\[%{NAME}\]\[%{VERSION}-%{RELEASE}\]\[%{ARCHIVESIZE}\]\[%{SIZE}\]\[%{GROUP}\]\[installed\]\[%{SUMMARY}\]\[%{URL}\]\[\]\[\]\[%{ARCH}\]\n'"
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = sorted(proc.stdout.read().split('\n'))

        elif subprocess.call(t_dpkg,shell=True) == 0:
            self.syslog.debug("Distro %s is DEB based " % self.dist[0])
            cmd = "/usr/bin/dpkg-query --show --showformat='[${Package}][${Version}][][${Installed-Size}][${Section}][${Status}][${binary:Summary}][${Homepage}][][][${Architecture}]\n'"
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = sorted(proc.stdout.read().split('\n'))

        else:
            self.syslog.warn("Unknown pkg system for %s " % self.dist[0])

        # parse pkglist
        packages = { }
        if lines: 
            i = 0
            for line in lines:
                match = re.search(r'\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]\[(.*)\]',line)
                if match:
                    val = { }
                    if not parser.isstr(match.group(1)):
                        val[0] = 'N/A'
                    else:
                        val[0] = parser.str2uni(match.group(1))
                    
                    if not parser.isstr(match.group(2)):
                        val[1] = 'N/A'
                    else:
                        val[1] = parser.str2uni(match.group(2))
                    
                    if not parser.isstr(match.group(3)):
                        val[2] = 'N/A'
                    else:
                        val[2] = parser.str2uni(match.group(3))
                    
                    if not parser.isstr(match.group(4)):
                        val[3] = 'N/A'
                    else:
                        val[3] = parser.str2uni(match.group(4))
                    
                    if not parser.isstr(match.group(5)):
                        val[4] = 'N/A'
                    else:
                        val[4] = parser.str2uni(match.group(5))
                    
                    if not parser.isstr(match.group(6)):
                        val[5] = 'N/A'
                    else:
                        tmp = match.group(6).split(' ')
                        if tmp[2]:
                            val[5] = parser.str2uni(tmp[2])
                        else:
                            val[5] = 'N/A'
                    
                    if not parser.isstr(match.group(7)):
                        val[6] = 'N/A'
                    else:
                        val[6] = parser.str2uni(match.group(7))
                    
                    if not parser.isstr(match.group(8)):
                        val[7] = 'N/A'
                    else:
                        val[7] = parser.str2uni(match.group(8))
                    
                    if not parser.isstr(match.group(9)):
                        val[8] = 'N/A'
                    else:
                        val[8] = parser.str2uni(match.group(9))
                    
                    if not parser.isstr(match.group(10)):
                        val[9] = 'N/A'
                    else:
                        val[9] = parser.str2uni(match.group(10))
                    
                    if not parser.isstr(match.group(11)):
                        val[10] = 'N/A'
                    else:
                        val[10] = parser.str2uni(match.group(11))
                        
                    packages[i] = [val[0],val[1],val[2],val[3],val[4],val[5],val[6],val[7],val[8],val[9],val[10]]
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

                if not parser.isstr(usage.total):
                    fstotal = 'N/A'
                else:
                    fstotal = parser.str2uni(usage.total)

                if not parser.isstr(usage.used):
                    fsused = 'N/A'
                else:
                    fsused = parser.str2uni(usage.used)

                if not parser.isstr(usage.free):
                    fsfree = 'N/A'
                else:
                    fsfree = parser.str2uni(usage.free)

                if not parser.isstr(usage.percent):
                    fspercent = 'N/A'
                else:
                    fspercent = parser.str2uni(usage.percent)

    
            if not parser.isstr(part.device):
                fsdev = 'N/A'
            else:
                fsdev = parser.str2uni(part.device)
            
            if not parser.isstr(part.mountpoint):
                fsmount = 'N/A'
            else:
                fsmount = parser.str2uni(part.mountpoint)

            if not parser.isstr(part.fstype):
                fstype = 'N/A'
            else:
                fstype = parser.str2uni(part.fstype)

            if not parser.isstr(part.opts):
                fsopts = 'N/A'
            else:
                fsopts = parser.str2uni(part.opts)

            disks[i] = [fsdev,fsmount,fstype,fsopts,fstotal,fsused,fsfree,fspercent]
            i += 1

        return disks


    # Get swap 
    def getswap(self):
        self.syslog.debug("Reading swap filesystems")
        parser = TeddixParser.TeddixStringParser() 

        fd = open('/proc/swaps')
        f = fd.read()
        lines = f.split('\n')
            
        i = 0 
        swaps = { }
        for line in lines:
                match = re.search(r'^([^ ]+)[ ]+(\w+)\W+(\d+)\W+(\d+)',line)
                if match:
                    val = { }
                    if not parser.isstr(match.group(1)):
                        dev = 'N/A'
                    else:
                        dev = parser.str2uni(match.group(1))
                    if not parser.isstr(match.group(2)):
                        swaptype = 'N/A'
                    else:
                        swaptype = parser.str2uni(match.group(2))
                    if not parser.isstr(match.group(3)):
                        total = 'N/A'
                    else:
                        total = parser.str2uni(match.group(3))
                    if not parser.isstr(match.group(4)):
                        used = 'N/A'
                    else:
                        used = parser.str2uni(match.group(4))
                    if not (parser.isint(match.group(3)) or parser.isint(match.group(4))): 
                        free = 'N/A'
                    else:
                        free = parser.str2int(match.group(3)) - parser.str2int(match.group(4))
                        free = str(free)
                  
                    swaps[i] = [dev,swaptype,total,used,free]
                    i += 1
                  
        fd.close()

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

            driver = 'N/A' 
            drvver = 'N/A' 
            kernmodule = 'N/A' 
            firmware = 'N/A'
            description = 'N/A'
            nictype = 'N/A'
            status = 'N/A'
            rx_packets = 'N/A'
            rx_bytes = 'N/A'
            tx_packets = 'N/A'
            tx_bytes = 'N/A'
            macaddr = 'N/A'

            t_ethtool = "test -x /sbin/ethtool"
            lines = None
            if subprocess.call(t_ethtool,shell=True) == 0:
                
                # driver
                cmd = "/sbin/ethtool -i %s " % name 
                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                lines = proc.stdout.read().split('\n')
                for line in lines:
                    match = re.search(r'^driver: (\w+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            driver = 'N/A'
                        else:
                            driver = parser.str2uni(match.group(1))
                            kernmodule = driver 

                for line in lines:
                    match = re.search(r'^firmware-version: (.+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            firmware = 'N/A'
                        else:
                            firmware = parser.str2uni(match.group(1))

                # MAC address 
                cmd = "/sbin/ethtool -P %s " % name 
                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                lines = proc.stdout.read().split('\n')
                for line in lines:
                    match = re.search(r'^Permanent address: ([\w:.-]+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            macaddr = 'N/A'
                        else:
                            macaddr = parser.str2uni(match.group(1))


                # statistics
                cmd = "/sbin/ethtool -S %s " % name 
                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                lines = proc.stdout.read().split('\n')
                for line in lines:
                    match = re.search(r'rx_packets: (\d+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            rx_packets = 'N/A'
                        else:
                            rx_packets = parser.str2uni(match.group(1))

                for line in lines:
                    match = re.search(r'rx_bytes: (\d+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            rx_bytes = 'N/A'
                        else:
                            rx_bytes = parser.str2uni(match.group(1))

                for line in lines:
                    match = re.search(r'tx_packets: (\d+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            tx_packets = 'N/A'
                        else:
                            tx_packets = parser.str2uni(match.group(1))

                for line in lines:
                    match = re.search(r'tx_bytes: (\d+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            tx_bytes = 'N/A'
                        else:
                            tx_bytes = parser.str2uni(match.group(1))


            t_modinfo = "test -x /sbin/modinfo"
            lines = None
            if subprocess.call(t_ethtool,shell=True) == 0:
 
                # driverinfo
                cmd = "/sbin/modinfo %s " % driver
                proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                lines = proc.stdout.read().split('\n')
                for line in lines:
                    match = re.search(r'^description:\W+(.+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            description = 'N/A'
                        else:
                            description = parser.str2uni(match.group(1))
                for line in lines:
                    match = re.search(r'^version:\W*(.+)',line)
                    if match:
                        if not parser.isstr(match.group(1)):
                            drvver = 'N/A'
                        else:
                            drvver = parser.str2uni(match.group(1))

            nics[i] = [name,description,nictype,status,rx_packets,tx_packets,rx_bytes,tx_bytes,driver,drvver,firmware,kernmodule,macaddr]
            i += 1
        
        return nics
            
    # Get ipv address  
    def getip(self,nic):
        self.syslog.debug("Reading %s IPv4 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

        t_ip = "test -x /bin/ip"
        t_ifconfig = "test -x /sbin/ifconfig"
        lines = None
        ips = {}
        i = 0
        if subprocess.call(t_ifconfig,shell=True) == 0:
            cmd = "/bin/ip addr list dev %s " % nic
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = proc.stdout.read().split('\n')
            
            for line in lines:
                match = re.search(r'inet[ \t]+(\d+\.\d+\.\d+\.\d+)/(\d+)\W+(brd\W+(\d+\.\d+\.\d+\.\d+)|)',line)
                if match:
                    if not parser.isstr(match.group(1)):
                        ipv4 = 'N/A'
                    else:
                        ipv4 = parser.str2uni(match.group(1))
                    if not parser.isstr(match.group(2)):
                        mask = 'N/A'
                    else:
                        mask = parser.str2uni(match.group(2))
                    if not parser.isstr(match.group(4)):
                        bcast = 'N/A'
                    else:
                        bcast = parser.str2uni(match.group(4)) 
                    
                    ips[i] = [ipv4,mask,bcast]
                    i += 1

        # use only if 'ip' is missing
        # TODO: handle multiple addresses 'wlan:6' 
        elif subprocess.call(t_ifconfig,shell=True) == 0:
            cmd = "/sbin/ifconfig %s " % nic
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = proc.stdout.read().split('\n')
            
            for line in lines:
                match = re.search(r'(inet |inet addr:)(\d+\.\d+\.\d+\.\d+)\W+Bcast:(\d+\.\d+\.\d+\.\d+)\W+(netmask |Mask:)(\d+\.\d+\.\d+\.\d+)',line)
                if match:
                    if not parser.isstr(match.group(2)):
                        ipv4 = 'N/A'
                    else:
                        ipv4 = parser.str2uni(match.group(2))
                    if not parser.isstr(match.group(5)):
                        mask = 'N/A'
                    else:
                        mask = parser.str2uni(match.group(5))
                    if not parser.isstr(match.group(3)):
                        bcast = 'N/A'
                    else:
                        bcast = parser.str2uni(match.group(3)) 
                    
                    ips[i] = [ipv4,mask,bcast]
                    i += 1

        return ips


    # Get ipv6 address  
    def getip6(self,nic):
        self.syslog.debug("Reading %s IPv6 configuraion" % nic)
        parser = TeddixParser.TeddixStringParser() 

        t_ip = "test -x /bin/ip"
        t_ifconfig = "test -x /sbin/ifconfig"
        lines = None
        ips6 = {}
        i = 0
        if subprocess.call(t_ifconfig,shell=True) == 0:
            cmd = "/bin/ip addr list dev %s " % nic
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = proc.stdout.read().split('\n')
            
            for line in lines:
                match = re.search(r'inet6[ \t]+([a-fA-F\d\:]+)/(\d+)\W+',line)
                if match:
                    if not parser.isstr(match.group(1)):
                        ipv6 = 'N/A'
                    else:
                        ipv6 = parser.str2uni(match.group(1))
                    if not parser.isstr(match.group(2)):
                        mask = 'N/A'
                    else:
                        mask = parser.str2uni(match.group(2))
                    
                    bcast = 'N/A'
                    ips6[i] = [ipv6,mask,bcast]
                    i += 1

        # use only if 'ip' is missing
        # TODO: handle multiple addresses 'wlan:6' 
        elif subprocess.call(t_ifconfig,shell=True) == 0:
            cmd = "/sbin/ifconfig %s " % nic
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lines = proc.stdout.read().split('\n')
            
            for line in lines:
                match = re.search(r'(inet6 |inet6 addr:)([a-fA-F\d\:]+)/(\d+)\W+',line)
                if match:
                    if not parser.isstr(match.group(2)):
                        ipv6 = 'N/A'
                    else:
                        ipv6 = parser.str2uni(match.group(2))
                    if not parser.isstr(match.group(3)):
                        mask = 'N/A'
                    else:
                        mask = parser.str2uni(match.group(3))
                    
                    bcast = 'N/A'
                    ips6[i] = [ipv6,mask,bcast]
                    i += 1

        return ips6


    # Get dnsservers 
    def getdns(self):
        self.syslog.debug("Reading DNS configuration")
        parser = TeddixParser.TeddixStringParser() 

        dns = {}
        fd = open('/etc/resolv.conf')
        f = fd.read()
        lines = f.split('\n')
       
        i = 0 
        for line in lines:
            match = re.search(r'^(nameserver|domain|search)[ \t]+(.+)',line)
            if match:
                if parser.isstr(match.group(2)):
                        dns[i] = [match.group(1),match.group(2)]
                        i += 1

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
        parser = TeddixParser.TeddixStringParser() 

        #pids = psutil.get_pid_list()
        #for pid in pids:
        #    p = psutil.Process(pid)
        
        procs = {}
        i = 0
        for p in psutil.process_iter():
               
            if not parser.isstr(p.pid):
                ppid = 'N/A'
            else:
                ppid = parser.str2uni(p.pid)

            if not parser.isstr(p.username):
                powner = 'N/A'
            else:
                powner = parser.str2uni(p.username)
            
            pcputime = p.get_cpu_times()
            if not parser.isstr(pcputime.system):
                psystime = 'N/A'
            else:
                psystime = parser.str2uni(pcputime.system)
            if not parser.isstr(pcputime.user):
                pusertime = 'N/A'
            else:
                pusertime = parser.str2uni(pcputime.user)

            # TODO: it takes too much time
            #pcpu = p.get_cpu_percent(interval=0.1)
            pcpu = 'N/A'
            pmem = p.get_memory_percent()
            if not parser.isstr(pmem):
                pmem = 'N/A'
            else:
                pmem = parser.str2uni(pmem)

            ppriority = parser.str2uni(p.get_nice())
            pstatus = parser.str2uni(p.status)
            if not parser.isstr(p.username):
                powner = 'N/A'
            else:
                powner = parser.str2uni(p.username)

            if not parser.isstr(p.name):
                pname = 'N/A'
            else:
                pname = parser.str2uni(p.name)

            pcmd = ''
            for pp in p.cmdline:
                pp += ' '
                pcmd += pp 
            
            if not parser.isstr(pcmd):
                pcmd = 'N/A'
            else:
                pcmd = parser.str2uni(pcmd)

            procs[i] = [ppid,powner,psystime,pusertime,pcpu,pmem,ppriority,pstatus,pname,pcmd]
            i += 1 

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


