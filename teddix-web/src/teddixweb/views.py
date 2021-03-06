# django 
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.core.context_processors import csrf
from django.template import Context, Template

# pygal 
import pygal
from pygal.style import LightSolarizedStyle
from pygal.style import CleanStyle
from pygal.style import LightColorizedStyle

# teddix
import logging 
from teddix import TeddixLogger
from teddix import TeddixConfigFile
from teddix import TeddixDatabase
from teddix import TeddixParser


#### helpers ####
def agents2ids(database):
    agents = []  

# get latest baseline ID for agents 
def agents2baselines(database):
    baselines = []  

    sql = "SELECT * FROM server " 
    database.execute(sql)
    result = database.fetchall()
    for row in result:
        agent_id = row[0]
        agent_name = row[1]
        agent_created = row[2]
 
        sql = "SELECT id FROM baseline WHERE created = (SELECT MAX(created) FROM baseline WHERE server_id = %s )"
        database.execute(sql,agent_id)
        result2 = database.fetchall()
        for row2 in result2:
            baselines.append(row2[0])

    return baselines

def agents2oslist(database):
    baselines = agents2baselines(database)
    agents_per_os = {}
    os_names = []
    for baseline in baselines: 
        sql = "SELECT name FROM system WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result2 = database.fetchall()
        for row2 in result2:
            os_name = row2[0]

            if os_name not in os_names: 
                os_names.append(os_name)
                agents_per_os[os_name] = 1 
            else:
                agents_per_os[os_name] += 1 

    return agents_per_os
 
def agents2archlist(database):
    baselines = agents2baselines(database)
    agents_per_arch = {}
    arch_names = []
    for baseline in baselines: 
        sql = "SELECT arch FROM system WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result2 = database.fetchall()
        for row2 in result2:
            arch_name = row2[0]

            if arch_name not in arch_names: 
                arch_names.append(arch_name)
                agents_per_arch[arch_name] = 1 
            else:
                agents_per_arch[arch_name] += 1 

    return agents_per_arch

def agents2netlist(database,ntype='ipv4'):
    baselines = agents2baselines(database)
    agents_per_net = {}
    net_names = []
    if ntype == 'ipv6':
        for baseline in baselines: 
            sql = "SELECT address,mask FROM ipv6 WHERE baseline_id = %s "
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                net_name = row[0]

                if net_name not in net_names: 
                    net_names.append(net_name)
                    agents_per_net[net_name] = 1 
                else:
                    agents_per_net[net_name] += 1 

    else: 
        for baseline in baselines: 
            sql = "SELECT address,mask FROM ipv4 WHERE baseline_id = %s "
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                net_name = row[0]

                if net_name not in net_names: 
                    net_names.append(net_name)
                    agents_per_net[net_name] = 1 
                else:
                    agents_per_net[net_name] += 1 

    return agents_per_net


def agents2softwarelist(database):
    baselines = agents2baselines(database)
    agents_per_pkg = {}
    pkg_names = []
    for baseline in baselines: 
        sql = "SELECT name,section FROM package WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            pkg_name = row[0] 

            if pkg_name not in pkg_names: 
                pkg_names.append(pkg_name)
                agents_per_pkg[pkg_name] = 1 
            else:
                agents_per_pkg[pkg_name] += 1 

    return agents_per_pkg

def pkgs2sectionlist(database):
    baselines = agents2baselines(database)
    pkgs_per_section = {}
    pkg_sections = []
    for baseline in baselines: 
        sql = "SELECT name,section FROM package WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            pkg_name = row[0] 
            pkg_section = row[1] 

            if pkg_section not in pkg_sections: 
                pkg_sections.append(pkg_section)
                pkgs_per_section[pkg_section] = 1 
            else:
                pkgs_per_section[pkg_section] += 1 

    return pkgs_per_section


def agents2patchlist(database,patchtype=None):
    baselines = agents2baselines(database)
    agents_per_patch = {}
    patch_names = []

    if patchtype == 'security':
         for baseline in baselines: 
            sql = "SELECT name,version,patchtype FROM patch WHERE baseline_id = %s AND patchtype = 'security'"
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                patch_name = row[0] + '-' + row[1]

                if patch_name not in patch_names: 
                    patch_names.append(patch_name)
                    agents_per_patch[patch_name] = 1 
                else:
                    agents_per_patch[patch_name] += 1 
    elif patchtype == 'bugfix':
         for baseline in baselines: 
            sql = "SELECT name,version,patchtype FROM patch WHERE baseline_id = %s AND patchtype = 'bugfix'"
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                patch_name = row[0] + '-' + row[1]

                if patch_name not in patch_names: 
                    patch_names.append(patch_name)
                    agents_per_patch[patch_name] = 1 
                else:
                    agents_per_patch[patch_name] += 1 
    elif patchtype == 'improvement':
         for baseline in baselines: 
            sql = "SELECT name,version,patchtype FROM patch WHERE baseline_id = %s AND patchtype = 'improvement'"
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                patch_name = row[0] + '-' + row[1]

                if patch_name not in patch_names: 
                    patch_names.append(patch_name)
                    agents_per_patch[patch_name] = 1 
                else:
                    agents_per_patch[patch_name] += 1 
    elif patchtype == 'other':
        for baseline in baselines: 
            sql = "SELECT name,version,patchtype FROM patch WHERE baseline_id = %s AND ( patchtype = 'other' OR patchtype = '' ) "
            database.execute(sql,baseline)
            result = database.fetchall()
            for row in result:
                patch_name = row[0] + '-' + row[1]

                if patch_name not in patch_names: 
                    patch_names.append(patch_name)
                    agents_per_patch[patch_name] = 1 
                else:
                    agents_per_patch[patch_name] += 1 


    return agents_per_patch

