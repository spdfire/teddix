from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import Context, Template

# Syslog handler                                                                
import logging
from teddix import TeddixLogger                                                 
                                                                                
# Config parser                                                                 
from teddix import TeddixConfigFile

# SQL Database                                                                                                                                                
from teddix import TeddixDatabase                                               
                                                                                
# Parser                                                                        
from teddix import TeddixParser

def check_permissions(request):
    if not request.user.is_authenticated():
        return redirect('/users/login/?next=%s' % request.path)

def agents_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    agent_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT id,name FROM server "
    database.execute(sql)
    result = database.fetchall()
    for row in result:
        server_id = row[0]
        server_name = row[1]
        if server_name.find(search) != -1 :
            agent_list.append({'id': server_id, 'name': server_name })

    database.disconnect()
    context = Context({'agent_list': agent_list, 'search': search } )
    return render(request, 'hosts/agents.html', context )

def os_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    os_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT name FROM system "
    database.execute(sql)
    result = database.fetchall()
    os_id = 0 
    for row in result:
        os_name = row[0]
        sql = "SELECT DISTINCT server_id,name FROM system WHERE name = '%s' "
        database.execute(sql % os_name)
        os_count = database.rowcount()
        if os_name.find(search) != -1 :
           os_list.append({'id': os_id, 'name': os_name, 'count': os_count })
        os_id += 1 

    database.disconnect()
    context = Context({'os_list': os_list, 'search': search } )
    return render(request, 'hosts/os.html', context )

def arch_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    arch_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT arch FROM system "
    database.execute(sql)
    result = database.fetchall()
    arch_id = 0 
    for row in result:
        arch_name = row[0]
        sql = "SELECT DISTINCT server_id,arch FROM system WHERE arch = '%s' "
        database.execute(sql % arch_name)
        arch_count = database.rowcount()
        if arch_name.find(search) != -1 :
           arch_list.append({'id': arch_id, 'name': arch_name, 'count': arch_count })
        arch_id += 1 

    database.disconnect()
    context = Context({'arch_list': arch_list, 'search': search } )
    return render(request, 'hosts/arch.html', context )

def net_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    net4_list = []
    net6_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT address,mask FROM ipv4 "
    database.execute(sql)
    result = database.fetchall()
    net4_id = 0 
    for row in result:
        net4_name = row[0]
        net4_mask = row[1]
        if net4_name.find(search) != -1 :
           net4_list.append({'id': net4_id, 'name': net4_name, 'mask': net4_mask })
        net4_id += 1 

    sql = "SELECT DISTINCT address,mask FROM ipv6 "
    database.execute(sql)
    result = database.fetchall()
    net6_id = 0 
    for row in result:
        net6_name = row[0]
        net6_mask = row[1]
        if net6_name.find(search) != -1 :
           net6_list.append({'id': net6_id, 'name': net6_name, 'mask': net6_mask })
        net6_id += 1 

    database.disconnect()
    context = Context({'net4_list': net4_list, 'net6_list': net6_list, 'search': search } )
    return render(request, 'hosts/net.html', context )

def software_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    pkg_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT name,version,arch,installedsize FROM package "
    database.execute(sql)
    result = database.fetchall()
    pkg_id = 0 
    for row in result:
        pkg_name = row[0]
        pkg_version = row[1]
        pkg_arch = row[2]
        pkg_size = row[3]
        if pkg_name.find(search) != -1 :
		pkg_list.append({'id': pkg_id, 'name': pkg_name, 'version': pkg_version, 'arch': pkg_arch, 'size': pkg_size })
        pkg_id += 1 

    database.disconnect()
    context = Context({'pkg_list': pkg_list, 'search': search } )
    return render(request, 'hosts/software.html', context )

def updates_view(request):
    check_permissions(request)

