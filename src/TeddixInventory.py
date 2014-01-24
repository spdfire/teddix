#!/usr/bin/env python
#

import os
import re
import sys
import time
import psutil
import locale
import platform
import dmidecode
import subprocess
import xml.dom.minidom as minidom
import xml.etree.ElementTree as xml

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile
import TeddixParser

# OS dependend stuff
import TeddixLinux

class TeddixBaseline:
    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.cfg = cfg
        
        system = platform.system()
        
        self.syslog.info("Generating Baseline")

        if system == 'Linux':
            self.osbase = TeddixLinux.TeddixLinux(syslog)

        elif system == 'SunOS':
            print "TODO OS"
            self.osbase = TeddixSunOS.TeddixSunOS(syslog)

        elif system == 'HP-UX':
            print "TODO OS"
            self.osbase = TeddixHPUX.TeddixHPUX(syslog)

        elif system == 'AIX':
            print "TODO OS"
            self.osbase = TeddixAix.TeddixAix(syslog)

        elif system == 'NT':
            print "TODO OS"
            self.osbase = TeddixWindows.TeddixWindows(syslog)

        else:
            raise RuntimeError


    def _getdmi(self):
        from pprint import pprint
        DMI = { }


        # get BIOS Data
        #tmp = dmidecode.bios()
        #pprint(tmp)
        for v  in dmidecode.bios().values():
            if type(v) == dict and v['dmi_type'] == 0:
                DMI['bios',0,'BIOS Revision'] = str((v['data']['BIOS Revision']))
                DMI['bios',0,'ROM Size'] = str((v['data']['ROM Size']))
                DMI['bios',0,'Relase Date'] = str((v['data']['Relase Date']))
                DMI['bios',0,'Runtime Size'] = str((v['data']['Runtime Size']))
                DMI['bios',0,'Vendor'] = str((v['data']['Vendor']))
                DMI['bios',0,'Version'] = str((v['data']['Version']))

        # get System Data
        #tmp = dmidecode.system()
        #pprint(tmp)
        for v  in dmidecode.system().values():
            if type(v) == dict and v['dmi_type'] == 1:
                DMI['system',0,'Family'] = str((v['data']['Family']))
                DMI['system',0,'Manufacturer'] = str((v['data']['Manufacturer']))
                DMI['system',0,'Product Name'] = str((v['data']['Product Name']))
                DMI['system',0,'SKU Number'] = str((v['data']['SKU Number']))
                DMI['system',0,'Serial Number'] = str((v['data']['Serial Number']))
                DMI['system',0,'UUID'] = str((v['data']['UUID']))
                DMI['system',0,'Version'] = str((v['data']['Version']))
                DMI['system',0,'Wake-Up Type'] = str((v['data']['Wake-Up Type']))

        # get BaseBoard Data
        #tmp = dmidecode.baseboard()
        #pprint(tmp)

        # get chassis Data
        #tmp = dmidecode.chassis()
        #pprint(tmp)
        for v  in dmidecode.chassis().values():
            if type(v) == dict and v['dmi_type'] == 3:
                DMI['chassis',0,'Asset Tag'] = str((v['data']['Asset Tag']))
                DMI['chassis',0,'Boot-Up State'] = str((v['data']['Boot-Up State']))
                DMI['chassis',0,'Lock'] = str((v['data']['Lock']))
                DMI['chassis',0,'Manufacturer'] = str((v['data']['Manufacturer']))
                DMI['chassis',0,'Power Supply State'] = str((v['data']['Power Supply State']))
                DMI['chassis',0,'Security Status'] = str((v['data']['Security Status']))
                DMI['chassis',0,'Serial Number'] = str((v['data']['Serial Number']))
                DMI['chassis',0,'Thermal State'] = str((v['data']['Thermal State']))
                DMI['chassis',0,'Type'] = str((v['data']['Type']))
                DMI['chassis',0,'Version'] = str((v['data']['Version']))

        # get Processor Data
        #tmp = dmidecode.processor()
        #pprint(tmp)
        i = 0
        for v  in dmidecode.processor().values():
            if type(v) == dict and v['dmi_type'] == 4:
                DMI['processor',i,'Asset Tag'] = str((v['data']['Asset Tag']))
                DMI['processor',i,'Characteristics'] = str((v['data']['Characteristics']))
                DMI['processor',i,'Core Count'] = str((v['data']['Core Count']))
                DMI['processor',i,'Core Enabled'] = str((v['data']['Core Enabled']))
                DMI['processor',i,'Current Speed'] =str((v['data']['Current Speed']))
                DMI['processor',i,'External Clock'] = str((v['data']['External Clock']))
                DMI['processor',i,'Family'] = str((v['data']['Family']))
                DMI['processor',i,'L1 Cache Handle'] = str((v['data']['L1 Cache Handle']))
                DMI['processor',i,'L2 Cache Handle'] = str((v['data']['L2 Cache Handle']))
                DMI['processor',i,'L3 Cache Handle'] = str((v['data']['L3 Cache Handle']))
                DMI['processor',i,'Manufacturer'] = str((v['data']['Manufacturer']['Vendor']))
                DMI['processor',i,'Max Speed'] = str((v['data']['Max Speed']))
                DMI['processor',i,'Part Number'] = str((v['data']['Part Number']))
                DMI['processor',i,'Serial Number'] = str((v['data']['Serial Number']))
                DMI['processor',i,'Socket Designation'] = str((v['data']['Socket Designation']))
                DMI['processor',i,'Status'] = str((v['data']['Status']))
                DMI['processor',i,'Thread Count'] = str((v['data']['Thread Count']))
                DMI['processor',i,'Type'] = str((v['data']['Type']))
                DMI['processor',i,'Upgrade'] = str((v['data']['Upgrade']))
                DMI['processor',i,'Version'] = str((v['data']['Version']))
                DMI['processor',i,'Voltage'] = str((v['data']['Voltage']))
                i += 1


        # get Memory Data
        #tmp = dmidecode.memory()
        #pprint(tmp)
        i = 0
        for v  in dmidecode.memory().values():
            if type(v) == dict and v['dmi_type'] == 17 :
                if str((v['data']['Size'])) != 'None':
                    DMI['memory',i,'Data Width'] = str((v['data']['Data Width']))
                    DMI['memory',i,'Error Information Handle'] = str((v['data']['Error Information Handle']))
                    DMI['memory',i,'Form Factor'] = str((v['data']['Form Factor']))
                    DMI['memory',i,'Bank Locator'] = str((v['data']['Bank Locator']))
                    DMI['memory',i,'Locator'] = str((v['data']['Locator']))
                    DMI['memory',i,'Manufacturer'] = str((v['data']['Manufacturer']))
                    DMI['memory',i,'Part Number'] = str((v['data']['Part Number']))
                    DMI['memory',i,'Serial Number'] = str((v['data']['Serial Number']))
                    DMI['memory',i,'Size'] = str((v['data']['Size']))
                    DMI['memory',i,'Speed'] = str((v['data']['Speed']))
                    DMI['memory',i,'Type'] = str((v['data']['Type']))
                    i += 1

        # get cache Data
        #tmp = dmidecode.cache()
        #pprint(tmp)

        # get connector Data
        #tmp = dmidecode.connector()
        #pprint(tmp)

        # get slot Data
        #tmp = dmidecode.slot()
        #pprint(tmp)

        return DMI

    # TODO: THIS SUCKS!
    def __getdmi_count(self,dmi,a,b):
        try:
            count = 0
            while dmi[a,count,b]:
                count += 1
        except (KeyError):
            pass

        return count


    def create_xml (self):
        dmi = self._getdmi()
        
        pkgs = self.osbase.getpkgs()
        partitions = self.osbase.getpartitions()
        nics = self.osbase.getnics()
        
        server = xml.Element('server')

        generated = xml.Element('generated')
        generated.attrib['program'] = sys.argv[0]
        generated.attrib['version'] = '2.0'
        generated.attrib['scantime'] = time.asctime()
        server.append(generated)

        host = xml.Element('host')
        host.attrib['name'] = self.cfg.global_hostname
        server.append(host)

        hardware = xml.Element('hardware')
        server.append(hardware)

        sysboard = xml.Element('sysboard')
        sysboard.attrib['manufacturer'] = dmi['system',0,'Manufacturer']
        sysboard.attrib['productname']  = dmi['system',0,'Product Name']
        sysboard.attrib['serialnumber'] = dmi['system',0,'Serial Number']
        sysboard.attrib['boardtype']    = dmi['chassis',0,'Type']
        hardware.append(sysboard)

        processors = xml.Element('processors')
        processors.attrib['count'] =  str(self.__getdmi_count(dmi,'processor','Current Speed'))
        hardware.append(processors)
        # for every CPU do:
        count = self.__getdmi_count(dmi,'processor','Current Speed')
        i = 0
        while i < count:
            processor = xml.Element('processor')
            processor.attrib['procid']       = str(i)
            processor.attrib['family']       = dmi['processor',i,'Family']
            processor.attrib['proctype']     = dmi['processor',i,'Type']
            processor.attrib['speed']        = dmi['processor',i,'Max Speed']
            processor.attrib['version']      = dmi['processor',i,'Version']
            processor.attrib['cores']        = dmi['processor',i,'Core Count']
            processor.attrib['threads']      = dmi['processor',i,'Thread Count']
            processor.attrib['extclock']     = dmi['processor',i,'External Clock']
            processor.attrib['partnumber']   = dmi['processor',i,'Part Number']
            processor.attrib['serialnumber'] = dmi['processor',i,'Serial Number']
            if dmi['processor',i,'Thread Count'] > dmi['processor',i,'Core Count']: 
                processor.attrib['htsystem'] = 'Yes'
            else:
                processor.attrib['htsystem'] = 'No'
            processors.append(processor)
            i += 1

        memory = xml.Element('memory')
        memory.attrib['count'] = str(self.__getdmi_count(dmi,'memory','Size'))
        hardware.append(memory)

        # for every memorybank do:
        count = self.__getdmi_count(dmi,'memory','Size')
        i = 0
        while i < count:
            memorymodule = xml.Element('memorymodule')
            memorymodule.attrib['location'] = dmi['memory',i,'Locator']
            memorymodule.attrib['bank'] = dmi['memory',i,'Bank Locator']
            memorymodule.attrib['memorysize'] = dmi['memory',i,'Size']
            memorymodule.attrib['formfactor'] = dmi['memory',i,'Form Factor']
            memorymodule.attrib['manufacturer'] = dmi['memory',i,'Manufacturer']
            memorymodule.attrib['memorytype'] = dmi['memory',i,'Type']
            memorymodule.attrib['partnumber'] = dmi['memory',i,'Part Number']
            memorymodule.attrib['serialnumber'] = dmi['memory',i,'Serial Number']
            memorymodule.attrib['width'] = dmi['memory',i,'Data Width']
            memory.append(memorymodule)
            i += 1

        bios = xml.Element('bios')
        bios.attrib['vendor'] = dmi['bios',0,'Vendor']
        bios.attrib['version'] = dmi['bios',0,'Version']
        bios.attrib['releasedate'] = dmi['bios',0,'Relase Date']
        hardware.append(bios)

        operatingsystem = xml.Element('system')
        operatingsystem.attrib['name'] = platform.system() 
        operatingsystem.attrib['arch'] = platform.machine()
        operatingsystem.attrib['serialnumber'] = 'TODO'
        operatingsystem.attrib['manufacturer'] = 'TODO'
        distro = platform.linux_distribution()
        osx = platform.mac_ver()
        win = platform.win32_ver()
        ostype = distro[0] + distro[1] + distro[2] + osx[0] + win[0] 
        operatingsystem.attrib['detail'] = ostype
        operatingsystem.attrib['kernel'] = platform.release()
        server.append(operatingsystem)

        software = xml.Element('software')
        operatingsystem.append(software)

        # for every pkg do:
        # [name][ver][pkgsize][instsize][section][status][info][homepage][signed][files][arch]
        for i in range(len(pkgs)):
            package = xml.Element('package')
            package.attrib['name']          = pkgs[i][0]
            package.attrib['version']       = pkgs[i][1]
            package.attrib['pkgsize']       = pkgs[i][2]
            package.attrib['installedsize'] = pkgs[i][3]
            package.attrib['section']       = pkgs[i][4]
            package.attrib['status']        = pkgs[i][5]
            package.attrib['description']   = pkgs[i][6]
            package.attrib['homepage']      = pkgs[i][7]
            package.attrib['signed']        = pkgs[i][8]
            package.attrib['files']         = pkgs[i][9]
            package.attrib['arch']          = pkgs[i][10]
            software.append(package)

        filesystems = xml.Element('filesystems')
        operatingsystem.append(filesystems)

        # for every partition do:
        # disks[i] = [fsdev,fsmount,fstype,fsopts,fstotal,fsused,fsfree,fspercent]
        for i in range(len(partitions)):
            filesystem = xml.Element('filesystem')
            filesystem.attrib['device']    = partitions[i][0]
            filesystem.attrib['name']      = partitions[i][1]
            filesystem.attrib['fstype']    = partitions[i][2]
            filesystem.attrib['fsopts']    = partitions[i][3]
            filesystem.attrib['fssize']    = partitions[i][4]
            filesystem.attrib['fsused']    = partitions[i][5]
            filesystem.attrib['fsfree']    = partitions[i][6]
            filesystem.attrib['fspercent'] = partitions[i][7]
            filesystems.append(filesystem)

        swap = xml.Element('swap')
        operatingsystem.append(swap)

        # for every swap do:
        for swp in self.osbase.getswap(): 
            swaparea = xml.Element('swaparea')
            data = swp.split(' ')
            swaparea.attrib['device'] = data[0]
            swaparea.attrib['swaptype'] = data[1]
            swaparea.attrib['swapsize'] = data[2]
            swaparea.attrib['swapused'] = 'TODO'
            swaparea.attrib['swapfree'] = 'TODO'
            swap.append(swaparea)


        network = xml.Element('network')
        operatingsystem.append(network)

        # for every NIC do:
        #(a) =  nics.keys()
        #print a[0][0]
        adapters = xml.Element('nics')
        network.append(adapters)
        for n in nics:
            
            adapter = xml.Element('nic')
            adapter.attrib['name'] = n
            adapter.attrib['description'] = 'TODO'
            adapter.attrib['nictype'] = 'TODO'
            adapter.attrib['status'] = 'TODO'
            adapter.attrib['MTU'] = 'TODO'
            adapter.attrib['RXpackets'] = 'TODO'
            adapter.attrib['TXpackets'] = 'TODO'
            adapter.attrib['RXbytes'] = 'TODO'
            adapter.attrib['TXbytes'] = 'TODO'
            adapter.attrib['driver'] = 'TODO'
            adapter.attrib['kernmodule'] = 'TODO'
            adapter.attrib['macaddress'] = self.osbase.getmac(n) 
            adapters.append(adapter)

            ips = self.osbase.getip(n)
            for ipv4 in ips:
                ip = xml.Element('ipv4')
                data = ipv4.split('/')
                ip.attrib['address'] = data[0]
                ip.attrib['mask'] = data[1]
                ip.attrib['broadcast'] = 'TODO' 
                adapter.append(ip)

            ips6 = self.osbase.getip6(n)
            for ipv6 in ips6:
                ip6 = xml.Element('ipv6')
                data = ipv6.split('/')
                ip6.attrib['address'] = data[0]
                ip6.attrib['mask'] = data[1]
                ip6.attrib['broadcast'] = 'TODO' 
                adapter.append(ip6)

        dnsservers = xml.Element('dnsservers')
        network.append(dnsservers)
        # for every dnsserver do:
        for nameserver in self.osbase.getdns(): 
            data = nameserver.split('/')
            dnsentry = xml.Element(data[0])
            dnsentry.attrib['address'] = data[1]
            dnsservers.append(dnsentry)

        routing = xml.Element('routing')
        network.append(routing)

        ip4routes = xml.Element('ipv4')
        routing.append(ip4routes)

        # for every iproute do:
        for rt in self.osbase.getroutes(): 
            route = xml.Element('route')
            data = rt.split('/')
            route.attrib['destination'] = data[0]
            route.attrib['mask'] = data[2]
            route.attrib['gateway'] = data[1]
            route.attrib['flags'] = data[3]
            route.attrib['metric'] = data[4]
            route.attrib['interface'] = data[5]
            ip4routes.append(route)

        ip6routes = xml.Element('ipv6')
        routing.append(ip6routes)

        # for every iproute do:
        for rt in self.osbase.getroutes6(): 
            route6 = xml.Element('route')
            data = rt.split('/')
            route6.attrib['destination'] = data[0]
            route6.attrib['mask'] = data[1]
            route6.attrib['gateway'] = data[2]
            route6.attrib['flags'] = data[3]
            route6.attrib['metric'] = data[4]
            route6.attrib['interface'] = data[5]
            ip6routes.append(route6)


        groups = xml.Element('groups')
        operatingsystem.append(groups)

        # for every group do:
        for grp in self.osbase.getgroups(): 
            group = xml.Element('group')
            data = grp.split(':')
            group.attrib['name'] = data[0]
            groups.append(group)

            # for every group member do:
            for usr in data[1].split(','): 
                member = xml.Element('member')
                if usr:
                    member.attrib['name'] = usr
                group.append(member)

        users = xml.Element('users')
        operatingsystem.append(users)

        # for every user do:
        for usr in self.osbase.getusers(): 
            user = xml.Element('user')
            data = usr.split(':')
            user.attrib['login'] = data[1]
            user.attrib['uid'] = data[0]
            user.attrib['gid'] = 'TODO'
            user.attrib['home'] = data[2]
            user.attrib['shell'] = data[3]
            user.attrib['expire'] = 'TODO'
            user.attrib['locked'] = 'TODO'
            user.attrib['hashtype'] = 'TODO'
            user.attrib['groups'] = 'TODO'
            users.append(user)

        regional = xml.Element('regional')
        loc = locale.getdefaultlocale()
        regional.attrib['timezone'] = time.tzname[0]
        regional.attrib['charset'] = loc[0]+'.'+loc[1]
        operatingsystem.append(regional)

        processes = xml.Element('processes')
        operatingsystem.append(processes)

        # for every process do:
        for proc in self.osbase.getprocs(): 
            process = xml.Element('process')
            process.attrib['pid'] = 'TODO'
            process.attrib['owner'] = 'TODO'
            process.attrib['cputime'] = 'TODO'
            process.attrib['pcpu'] = 'TODO'
            process.attrib['pmemory'] = 'TODO'
            process.attrib['virtsize'] = 'TODO'
            process.attrib['sharedsize'] = 'TODO'
            process.attrib['priority'] = 'TODO'
            process.attrib['command'] = proc
            processes.append(process)

        services = xml.Element('services')
        operatingsystem.append(services)

        # for every service do:
        for svc in self.osbase.getsvcs(): 
            service = xml.Element('service')
            data = svc.split('/')
            service.attrib['name'] = data[0]
            service.attrib['autostart'] = data[1]
            service.attrib['running'] = 'TODO'
            services.append(service)

        # make xml pretty ;)
        raw_xml = xml.tostring(server, 'utf-8')
        #reparsed_xml = minidom.parseString(raw_xml)
        #pretty_xml = reparsed_xml.toprettyxml(indent="  ")

        return raw_xml
        #f = open("/tmp/test.xml", 'w')
        #f.write(pretty_xml)
        #f.close()