def agents2userlist(database):
    baselines = agents2baselines(database)
    agents_per_user = {}
    names = []
    for baseline in baselines: 
        sql = "SELECT login FROM sysuser WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            name = row[0] 

            if name not in names: 
                names.append(name)
                agents_per_user[name] = 1 
            else:
                agents_per_user[name] += 1 

    return agents_per_user

def agents2grouplist(database):
    baselines = agents2baselines(database)
    agents_per_group = {}
    names = []
    for baseline in baselines: 
        sql = "SELECT name FROM sysgroup WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            name = row[0] 

            if name not in names: 
                names.append(name)
                agents_per_group[name] = 1 
            else:
                agents_per_group[name] += 1 
 
    return agents_per_group

def users2hashlist(database):
    baselines = agents2baselines(database)
    users_per_hash = {}
    hash_names = []
    for baseline in baselines: 
        sql = "SELECT hashtype FROM sysuser WHERE baseline_id = %s AND locked = 'False'"
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            hash_name = row[0]

            if hash_name not in hash_names: 
                hash_names.append(hash_name)
                users_per_hash[hash_name] = 1 
            else:
                users_per_hash[hash_name] += 1 

    return users_per_hash
 
def users2activelist(database):
    baselines = agents2baselines(database)
    users_per_status = {}
    status_names = []
    for baseline in baselines: 
        sql = "SELECT locked FROM sysuser WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            if row[0] == 'False':
                status_name = 'Active'
            elif row[0] == 'True':
                status_name = 'Locked'
            else:
                status_name = 'Unknown'

            if status_name not in status_names: 
                status_names.append(status_name)
                users_per_status[status_name] = 1 
            else:
                users_per_status[status_name] += 1 

    return users_per_status
 
def users2typelist(database):
    baselines = agents2baselines(database)
    users_per_type = {}
    type_names = []
    for baseline in baselines: 
        sql = "SELECT uid FROM sysuser WHERE baseline_id = %s "
        database.execute(sql,baseline)
        result = database.fetchall()
        for row in result:
            if int(row[0]) < 1000:
                type_name = 'System Account'
            elif int(row[0]) >= 1000 :
                type_name = 'User Account'
            else:
                type_name = 'Unknown'

            if type_name not in type_names: 
                type_names.append(type_name)
                users_per_type[type_name] = 1 
            else:
                users_per_type[type_name] += 1 

    return users_per_type
 

def check_permissions(request):
    if not request.user.is_authenticated():
        return redirect('/users/login/?next=%s' % request.path)


#### views ####

