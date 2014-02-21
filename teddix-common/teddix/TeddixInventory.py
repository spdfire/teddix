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

class TeddixBaseline:
    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.cfg = cfg
        
        system = platform.system()
        
        self.syslog.info("Generating Baseline")

        if system == 'Linux':
            import TeddixLinux

            self.osbase = TeddixLinux.TeddixLinux(syslog)

        elif system == 'SunOS':
            import TeddixSunOS
            
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
        for v  in dmidecode.baseboard().values():
            if type(v) == dict and v['dmi_type'] == 2:
                DMI['baseboard',0,'Manufacturer'] = str((v['data']['Manufacturer']))
                DMI['baseboard',0,'Product Name'] = str((v['data']['Product Name']))
                DMI['baseboard',0,'Serial Number'] = str((v['data']['Serial Number']))
                DMI['baseboard',0,'Version'] = str((v['data']['Version']))


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

        bios = xml.Element('bios')
        count = self.__getdmi_count(dmi,'bios','Vendor')
        i = 0
        while i < count:
            bios.attrib['revision']     = dmi['bios',0,'BIOS Revision']
            bios.attrib['vendor']       = dmi['bios',0,'Vendor']
            bios.attrib['version']      = dmi['bios',0,'Version']
            bios.attrib['releasedate']  = dmi['bios',0,'Relase Date']
            i += 1
        hardware.append(bios)

        sysboard = xml.Element('baseboard')
        count = self.__getdmi_count(dmi,'baseboard','Version')
        i = 0
        while i < count:
            sysboard.attrib['manufacturer']     = dmi['baseboard',0,'Manufacturer']
            sysboard.attrib['productname']      = dmi['baseboard',0,'Product Name']
            sysboard.attrib['serialnumber']     = dmi['baseboard',0,'Serial Number']
            sysboard.attrib['version']          = dmi['baseboard',0,'Version']
            i += 1
        hardware.append(sysboard)

        system = xml.Element('system')
        count = self.__getdmi_count(dmi,'system','Version')
        i = 0
        while i < count:
            system.attrib['manufacturer'] = dmi['system',0,'Manufacturer']
            system.attrib['productname']  = dmi['system',0,'Product Name']
            system.attrib['family']       = dmi['system',0,'Family']
            system.attrib['serialnumber'] = dmi['system',0,'Serial Number']
            system.attrib['version']      = dmi['system',0,'Version']
            i += 1
        hardware.append(system)
        
        chassis = xml.Element('chassis')
        count = self.__getdmi_count(dmi,'chassis','Version')
        i = 0
        while i < count:
            chassis.attrib['manufacturer'] = dmi['chassis',0,'Manufacturer']
            chassis.attrib['serialnumber'] = dmi['chassis',0,'Serial Number']
            chassis.attrib['thermalstate'] = dmi['chassis',0,'Thermal State']
            chassis.attrib['type']         = dmi['chassis',0,'Type']
            chassis.attrib['version']      = dmi['chassis',0,'Version']
            i += 1
        hardware.append(chassis)

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
            processor.attrib['socket']       = dmi['processor',i,'Socket Designation']
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
            memorymodule.attrib['location']     = dmi['memory',i,'Locator']
            memorymodule.attrib['bank']         = dmi['memory',i,'Bank Locator']
            memorymodule.attrib['memorysize']   = dmi['memory',i,'Size']
            memorymodule.attrib['formfactor']   = dmi['memory',i,'Form Factor']
            memorymodule.attrib['manufacturer'] = dmi['memory',i,'Manufacturer']
            memorymodule.attrib['memorytype']   = dmi['memory',i,'Type']
            memorymodule.attrib['partnumber']   = dmi['memory',i,'Part Number']
            memorymodule.attrib['serialnumber'] = dmi['memory',i,'Serial Number']
            memorymodule.attrib['width']        = dmi['memory',i,'Data Width']
            memorymodule.attrib['speed']        = dmi['memory',i,'Speed']
            memory.append(memorymodule)
            i += 1
        
        # get blockdevices 
        blockdevs = self.osbase.getblock()
        blockdevices = xml.Element('blockdevices')
        blockdevices.attrib['count'] = str(len(blockdevs))
        hardware.append(blockdevices)

        #[name,devtype,vendor,model,nr_sectors,sect_size,rotational,readonly,removable,major,minor]
        i = 0 
        for i in range(len(blockdevs)):
            block = xml.Element('blockdevice')
            block.attrib['name']        = blockdevs[i][0] 
            block.attrib['type']        = blockdevs[i][1] 
            block.attrib['vendor']      = blockdevs[i][2] 
            block.attrib['model']       = blockdevs[i][3] 
            block.attrib['sectors']     = blockdevs[i][4] 
            block.attrib['sectorsize']  = blockdevs[i][5] 
            block.attrib['rotational']  = blockdevs[i][6] 
            block.attrib['readonly']    = blockdevs[i][7] 
            block.attrib['removable']   = blockdevs[i][8] 
            block.attrib['major']       = blockdevs[i][9] 
            block.attrib['minor']       = blockdevs[i][10] 
            blockdevices.append(block)

        # get PCIdevices 
        pcidevs = self.osbase.getpci()
        pcidevices = xml.Element('pcidevices')
        pcidevices.attrib['count'] = str(len(pcidevs))
        hardware.append(pcidevices)

        # [path,devtype,vendor,model,revision]
        i = 0 
        for i in range(len(pcidevs)):
            pci = xml.Element('pcidevice')
            pci.attrib['path']        = pcidevs[i][0] 
            pci.attrib['type']        = pcidevs[i][1] 
            pci.attrib['vendor']      = pcidevs[i][2] 
            pci.attrib['model']       = pcidevs[i][3] 
            pci.attrib['revision']    = pcidevs[i][4] 
            pcidevices.append(pci)

        # TODO: get info from HP tools 

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

        pkgs = self.osbase.getpkgs()
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

        updates = self.osbase.getupdates()
       
        up2date = xml.Element('updates')
        operatingsystem.append(up2date)

        # for every update do:
        secupdate = 0 
        bugfixupdate = 0 
        totalupdate = 0 
        for i in range(len(updates)): 
            package = xml.Element('package')
            package.attrib['type']        = updates[i][0]
            package.attrib['name']        = updates[i][1]
            package.attrib['available']   = updates[i][2]
            package.attrib['info']        = 'N/A'
            if updates[i][0] == "security":
                secupdate += 1 
            if updates[i][0] == "bugfix":
                bugfixupdate += 1 
            totalupdate += 1 
            up2date.append(package)
        
        up2date.attrib['total'] = str(totalupdate)
        up2date.attrib['security'] = str(secupdate)
        up2date.attrib['bugfix'] = str(bugfixupdate)


        partitions = self.osbase.getpartitions()
        # for every partition do:
        # disks[i] = [fsdev,fsmount,fstype,fsopts,fstotal,fsused,fsfree,fspercent]
        for i in range(len(partitions)):
            filesystem = xml.Element('filesystem')
            filesystem.attrib['fsdevice']  = partitions[i][0]
            filesystem.attrib['fsname']    = partitions[i][1]
            filesystem.attrib['fstype']    = partitions[i][2]
            filesystem.attrib['fsopts']    = partitions[i][3]
            filesystem.attrib['fstotal']   = partitions[i][4]
            filesystem.attrib['fsused']    = partitions[i][5]
            filesystem.attrib['fsfree']    = partitions[i][6]
            filesystem.attrib['fspercent'] = partitions[i][7]
            filesystems.append(filesystem)

        swap = xml.Element('swap')
        operatingsystem.append(swap)

        swaps = self.osbase.getswap() 
        # for every swap do:
        # swaps[i] = [dev,type,total,used,free]
        for i in range(len(swaps)): 
            swaparea = xml.Element('swaparea')
            swaparea.attrib['device']   = swaps[i][0]
            swaparea.attrib['swaptype'] = swaps[i][1]
            swaparea.attrib['swapsize'] = swaps[i][2]
            swaparea.attrib['swapused'] = swaps[i][3]
            swaparea.attrib['swapfree'] = swaps[i][4]
            swap.append(swaparea)


        network = xml.Element('network')
        operatingsystem.append(network)

        nics = self.osbase.getnics()
        # for every NIC do:
        #(a) =  nics.keys()
        #print a[0][0]
        adapters = xml.Element('nics')
        network.append(adapters)
        #[name,description,nictype,status,rx_packets,tx_packets,rx_bytes,tx_bytes,driver,drvver,firmware,kernmodule,macaddr]
        for i in range(len(nics)):
            adapter = xml.Element('nic')
            adapter.attrib['name']        = nics[i][0]
            adapter.attrib['description'] = nics[i][1]
            adapter.attrib['nictype']     = nics[i][2]
            adapter.attrib['status']      = nics[i][3]
            adapter.attrib['RXpackets']   = nics[i][4]
            adapter.attrib['TXpackets']   = nics[i][5]
            adapter.attrib['RXbytes']     = nics[i][6]
            adapter.attrib['TXbytes']     = nics[i][7]
            adapter.attrib['driver']      = nics[i][8]
            adapter.attrib['drvver']      = nics[i][9]
            adapter.attrib['firmware']    = nics[i][10]
            adapter.attrib['kernmodule']  = nics[i][11]
            adapter.attrib['macaddress']  = nics[i][12]
            adapters.append(adapter)

            ips = self.osbase.getip(nics[i][0])
            for j in range(len(ips)):
                ip = xml.Element('ipv4')
                ip.attrib['address']      = ips[j][0]
                ip.attrib['mask']         = ips[j][1]
                ip.attrib['broadcast']    = ips[j][2] 
                adapter.append(ip)

            ips6 = self.osbase.getip6(nics[i][0])
            for k in range(len(ips6)):
                ip6 = xml.Element('ipv6')
                ip6.attrib['address']     = ips6[k][0] 
                ip6.attrib['mask']        = ips6[k][1]
                ip6.attrib['broadcast']   = ips6[k][2]
                adapter.append(ip6)

        dnsservers = xml.Element('dnsservers')
        network.append(dnsservers)
        # for every dnsserver do:
        dns = self.osbase.getdns() 
        for i in range(len(dns)): 
            dnsentry = xml.Element(dns[i][0])
            dnsentry.attrib['address']    = dns[i][1]
            dnsservers.append(dnsentry)

        routing = xml.Element('routing')
        network.append(routing)

        ip4routes = xml.Element('ipv4')
        routing.append(ip4routes)

        routes4 = self.osbase.getroutes()
        # for every iproute do:
        for i in range(len(routes4)):
            route = xml.Element('route')
            route.attrib['destination'] = routes4[i][0]
            route.attrib['gateway']     = routes4[i][1]
            route.attrib['mask']        = routes4[i][2]
            route.attrib['flags']       = routes4[i][3]
            route.attrib['metric']      = routes4[i][4]
            route.attrib['interface']   = routes4[i][5]
            ip4routes.append(route)

        ip6routes = xml.Element('ipv6')
        routing.append(ip6routes)

        routes6 = self.osbase.getroutes6()
        # for every iproute do:
        for i in range(len(routes6)):
            route6 = xml.Element('route')
            route6.attrib['destination'] = routes6[i][0]
            route6.attrib['mask']        = routes6[i][1]
            route6.attrib['gateway']     = routes6[i][2]
            route6.attrib['flags']       = routes6[i][3]
            route6.attrib['metric']      = routes6[i][4]
            route6.attrib['interface']   = routes6[i][5]
            ip6routes.append(route6)


        groups = xml.Element('groups')
        operatingsystem.append(groups)

        pwgroups = self.osbase.getgroups()
        # for every group do:
        for i in range(len(pwgroups)):
            group = xml.Element('group')
            group.attrib['name']        = pwgroups[i][0]
            group.attrib['gid']         = pwgroups[i][1]
            groups.append(group)

            # for every group member do:
            for usr in pwgroups[i][2].split(','): 
                if usr:
                    member = xml.Element('member')
                    member.attrib['name'] = usr
                    group.append(member)

        xmlusers = xml.Element('users')
        operatingsystem.append(xmlusers)

        # for every user do:
        users = self.osbase.getusers()
        # [login,uid,gid,comment,home,shell,locked,hashtype,groups]
        for i in range(len(users)): 
            user = xml.Element('user')
            user.attrib['login']            = users[i][0]
            user.attrib['uid']              = users[i][1]
            user.attrib['gid']              = users[i][2]
            user.attrib['comment']          = users[i][3]
            user.attrib['home']             = users[i][4]
            user.attrib['shell']            = users[i][5]
            user.attrib['locked']           = users[i][6]
            user.attrib['hashtype']         = users[i][7]
            user.attrib['groups']           = users[i][8]
            xmlusers.append(user)

        regional = xml.Element('regional')
        loc = locale.getdefaultlocale()
        regional.attrib['timezone'] = time.tzname[0]
        regional.attrib['charset'] = loc[0]+'.'+loc[1]
        operatingsystem.append(regional)

        processes = xml.Element('processes')
        operatingsystem.append(processes)

        # for every process do:
        procs = self.osbase.getprocs()
        # [ppid,powner,psystime,pusertime,pcpu,pmem,ppriority,pstatus,pname,pcmd]
        for i in range(len(procs)):
            process = xml.Element('process')
            process.attrib['pid']           = procs[i][0]
            process.attrib['owner']         = procs[i][1]
            process.attrib['cpusystime']    = procs[i][2]
            process.attrib['cpuusertime']   = procs[i][3]
            process.attrib['pcpu']          = procs[i][4]
            process.attrib['pmemory']       = procs[i][5]
            process.attrib['priority']      = procs[i][6]
            process.attrib['status']        = procs[i][7]
            process.attrib['name']          = procs[i][8]
            process.attrib['command']       = procs[i][9]
            processes.append(process)

        services = xml.Element('services')
        operatingsystem.append(services)

        svcs = self.osbase.getsvcs()
        # for every service do:
        # [name,boot,status]
        for i in range(len(svcs)):
            service = xml.Element('service')
            service.attrib['name']          = svcs[i][0]
            service.attrib['autostart']     = svcs[i][1]
            service.attrib['running']       = svcs[i][2]
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