def usersgroups_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    user_list = []
    group_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT login FROM sysuser "
    database.execute(sql)
    result = database.fetchall()
    user_id = 0 
    for row in result:
        user_login = row[0]
        if user_login.find(search) != -1 :
		user_list.append({'id': user_id, 'login': user_login })
        user_id += 1 

    sql = "SELECT DISTINCT name FROM sysgroup "
    database.execute(sql)
    result = database.fetchall()
    group_id = 0 
    for row in result:
        group_name = row[0]
        if group_name.find(search) != -1 :
		group_list.append({'id': group_id, 'name': group_name })
        group_id += 1 

    database.disconnect()
    context = Context({'user_list': user_list, 'group_list': group_list, 'search': search } )
    return render(request, 'hosts/usersgroups.html', context )

def hardware_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    cpu_list = []
    mem_list = []
    board_list = []
    disk_list = []
    pci_list = []
    bios_list = []
    search = request.GET.get('search','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    sql = "SELECT DISTINCT familly,speed,cores,htsystem FROM processor "
    database.execute(sql)
    result = database.fetchall()
    cpu_id = 0 
    for row in result:
        #cpu_familly = row[0]
        #cpu_speed = row[1]
        cpu_familly = 'TODO'
        cpu_speed = 'TODO'
        cpu_cores = row[2]
        cpu_ht = row[3]
        #if cpu_familly.find(search) != -1 :
	cpu_list.append({'id': cpu_id, 'familly': cpu_familly, 'speed': cpu_speed, 'cores': cpu_cores, 'ht': cpu_ht })
        cpu_id += 1 

    sql = "SELECT DISTINCT manufacturer,modulesize,speed FROM memorymodule "
    database.execute(sql)
    result = database.fetchall()
    mem_id = 0 
    for row in result:
        mem_manufacturer = row[0]
        mem_modulesize = row[1]
        mem_speed = row[2]
        if mem_manufacturer.find(search) != -1 :
		mem_list.append({'id': mem_id, 'manufacturer': mem_manufacturer, 'size': mem_modulesize, 'speed': mem_speed })
        mem_id += 1 

    sql = "SELECT DISTINCT manufacturer,productname,version FROM baseboard "
    database.execute(sql)
    result = database.fetchall()
    board_id = 0 
    for row in result:
        board_manufacturer = row[0]
        board_productname = row[1]
        board_version = row[2]
        if board_productname.find(search) != -1 :
		board_list.append({'id': board_id, 'manufacturer': board_manufacturer, 'productname': board_productname, 'version': board_version })
        board_id += 1 

    sql = "SELECT DISTINCT model,sectors,sectorsize FROM blockdevice "
    database.execute(sql)
    result = database.fetchall()
    disk_id = 0 
    for row in result:
        disk_model = row[0]
        disk_size = str( parser.str2int(row[1]) * parser.str2int(row[2]))
        if disk_model.find(search) != -1 :
		disk_list.append({'id': disk_id, 'model': disk_model, 'size': disk_size })
        disk_id += 1 

    sql = "SELECT DISTINCT devtype,vendor,model FROM pcidevice "
    database.execute(sql)
    result = database.fetchall()
    pci_id = 0 
    for row in result:
        pci_type = row[0]
        pci_vendor = row[1]
        pci_model = row[2]
        if pci_model.find(search) != -1 :
		pci_list.append({'id': pci_id, 'type': pci_type, 'vendor': pci_vendor, 'model': pci_model })
        pci_id += 1 

    sql = "SELECT DISTINCT vendor,version FROM bios "
    database.execute(sql)
    result = database.fetchall()
    bios_id = 0 
    for row in result:
        bios_vendor = row[0]
        bios_version = row[1]
        if bios_vendor.find(search) != -1 :
		bios_list.append({'id': bios_id, 'vendor': bios_vendor, 'version': bios_version })
        bios_id += 1 

    database.disconnect()
    context = Context({'cpu_list': cpu_list, 'mem_list': mem_list, 'board_list': board_list, 'disk_list': disk_list, 'pci_list': pci_list, 'bios_list': bios_list, 'search': search } )
    return render(request, 'hosts/hardware.html', context )



def dashboard_view(request):
    check_permissions(request)
    return render(request, 'monitor/dashboard.html')


def base_view(request):
    check_permissions(request)
    return render(request, 'base.html')


def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(1209600) # 2 weeks
    return auth_views.login(request, *args, **kwargs)