class TeddixCfg2Html:
    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.cfg = cfg
        self.agent_cfg2html_file = self.cfg.global_workdir  + '/agent' + "/" + self.cfg.global_hostname + ".html" 

    def run(self):
        try:
            subprocess.Popen(self.cfg.agent_cfg2html,stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
            self.syslog.info("cfg2html succeeded ")
        except Exception, e:
            self.syslog.warn("cfg2html failed ")
            self.syslog.debug("run() %s " % e)
    
    def create_html(self):
        f = open(self.agent_cfg2html_file, 'r')
        html = f.read()
        f.close()
        return html


class TeddixOra2Html:
    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.cfg = cfg
        self.ora2html_file = self.cfg.global_workdir  + '/agent' + "/" + self.cfg.global_hostname + "_ora2html.html"

    def run(self):
        try:
            subprocess.Popen([self.cfg.agent_ora2html,"-file", self.ora2html_file], stderr=subprocess.STDOUT, stdout=subprocess.PIPE).communicate()[0]
            self.syslog.info("ora2html succeeded ")
        except Exception, e:
            self.syslog.warn("ora2html failed ")
            self.syslog.debug("run() %s " % e)

    def create_html(self):
        f = open(self.ora2html_file, 'r')
        html = f.read()
        f.close()
        return html

if __name__ == "__main__":
    cfg = TeddixConfigFile.TeddixConfigFile()

    # Open syslog
    syslog = TeddixLogger.TeddixLogger ("TeddixInventory")
    syslog.open_console()

    # Switch to working directory
    try:
        os.chdir(cfg.global_workdir + '/agent')
    except Exception, e:
        syslog.error("Unable to change workdir to %s " % cfg.global_workdir + '/agent')
        syslog.exception('__init__(): %s' % e )
        exit(20)

    if not os.access(cfg.global_workdir + '/agent', os.R_OK):
        syslog.error("workdir %s needs to be readable" % cfg.global_workdir + '/agent')
    if not os.access(cfg.global_workdir + '/agent', os.W_OK):
        syslog.error("workdir %s needs to be writable" % cfg.global_workdir + '/agent')
    if not os.access(cfg.global_workdir + '/agent', os.X_OK):
        syslog.error("workdir %s needs to be executable" % cfg.global_workdir + '/agent')

    baseline = TeddixBaseline(syslog,cfg)
    raw_xml = baseline.create_xml()
    # make xml pretty ;)
    reparsed_xml = minidom.parseString(raw_xml)
    pretty_xml = reparsed_xml.toprettyxml(indent="  ")

    print pretty_xml
    #cfg2html = TeddixCfg2Html(syslog,cfg)
    #cfg2html.run()
    #ora2html = TeddixOra2Html(syslog,cfg)
    #ora2html.run()