class TeddixBootlog:
    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.cfg = cfg

    def get(self):
        dmesg = 'N/A'

        t_bootdmesg1 = "test -f /var/log/dmesg"
        t_bootdmesg2 = "test -f /var/log/dmesg.boot"
        t_bootdmesg3 = "test -f /var/log/boot.dmesg"
        t_bootdmesg4 = "test -f /var/log/boot.log"
        if subprocess.call(t_bootdmesg1,shell=True) == 0:
            self.syslog.debug("Found /var/log/dmesg" )
            f = open('/var/log/dmesg', 'r')
            dmesg = f.read()
            f.close()
 
        elif subprocess.call(t_bootdmesg2,shell=True) == 0:
            self.syslog.debug("Found /var/log/dmesg.boot" )
            f = open('/var/log/dmesg.boot', 'r')
            dmesg = f.read()
            f.close()

        elif subprocess.call(t_bootdmesg3,shell=True) == 0:
            self.syslog.debug("Found /var/log/boot.dmesg" )
            f = open('/var/log/boot.dmesg', 'r')
            dmesg = f.read()
            f.close()

        elif subprocess.call(t_bootdmesg4,shell=True) == 0:
            self.syslog.debug("Found /var/log/boot.log" )
            f = open('/var/log/boot.log', 'r')
            dmesg = f.read()
            f.close()

        else: 
            self.syslog.debug("Fallback to dmesg command" % self.dist[0])
            cmd = "dmesg --ctime"
            state = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            dmesg = state.stdout.read()

        return dmesg


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