def connection_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()

    action = request.GET.get('action','')
    agent_id = request.GET.get('agent_id','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 

    sql = "SELECT id,name,created,hostname,ipv4,ipv6,resolving,active FROM server WHERE id = %s " 
    database.execute(sql,agent_id)
    result = database.fetchall()
    for row in result:
        agent_id = row[0]
        agent_name = row[1]
        agent_created = row[2]
        agent_hostname = row[3]
        agent_ipv4 = row[4]
        agent_ipv6 = row[5]
        agent_resolving = row[6]
        agent_active = row[7]
 
    if agent_resolving == "dns":
        host = agent_hostname
    elif agent_resolving == "ipv4":
        host = agent_ipv4
    elif agent_resolving == "ipv6":
        host = agent_ipv6

    # TODO: RCE vuln
    output = ''
    if action == "test1":
        lines  = parser.readstdout("ping -c 3 -i 0.2 -W 10 %s" % host)
        for i in range(len(lines)):
            output += lines[i] + "\n" 

    if action == "test2":
        lines  = parser.readstdout("nmap -sT -p 45003 %s" % host )
        for i in range(len(lines)):
            output += lines[i] + "\n" 

    if action == "test3":
        lines  = parser.readstdout("tcptraceroute -w 5 %s 45003" % host)
        for i in range(len(lines)):
            output += lines[i] + "\n" 

    if action == "test4":
        lines  = parser.readstdout("curl --max-time 120 --connect-timeout 30 --insecure  https://%s:45003/status " % host )
        for i in range(len(lines)):
            output += lines[i] + "\n" 

    if action == "test5":
        lines  = parser.readstdout("curl --max-time 120 --connect-timeout 30 --insecure  https://%s:45003/baseline " % host )
        for i in range(len(lines)):
            output += lines[i] + "\n" 

    context = Context({ "agent_id": agent_id, "action": action, "output": output } )
    return render(request, 'agents/connection_test.html', context )


def agents_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    agent_list = []
    info = ''
    error = ''

    search = request.GET.get('search','')
    action = request.GET.get('action','')
    agent_id = request.GET.get('agent_id','')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 

    if action == "new":
        context = Context({ "action": action, "info": info, "error": error } )
        return render(request, 'agents/agent_edit.html', context )

    if action == "new2":
        agent_name = request.GET.get('agent_name','')
        agent_hostname = request.GET.get('agent_hostname','')
        agent_ipv4 = request.GET.get('agent_ipv4','')
        agent_ipv6 = request.GET.get('agent_ipv6','')
        agent_resolving = request.GET.get('agent_resolving','')
        agent_active = request.GET.get('agent_active','no')
        sql = "INSERT INTO server(name,created,hostname,ipv4,ipv6,resolving,active) VALUES (%s,NOW(),%s,%s,%s,%s,%s); " 
        database.execute(sql,(agent_name,agent_hostname,agent_ipv4,agent_ipv6,agent_resolving,agent_active))
        database.commit()
        info = "Agent was created"
    
    if action == "schedule":
        info = "Schedule"

    if action == "test":
        info = "Connection test"
        
        sql = "SELECT * FROM server WHERE id = %s " 
        database.execute(sql,agent_id)
        result = database.fetchall()
        for row in result:
            agent_id = row[0]
            agent_hostname = row[1]
            agent_ip = ''

        # ping -c 5 -W 5 host  
        # nc -vz -w 5 google.com 80
        # tcptraceroute -w 2 google.com 80
        # curl --max-time 5 --insecure 
        database.disconnect()
        context = Context({ "agent_id": agent_id, "agent_hostname": agent_hostname,"agent_ip": agent_ip, "info": info, "error": error } )
        return render(request, 'agents/agent_test.html', context )

    if action == "restart":
        info = "Server has been restarted!"

    if action == "delete":
        sql = "DELETE FROM server WHERE id = %s " 
        database.execute(sql,agent_id)
        database.commit()
        info = "Server has been deleted!"
        #error  = "bbbb"
    
    if action == "edit":
        sql = "SELECT id,name,created,hostname,ipv4,ipv6,resolving,active FROM server WHERE id = %s " 
        database.execute(sql,agent_id)
        result = database.fetchall()
        for row in result:
            agent_id = row[0]
            agent_name = row[1]
            agent_created = row[2]
            agent_hostname = row[3]
            agent_ipv4 = row[4]
            agent_ipv6 = row[5]
            agent_resolving = row[6]
            agent_active = row[7]
        
        database.disconnect()
        context = Context({
            "action": action,
            "agent_id": agent_id, 
            "agent_name": agent_name, 
            "agent_created": agent_created, 
            "agent_hostname": agent_hostname, 
            "agent_ipv4": agent_ipv4, 
            "agent_ipv6": agent_ipv6, 
            "agent_resolving": agent_resolving, 
            "agent_active": agent_active, 
            "info": info, "error": error } )
        return render(request, 'agents/agent_edit.html', context )
    
    if action == "edit2":
        agent_id = request.GET.get('agent_id','')
        agent_name = request.GET.get('agent_name','')
        agent_hostname = request.GET.get('agent_hostname','')
        agent_ipv4 = request.GET.get('agent_ipv4','')
        agent_ipv6 = request.GET.get('agent_ipv6','')
        agent_resolving = request.GET.get('agent_resolving','')
        agent_active = request.GET.get('agent_active','')
        sql = "UPDATE server SET name = %s, hostname = %s, ipv4 = %s, ipv6 = %s, resolving = %s, active = %s  WHERE id = %s " 
        database.execute(sql,(agent_name,agent_hostname,agent_ipv4,agent_ipv6,agent_resolving,agent_active,agent_id))
        database.commit()
        info = "Agent was modified"
    
    if action == "show":
        sql = "SELECT * FROM server WHERE id = %s " 
        database.execute(sql,agent_id)

        result = database.fetchall()
        for row in result:
            agent_id = row[0]
            agent_name = row[1]
            agent_created = row[2]
        
        sql = "SELECT COUNT(*) FROM baseline WHERE server_id = %s" 
        database.execute(sql,agent_id)

        result = database.fetchall()
        for row in result:
            agent_report_count = row[0]
        
        sql = "SELECT MAX(created) FROM baseline WHERE server_id = %s" 
        database.execute(sql,agent_id)
        result = database.fetchall()
        for row in result:
            agent_report_last = row[0]
   
        sql = "SELECT id FROM baseline WHERE created = (SELECT MAX(created) FROM baseline WHERE server_id = %s )"
        database.execute(sql,agent_id)

        if database.rowcount() < 1:
            error = "Agent does not have any hardware reports. "
            database.disconnect()
            context = Context({"agent_id": agent_id, 
                "agent_name": agent_name, 
                "agent_created": agent_created, 
                "agent_report_count": agent_report_count, 
                "agent_report_last": agent_report_last, 
                "info": info, "error": error } )
            return render(request, 'agents/agent_detail.html', context )
        
        result = database.fetchall()
        for row in result:
            baseline_id = row[0]

        sql = "SELECT name,detail,kernel,arch,manufacturer,serialnumber FROM system WHERE baseline_id = %s "
        database.execute(sql,baseline_id)
        result = database.fetchall()
        for row in result:
            os_name             = row[0]
            os_detail           = row[1]
            os_kernel           = row[2]
            os_arch             = row[3]
            os_manufacturer     = row[4]
            os_serialnumber     = row[5]

        sql = "SELECT name,version,arch,section,installedsize,status,description FROM package WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        pkg_id = 0
        pkg_list = [] 
        for row in result:
            pkg_name = row[0]
            pkg_version = row[1]
            pkg_arch = row[2]
            pkg_section = row[3]
            pkg_size = row[4]
            pkg_status = row[5]
            pkg_description = row[6]
            pkg_list.append({'id': pkg_id, 'name': pkg_name, 'version': pkg_version, 'arch': pkg_arch, 'section': pkg_section, 'size': pkg_size,'status': pkg_status, 'description': pkg_description })
            pkg_id += 1 

        sql = "SELECT name,running,autostart FROM service WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        srv_id = 0
        service_list = [] 
        for row in result:
            srv_name = row[0]
            srv_status = row[1]
            srv_autostart = row[2]
            service_list.append({'id': srv_id, 'name': srv_name, 'status': srv_status, 'autostart': srv_autostart })
            srv_id += 1 

        sql = "SELECT pid,owner,priority,status,pcpu,pmemory,name,command FROM process WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        proc_list = [] 
        for row in result:
            proc_pid = row[0]
            proc_owner = row[1]
            proc_priority = row[2]
            proc_status = row[3]
            proc_pcpu = row[4]
            proc_pmemory = row[5]
            proc_name = row[6]
            proc_command = row[7]
            proc_list.append({'pid': proc_pid, 'owner': proc_owner, 'priority': proc_priority, 'status': proc_status, 'pcpu': proc_pcpu, 'pmemory': proc_pmemory, 'name': proc_name, 'command': proc_command})

        sql = "SELECT name,version,patchtype,description FROM patch WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        patch_list = [] 
        patch_id = 0
        for row in result:
            patch_name = row[0]
            patch_version = row[1]
            patch_type = row[2]
            patch_description = row[3]
            patch_list.append({'id': patch_id, 'name': patch_name, 'version': patch_version, 'type': patch_type, 'description': patch_description })
            patch_id += 1 

        sql = "SELECT fsdevice,fsname,fstype,fsopts,fsused,fsfree,fstotal,fspercent FROM filesystem WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        fs_list = [] 
        fs_id = 0
        for row in result:
            fs_device = row[0]
            fs_mount = row[1]
            fs_type = row[2]
            fs_opts = row[3]
            fs_used = row[4]
            fs_free = row[5]
            fs_total = row[5]
            fs_pused = row[6]
            fs_list.append({'id':fs_id, 'device': fs_device, 'mountpoint': fs_mount, 'type': fs_type, 'options': fs_opts, 'used': fs_used, 'free': fs_free, 'total': fs_total, 'pused': fs_pused })
            fs_id += 1 

     
        sql = "SELECT name,driver,drvver,firmware,nictype,macaddress,status,description FROM nic WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        nic_id = 0
        nic_list = []
        for row in result:
            nic_name = row[0]
            nic_driver = row[1]
            nic_drvver = row[2]
            nic_firmware = row[3]
            nic_type = row[4]
            nic_mac = row[5]
            nic_status = row[6]
            nic_description = row[7]
            nic_list.append({'id': nic_id, 'name': nic_name, 'driver': nic_driver, 'drvver': nic_drvver, 'firmware': nic_firmware, 'type': nic_type, 'mac': nic_mac, 'status': nic_status, 'description': nic_description })
            nic_id += 1 

   
        sql = "SELECT address,mask FROM ipv4 WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        ipv4_id = 0
        ipv4_list = []
        for row in result:
            ipv4_ip = row[0]
            ipv4_mask = row[1]
            ipv4_list.append({'id': ipv4_id, 'address': ipv4_ip, 'mask': ipv4_mask })
            ipv4_id += 1 

        sql = "SELECT address,mask FROM ipv6 WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        ipv6_id = 0 
        ipv6_list = []
        for row in result:
            ipv6_ip = row[0]
            ipv6_mask = row[1]
            ipv6_list.append({'id': ipv6_id, 'address': ipv6_ip, 'mask': ipv6_mask })
            ipv6_id += 1 
 

        sql = "SELECT destination,mask,gateway,metric,flags,interface FROM route4 WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        net4_id = 0
        net4_list = []
        for row in result:
            net4_destination = row[0]
            net4_mask = row[1]
            net4_gateway = row[2]
            net4_metric = row[3]
            net4_flags = row[4]
            net4_interface = row[5]
            net4_list.append({'id': net4_id, 'destination': net4_destination, 'mask': net4_mask, 'gateway': net4_gateway, 'metric': net4_metric, 'flags': net4_flags, 'interface': net4_interface })
            net4_id += 1 

        sql = "SELECT destination,mask,gateway,metric,flags,interface FROM route6 WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        net6_id = 0 
        net6_list = []
        for row in result:
            net6_destination = row[0]
            net6_mask = row[1]
            net6_gateway = row[2]
            net6_metric = row[3]
            net6_flags = row[4]
            net6_interface = row[5]
            net6_list.append({'id': net6_id, 'destination': net6_destination, 'mask': net6_mask, 'gateway': net6_gateway, 'metric': net6_metric, 'flags': net6_flags, 'interface': net6_interface})
            net6_id += 1 

        sql = "SELECT address FROM nameserver WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        dns_id = 0 
        dns_list = []
        for row in result:
            dns_address = row[0]
            dns_list.append({'id': dns_id, 'address': dns_address})
            dns_id += 1 


        sql = "SELECT uid,gid,login,home,shell,locked,hashtype,groups,comment FROM sysuser WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        user_list = []
        for row in result:
            user_uid        = row[0]
            user_gid        = row[1]
            user_login      = row[2]
            user_homedir    = row[3]
            user_shell      = row[4]
            user_locked     = row[5]
            user_hash       = row[6]
            user_groups     = row[7]
            user_comment    = row[8]
            user_list.append({'uid': user_uid, 'gid': user_gid, 'login': user_login, 'homedir': user_homedir, 'shell': user_shell, 'locked': user_locked, 'hash': user_hash, 'groups': user_groups, 'comment': user_comment })


        sql = "SELECT family,procversion,speed,cores,threads,htsystem,proctype,socket,extclock,serialnumber,partnumber FROM processor WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        cpu_id = 0 
        cpu_list = []
        for row in result:
            cpu_family = row[0]
            cpu_version = row[1]
            cpu_speed = row[2]
            cpu_cores = row[3]
            cpu_threads = row[4]
            cpu_ht = row[5]
            cpu_type = row[6]
            cpu_socket = row[7]
            cpu_extclock = row[8]
            cpu_serialnumber = row[9]
            cpu_partnumber = row[10]
            cpu_list.append({'id': cpu_id, 'family': cpu_family, 'version': cpu_version, 'speed': cpu_speed, 'cores': cpu_cores, 'threads': cpu_threads, 'ht': cpu_ht, 'type': cpu_type, 'socket': cpu_socket, 'extclock': cpu_extclock, 'serialnumber': cpu_serialnumber, 'partnumber': cpu_partnumber})
            cpu_id += 1 

        sql = "SELECT bank,location,memorytype,modulesize,speed,width,manufacturer,serialnumber,partnumber FROM memorymodule WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        mem_id = 0 
        mem_list = []
        for row in result:
            mem_bank = row[0]
            mem_location = row[1]
            mem_type = row[2]
            mem_size = row[3]
            mem_speed = row[4]
            mem_width = row[5]
            mem_manufacturer = row[6]
            mem_serialnumber = row[7]
            mem_partnumber = row[8]
            mem_list.append({'id': mem_id, 'bank': mem_bank, 'location': mem_location, 'type': mem_type, 'size': mem_size, 'speed': mem_speed, 'width': mem_width, 'manufacturer': mem_manufacturer, 'serialnumber': mem_serialnumber, 'partnumber': mem_partnumber})
            mem_id += 1 

        sql = "SELECT manufacturer,productname,version,serialnumber FROM baseboard WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        board_id = 0 
        board_list = []
        for row in result:
            board_manufacturer = row[0]
            board_productname = row[1]
            board_version = row[2]
            board_serialnumber = row[3]
            board_list.append({'id': board_id, 'manufacturer': board_manufacturer, 'productname': board_productname, 'version': board_version, 'serialnumber': board_serialnumber})
            board_id += 1 

        sql = "SELECT name,model,vendor,devtype,sectors,sectorsize,rotational,readonly,removable,major,minor FROM blockdevice WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        block_id = 0 
        block_list = []
        for row in result:
            block_name = row[0]
            block_model = row[1]
            block_vendor = row[2]
            block_type = row[3]
            block_sectors = row[4]
            block_sectorsize = row[5]
            block_rotational = row[6]
            block_readonly = row[7]
            block_removable = row[8]
            block_major = row[9]
            block_minor = row[10]
            block_list.append({'id': block_id, 'name': block_name, 'model': block_model, 'vendor': block_vendor, 'type': block_type, 'sectors': block_sectors, 'sectorsize': block_sectorsize, 'rotational': block_rotational, 'readonly': block_readonly, 'removable': block_removable, 'major': block_major, 'minor': block_minor  })
            block_id += 1 

        sql = "SELECT path,devtype,vendor,model,revision FROM pcidevice WHERE baseline_id = %s"
        database.execute(sql,baseline_id)
        result = database.fetchall()
        pci_id = 0 
        pci_list = []
        for row in result:
            pci_path = row[0]
            pci_type = row[1]
            pci_vendor = row[2]
            pci_model = row[3]
            pci_revision = row[4]
            pci_list.append({'id': pci_id, 'path': pci_path, 'type': pci_type, 'vendor': pci_vendor, 'model': pci_model, 'revision': pci_revision})
            pci_id += 1 


        cfg2html = 'No data'
        sql = "SELECT cfg2html FROM extra WHERE server_id = %s AND created = (SELECT MAX(created) FROM extra WHERE server_id = %s )" 
        database.execute(sql,(agent_id,agent_id))
        result = database.fetchall()
        for row in result:
    	    b64_cfg2html = row[0]
	    cfg2html = parser.b64decode(b64_cfg2html)

        bootlog = 'No data'
        sql = "SELECT bootlog FROM extra WHERE server_id = %s AND created = (SELECT MAX(created) FROM extra WHERE server_id = %s )" 
        database.execute(sql,(agent_id,agent_id))
        result = database.fetchall()
        for row in result:
    	    b64_bootlog = row[0]
	    bootlog = parser.b64decode(b64_bootlog)

        dmesg = 'No data'
        sql = "SELECT dmesg FROM extra WHERE server_id = %s AND created = (SELECT MAX(created) FROM extra WHERE server_id = %s )" 
        database.execute(sql,(agent_id,agent_id))
        result = database.fetchall()
        for row in result:
    	    b64_dmesg = row[0]
	    dmesg = parser.b64decode(b64_dmesg)


        database.disconnect()
        context = Context({"agent_id": agent_id, 
            "agent_name": agent_name, 
            "agent_created": agent_created, 
            "agent_report_count": agent_report_count, 
            "agent_report_last": agent_report_last, 
            "os_name": os_name,
            "os_detail": os_detail,
            "os_kernel": os_kernel,
            "os_arch": os_arch,
            "os_manufacturer": os_manufacturer,
            "os_serialnumber": os_serialnumber,
            "pkg_list": pkg_list,
            "service_list": service_list,
            "proc_list": proc_list,
            "patch_list": patch_list,
            "fs_list": fs_list,
            "nic_list": nic_list,
            "ipv4_list": ipv4_list,
            "ipv6_list": ipv6_list,
            "net4_list": net4_list,
            "net6_list": net6_list,
            "dns_list": dns_list,
            "user_list": user_list,
            "cpu_list": cpu_list,
            "mem_list": mem_list,
            "board_list": board_list,
            "block_list": block_list,
            "pci_list": pci_list,
            "cfg2html": cfg2html,
            "bootlog": bootlog,
            "dmesg": dmesg,
            "info": info, "error": error } )
        return render(request, 'agents/agent_detail.html', context )


    sql = "SELECT id,name FROM server "
    database.execute(sql)
    result = database.fetchall()
    for row in result:
        server_id = row[0]
        server_name = row[1]
        if server_name.find(search) != -1 :
            agent_list.append({'id': server_id, 'name': server_name })

    database.disconnect()
    context = Context({'agent_list': agent_list, 'search': search, "info": info, "error": error } )
    return render(request, 'agents/agents.html', context )


def os_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    os_list = []
    search = request.GET.get('search','')
    
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_os = agents2oslist(database)
    database.disconnect()
    
    os_id = 0
    for os_name in agents_per_os: 
        if os_name.find(search) != -1 : 
            os_list.append({'id': os_id, 'name': os_name, 'count': agents_per_os[os_name] })
            os_id += 1

    context = Context({'os_list': os_list, 'search': search } )
    return render(request, 'statistics/os.html', context )

def arch_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    arch_list = []
    arch_names = []
    search = request.GET.get('search','')
    
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_arch = agents2archlist(database)
    database.disconnect()
    
    arch_id = 0
    for arch_name in agents_per_arch: 
        if arch_name.find(search) != -1 : 
            arch_list.append({'id': arch_id, 'name': arch_name, 'count': agents_per_arch[arch_name] })
            arch_id += 1

    context = Context({'arch_list': arch_list, 'search': search } )
    return render(request, 'statistics/arch.html', context )

def net_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    net4_list = []
    net6_list = []
    search_name = request.GET.get('search_name','')
    search_type = request.GET.get('search_type','ipv4')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
   
    # TODO: Network field missing (db,agent,server fix)
    # TODO: show IP/mask for now... 
    if search_type == 'ipv4':
        sql = "SELECT DISTINCT address,mask FROM ipv4 "
        database.execute(sql)
        result = database.fetchall()
        net4_id = 0 
        for row in result:
            net4_name = row[0]
            net4_mask = row[1]
            sql = "SELECT server_id,address,mask FROM ipv4 WHERE address = '%s' AND mask = '%s' "
            database.execute(sql,(net4_name,net4_mask))
            #net4_count = database.rowcount()
            if net4_name.find(search_name) != -1 :
                net4_list.append({'id': net4_id, 'name': net4_name, 'mask': net4_mask })
            net4_id += 1 

    elif search_type == 'ipv6' :
        sql = "SELECT DISTINCT address,mask FROM ipv6 "
        database.execute(sql)
        result = database.fetchall()
        net6_id = 0 
        for row in result:
            net6_name = row[0]
            net6_mask = row[1]
            sql = "SELECT server_id,address,mask FROM ipv6 WHERE address = '%s' AND mask = '%s' "
            database.execute(sql,(net6_name,net6_mask))
            #net6_count = database.rowcount()
            if net6_name.find(search_name) != -1 :
                net6_list.append({'id': net6_id, 'name': net6_name, 'mask': net6_mask })
            net6_id += 1 

    database.disconnect()
    context = Context({'net4_list': net4_list, 'net6_list': net6_list, 'search_name': search_name, 'search_type': search_type } )
    return render(request, 'statistics/net.html', context )

def software_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    pkg_list = []
    search = request.GET.get('search','')
    
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_pkg = agents2softwarelist(database)
    database.disconnect()
    
    pkg_id = 0
    for pkg_name in agents_per_pkg: 
        if pkg_name.find(search) != -1 : 
            pkg_list.append({'id': pkg_id, 'name': pkg_name, 'count': agents_per_pkg[pkg_name] })
            pkg_id += 1

    context = Context({'pkg_list': pkg_list, 'search': search } )
    return render(request, 'statistics/software.html', context )

def patches_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    patch_list = []
    patch_names = []
    search = request.GET.get('search','')

    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_patch_security = agents2patchlist(database,patchtype='security')
    agents_per_patch_bugfix = agents2patchlist(database,patchtype='bugfix')
    agents_per_patch_improvement = agents2patchlist(database,patchtype='improvement')
    agents_per_patch_other = agents2patchlist(database,patchtype='other')
    database.disconnect()
    
    patch_id = 0
    for patch_name in agents_per_patch_security: 
        if patch_name.find(search) != -1 : 
            patch_list.append({'id': patch_id, 'name': patch_name, 'type': 'security','count': agents_per_patch_security[patch_name] })
            patch_id += 1
    for patch_name in agents_per_patch_bugfix: 
        if patch_name.find(search) != -1 : 
            patch_list.append({'id': patch_id, 'name': patch_name, 'type': 'bugfix','count': agents_per_patch_bugfix[patch_name] })
            patch_id += 1
    for patch_name in agents_per_patch_improvement: 
        if patch_name.find(search) != -1 : 
            patch_list.append({'id': patch_id, 'name': patch_name, 'type': 'improvement','count': agents_per_patch_improvement[patch_name] })
            patch_id += 1
    for patch_name in agents_per_patch_other: 
        if patch_name.find(search) != -1 : 
            patch_list.append({'id': patch_id, 'name': patch_name, 'type': 'other','count': agents_per_patch_other[patch_name] })
            patch_id += 1


    context = Context({'patch_list': patch_list, 'search': search } )
    return render(request, 'statistics/patches.html', context )


def users_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    user_list = []
    search = request.GET.get('search','')
   
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_user = agents2userlist(database)
    database.disconnect()

    user_id = 0
    for name in agents_per_user: 
        if name.find(search) != -1 : 
	    user_list.append({'id': user_id, 'name': name, 'count': agents_per_user[name] })
            user_id += 1


    context = Context({'user_list': user_list, 'search': search } )
    return render(request, 'statistics/users.html', context )

def groups_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser()
    group_list = []
    names = []
    search = request.GET.get('search','')

    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    agents_per_group = agents2grouplist(database)
    database.disconnect()

    group_id = 0
    for name in agents_per_group: 
        if name.find(search) != -1 : 
	    group_list.append({'id': group_id, 'name': name, 'count': agents_per_group[name] })
            group_id += 1


    context = Context({'group_list': group_list, 'search': search } )
    return render(request, 'statistics/groups.html', context )


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
    search_name = request.GET.get('search_name','')
    search_type = request.GET.get('search_type','processor')
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 
    
    if search_type == 'processor':
        sql = "SELECT DISTINCT family,speed,cores,htsystem FROM processor "
        database.execute(sql)
        result = database.fetchall()
        cpu_id = 0 
        for row in result:
            cpu_familly = row[0]
            cpu_speed = row[1]
            cpu_cores = row[2]
            cpu_ht = row[3]
            #if cpu_familly.find(search_name) != -1 :
	    cpu_list.append({'id': cpu_id, 'familly': cpu_familly, 'speed': cpu_speed, 'cores': cpu_cores, 'ht': cpu_ht })
            cpu_id += 1 

    elif search_type == 'memory':
        sql = "SELECT DISTINCT manufacturer,modulesize,speed FROM memorymodule "
        database.execute(sql)
        result = database.fetchall()
        mem_id = 0 
        for row in result:
            mem_manufacturer = row[0]
            mem_modulesize = row[1]
            mem_speed = row[2]
            if mem_manufacturer.find(search_name) != -1 :
                mem_list.append({'id': mem_id, 'manufacturer': mem_manufacturer, 'size': mem_modulesize, 'speed': mem_speed })
            mem_id += 1 

    elif search_type == 'mainboard':
        sql = "SELECT DISTINCT manufacturer,productname,version FROM baseboard "
        database.execute(sql)
        result = database.fetchall()
        board_id = 0 
        for row in result:
            board_manufacturer = row[0]
            board_productname = row[1]
            board_version = row[2]
            if board_productname.find(search_name) != -1 :
                board_list.append({'id': board_id, 'manufacturer': board_manufacturer, 'productname': board_productname, 'version': board_version })
            board_id += 1 

    elif search_type == 'disk':
        sql = "SELECT DISTINCT model,sectors,sectorsize FROM blockdevice "
        database.execute(sql)
        result = database.fetchall()
        disk_id = 0 
        for row in result:
            disk_model = row[0]
            disk_size = str( parser.str2int(row[1]) * parser.str2int(row[2]))
            if disk_model.find(search_name) != -1 :
                disk_list.append({'id': disk_id, 'model': disk_model, 'size': disk_size })
            disk_id += 1 

    elif search_type == 'pcidev':
        sql = "SELECT DISTINCT devtype,vendor,model FROM pcidevice "
        database.execute(sql)
        result = database.fetchall()
        pci_id = 0 
        for row in result:
            pci_type = row[0]
            pci_vendor = row[1]
            pci_model = row[2]
            if pci_model.find(search_name) != -1 :
                pci_list.append({'id': pci_id, 'type': pci_type, 'vendor': pci_vendor, 'model': pci_model })
            pci_id += 1 

    elif search_type == 'firmware':
        sql = "SELECT DISTINCT vendor,version FROM bios "
        database.execute(sql)
        result = database.fetchall()
        bios_id = 0 
        for row in result:
            bios_vendor = row[0]
            bios_version = row[1]
            if bios_vendor.find(search_name) != -1 :
                bios_list.append({'id': bios_id, 'vendor': bios_vendor, 'version': bios_version })
            bios_id += 1 

    database.disconnect()
    context = Context({'cpu_list': cpu_list, 'mem_list': mem_list, 'board_list': board_list, 'disk_list': disk_list, 'pci_list': pci_list, 'bios_list': bios_list, 'search_name': search_name, 'search_type': search_type } )
    return render(request, 'statistics/hardware.html', context )

def dashboard_view(request):
    check_permissions(request)

    cfg = TeddixConfigFile.TeddixConfigFile()
    syslog = TeddixLogger.TeddixLogger("TeddixWeb")
    syslog.open_syslog()
    parser = TeddixParser.TeddixStringParser() 
    database = TeddixDatabase.TeddixDatabase(syslog,cfg) 

    # agent status 
    sql = "SELECT id FROM server WHERE active = 'yes'"
    database.execute(sql)
    active = database.rowcount()

    sql = "SELECT id FROM server WHERE active = 'no'"
    database.execute(sql)
    inactive = database.rowcount()

    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Agent status'
    pie_chart.add('Active', active)
    pie_chart.add('Inactive', inactive)
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-agents.svg')
 
    # OS stats
    agents_per_os = agents2oslist(database)
    
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Operating Systems'
    
    for name in agents_per_os: 
        pie_chart.add(name, agents_per_os[name])
    
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-os.svg')

    # Arch stats
    agents_per_arch = agents2archlist(database)
    
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Architectures'
    
    for name in agents_per_arch: 
        pie_chart.add(name, agents_per_arch[name])
    
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-arch.svg')

    # Available updates 
    bar_chart = pygal.Bar(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    bar_chart.title = 'Available updates'
    
    patches_security = agents2patchlist(database,patchtype='security')
    count = 0
    for name in patches_security: 
        count += 1 
    bar_chart.add('security', count)

    patches_bugfix = agents2patchlist(database,patchtype='bugfix')
    count = 0
    for name in patches_bugfix: 
        count += 1 
    bar_chart.add('bugfix', count)
    
    patches_improvement = agents2patchlist(database,patchtype='improvement')
    count = 0
    for name in patches_improvement: 
        count += 1 
    bar_chart.add('improvement', count) 
    
    patches_other = agents2patchlist(database,patchtype='other')
    count = 0
    for name in patches_other: 
        count += 1 
    bar_chart.add('other', count)

    bar_chart.render_to_file('teddixweb/static/charts/dashboard-patches.svg')
 
    # Update per hosts
    bar_chart = pygal.Bar(width=800, height=400, explicit_size=False,legend_font_size=10, legend_at_bottom=True, style=CleanStyle)
    bar_chart.title = 'Servers to update'
    
    patches_security = agents2patchlist(database,patchtype='security')
    for name in patches_security:
        bar_chart.add(name, patches_security[name])

    patches_bugfix = agents2patchlist(database,patchtype='bugfix')
    for name in patches_bugfix: 
        bar_chart.add(name, patches_bugfix[name])
    
    patches_improvement = agents2patchlist(database,patchtype='improvement')
    for name in patches_improvement: 
        bar_chart.add(name, patches_improvement[name])
    
    patches_other = agents2patchlist(database,patchtype='other')
    for name in patches_other: 
        bar_chart.add(name, patches_other[name])

    bar_chart.render_to_file('teddixweb/static/charts/dashboard-patches2.svg')
   
    # software
    pkgs_per_section = pkgs2sectionlist(database)
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Software type'
    for name in pkgs_per_section: 
        pie_chart.add(name, pkgs_per_section[name])
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-software.svg')


    # Network stats ipv4
    agents_per_net = agents2netlist(database,ntype='ipv4')
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'IPv4 Networks'
    for name in agents_per_net: 
        pie_chart.add(name, agents_per_net[name])
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-networks.svg')
 
    # Network stats ipv6
    agents_per_net = agents2netlist(database,ntype='ipv6')
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'IPv6 Networks'
    for name in agents_per_net: 
        pie_chart.add(name, agents_per_net[name])
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-networks2.svg')
    
    # User type
    users_per_type = users2typelist(database)
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Account type'
    for name in users_per_type: 
        pie_chart.add(name, users_per_type[name])
    #pie_chart.add('System account', 30)
    #pie_chart.add('User account', 10)
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-users-type.svg')

    # locked 
    users_per_status = users2activelist(database)
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Active accounts'
    for name in users_per_status: 
        pie_chart.add(name, users_per_status[name])
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-users-status.svg')

    # hash 
    users_per_hash = users2hashlist(database)
    pie_chart = pygal.Pie(width=400, height=400, explicit_size=False, legend_at_bottom=True, style=CleanStyle)
    pie_chart.title = 'Hash type'
    for name in users_per_hash: 
        pie_chart.add(name, users_per_hash[name])
    pie_chart.render_to_file('teddixweb/static/charts/dashboard-users-hash.svg')
    
    
 
    # patches / trends 
    #line_chart = pygal.StackedLine(width=400, height=400, explicit_size=False, style=CleanStyle,legend_at_bottom=True,fill=True)
    #line_chart.title = 'Available updates'
    #line_chart.x_labels = map(str, range(1, 12))
    #line_chart.add('Security', [None, 0, 5, 16, 25, 31, 36, 45, 46, 42, 37, 45])
    #line_chart.add('Bugfix', [None, 0, 2, 3, 7, 15, 12, 24, 8, 8, 1, 19])
    #line_chart.add('Extra', [None, 0, 5, 16, 12, 15, 17, 7, 3, 6, 36, 4])
    #line_chart.render_to_file('teddixweb/static/charts/dashboard-patches.svg')


    # agent count / trends 

    #line_chart = pygal.StackedLine(width=400, height=400, explicit_size=False, style=CleanStyle,legend_at_bottom=True,fill=True)
    #line_chart.title = 'Agent status'
    #line_chart.x_labels = map(str, range(1, 12))
    #line_chart.add('agents', [None, 0, 5, 16, 25, 31, 36, 45, 46, 42, 37, 45])
    #line_chart.render_to_file('teddixweb/static/charts/dashboard-agents.svg')

    database.disconnect()
    return render(request, 'monitor/dashboard.html')

def notready_view(request):
    check_permissions(request)
    return render(request, 'notready.html' )



def base_view(request):
    check_permissions(request)
    return render(request, 'base.html')


def login(request, *args, **kwargs):
    if request.method == 'POST':
        if not request.POST.get('remember_me', None):
            request.session.set_expiry(1209600) # 2 weeks
    return auth_views.login(request, *args, **kwargs)

