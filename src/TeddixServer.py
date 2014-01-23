#!/usr/bin/env python

# Option parser
from optparse import OptionParser

# XML parsing
import xml.etree.ElementTree as xml
import base64

# Daemon
import threading
import Queue
import daemon
import time
import sys
import pwd
import grp
import os
import re

# TCP client 
import httplib
import socket

# Signals
import signal

# Pidfile
try:
    from daemon.pidfile import TimeoutPIDLockFile
except (AttributeError,ImportError):
    try:
        from daemon.pidlockfile import TimeoutPIDLockFile
    except (AttributeError,ImportError):
        raise


# Set python module dir
sys.path.append('@pythondir@' + '/teddix')
#sys.path.append('/usr/lib/python2.7/site-packages' + '/teddix')

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile

# Teddix Baseline
import TeddixInventory

# SQL Database
import TeddixDatabase



class TeddixServer:
    # Signal handlers
    def sig_handler(self,signum, stackframe):
        if signum == signal.SIGTERM:
            self.syslog.warn("SIGTERM caught - Shutting down TeddixServer ")
            self.terminate = True
        elif signum == signal.SIGINT:
            self.syslog.warn("SIGINT caught - Shutting down TeddixServer ")
            self.terminate = True
        elif signum == signal.SIGHUP:
            self.syslog.info("SIGHUP caught - TODO: reload config file ")
        elif signum == signal.SIGUSR1:
            self.syslog.info("SIGUSR1 caught - ignoring ")
        elif signum == signal.SIGUSR2:
            self.syslog.info("SIGUSR2 caught - ignoring ")

    def print_time(self):
        self.syslog.debug("Time: " )

    def convert_to_seconds(self,s):
        s = s.strip()
        s = s.lower()
        seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800, "y": 31556926 }
        return int(s[:-1]) * seconds_per_unit[s[-1]]

    def make_request(self,host,request):
        self.syslog.debug("%s: Make request \"GET %s\" " % (host,request))
        try:
            conn = httplib.HTTPSConnection(host, 45003,timeout=600)
            conn.request("GET", request)
            resp = conn.getresponse()
            conn.close()
        except httplib.BadStatusLine:
            self.syslog.info("%s: Agent did not reply in HTTP " % host)
            self.syslog.warn("%s: Unable to parse reply" % host)
            return 

        except Exception, e:
            self.syslog.warn("%s: Unable to connect to server" % host)
            # self.syslog.exception('make_request(): %s' % e )
            return 

        if resp.status != httplib.OK: 
            self.syslog.info("%s: Wrong HTTP code" % host)
            self.syslog.warn("%s: Unable to parse reply" % host)
        else: 
            self.syslog.debug("%s: Request \"GET %s\" OK " % (host,request))
            data = resp.read()
            return data

    def parse_reply(self,host,msg):
        root = xml.fromstring(msg)
        if root.get('version') != '2.0':
            self.syslog.warn("%s: Unknown message protocol version" % host)
            return None
        if root.get('program') != 'teddix':
            self.syslog.warn("%s: Unknown message " % host)
            return None
        if root.get('type') != 'reply':
            self.syslog.warn("%s: Unknown message " % host)
            return None
       
        reply = root.find('reply')
        request = reply.find('request').text
        
        if reply.find('code').text != '200': 
            result = reply.find('result').text
            info = reply.find('info').text
            code = reply.find('code').text
            self.syslog.warn("%s: server error: %s(code: %s) info: %s " % (host,result,code,info) )
            return None

        data = reply.find('data')
        return data
        

    def save_dbbaseline(self,database,host,baseline):
        self.syslog.debug("%s: Save baseline " % (host))

        # Get server ID 
        sql = "SELECT id FROM server WHERE LOWER(name) = \"%s\" " % host 
        database.execute(sql)
        result = database.fetchall()
        server_id = '' 
        for row in result:
            server_id = row[0] 
        
        #TODO: check if only one record is returned, rollback if req 
        if database.rowcount() > 1: 
            self.syslog.warn("SQL Duplicate IDs for server %s " % host)

        syslog.debug("SQL result: server %s have ID %s " % (host,server_id))

        # save baseline 
        b_hostname = baseline.find('server').find('host').get('name')
        b_program = baseline.find('server').find('generated').get('program')
        b_scantime = baseline.find('server').find('generated').get('scantime')
        b_version = baseline.find('server').find('generated').get('version')

        sql  = "INSERT INTO baseline(server_id,hostname,program,scantime,version) "
        sql += "VALUES(%s,\"%s\",\"%s\",\"%s\",\"%s\")" 
        sql = sql % (server_id,b_hostname,b_program,b_scantime,b_version)
        database.execute(sql)
        baseline_id = database.insert_id()

        # save HW info
        hardware = baseline.find('server').find('hardware')

        boardtype = hardware.find('sysboard').get('boardtype')
        serialnumber = hardware.find('sysboard').get('serialnumber')
        manufacturer = hardware.find('sysboard').get('manufacturer')
        productname = hardware.find('sysboard').get('productname')

        sql  = "INSERT INTO sysboard(server_id,baseline_id,boardtype,serialnumber,manufacturer,productname) "
        sql += "VALUES(%s,%s,\"%s\",\"%s\",\"%s\",\"%s\")" 
        sql = sql % (server_id,baseline_id,boardtype,serialnumber,manufacturer,productname)
        database.execute(sql)

        # Processors 
        root = hardware.find('processors')
        for child in root:
            cores = child.get('cores')
            extclock = child.get('extclock')
            familly = child.get('familly')
            htsystem = child.get('htsystem')
            procid = child.get('procid')
            partnumber = child.get('partnumber')
            serialnumber = child.get('serialnumber')
            clock = child.get('clock')
            threads = child.get('threads')
            proctype = child.get('proctype')
            procversion = child.get('procversion')
            sql  = "INSERT INTO processor(server_id,baseline_id,cores,extclock,familly,htsystem,procid,partnumber,serialnumber,clock,threads,proctype,procversion) "
            sql += "VALUES(%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,cores,extclock,familly,htsystem,procid,partnumber,serialnumber,clock,threads,proctype,procversion)
            database.execute(sql)


        # RAM modules 
        root = hardware.find('memory')
        for child in root:
            bank = child.get('bank')
            formfactor = child.get('formfactor')
            location = child.get('location')
            manufacturer = child.get('manufacturer')
            memorytype = child.get('memorytype')
            partnumber = child.get('partnumber')
            serialnumber = child.get('serialnumber')
            modulesize = child.get('modulesize')
            width = child.get('width')
            sql  = "INSERT INTO memorymodule(server_id,baseline_id,bank,formfactor,location,manufacturer,memorytype,partnumber,serialnumber,modulesize,width) "
            sql += "VALUES(%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,bank,formfactor,location,manufacturer,memorytype,partnumber,serialnumber,modulesize,width)
            database.execute(sql)


        # firmware  
        releasedate = hardware.find('bios').get('releasedate')
        vendor = hardware.find('bios').get('vendor')
        version = hardware.find('bios').get('version')
        sql  = "INSERT INTO bios(server_id,baseline_id,releasedate,vendor,version) "
        sql += "VALUES(%s,%s,\"%s\",\"%s\",\"%s\")" 
        sql = sql % (server_id,baseline_id,releasedate,vendor,version)
        database.execute(sql)

        # save OS info
        system = baseline.find('server').find('system')
        arch = system.get('arch')
        detail = system.get('detail')
        kernel = system.get('kernel')
        manufacturer = system.get('manufacturer')
        name = system.get('name')
        serialnumber = system.get('serialnumber')
        sql  = "INSERT INTO system(server_id,baseline_id,arch,detail,kernel,manufacturer,name,serialnumber) "
        sql += "VALUES(%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
        sql = sql % (server_id,baseline_id,arch,detail,kernel,manufacturer,name,serialnumber)
        database.execute(sql)
        system_id = database.insert_id()


        # packages 
        root = system.find('software')
        for child in root:
            description = child.get('description')
            files = child.get('files')
            homepage = child.get('homepage')
            name = child.get('name')
            pkgsize = child.get('pkgsize')
            section = child.get('section')
            signed = child.get('signed')
            installedsize = child.get('installedsize')
            status = child.get('status')
            version = child.get('version')
            sql  = "INSERT INTO package(server_id,baseline_id,system_id,description,files,homepage,name,pkgsize,section,signed,installedsize,status,version) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,description,files,homepage,name,pkgsize,section,signed,installedsize,status,version)
            database.execute(sql)

        # filesystems 
        root = system.find('filesystems')
        for child in root:
            device = child.get('device')
            fstype = child.get('fstype')
            fsfree = child.get('fsfree')
            name = child.get('name')
            fssize = child.get('fssize')
            fsused = child.get('fsused')
            sql  = "INSERT INTO filesystem(server_id,baseline_id,system_id,device,fstype,fsfree,name,fssize,fsused) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,device,fstype,fsfree,name,fssize,fsused)
            database.execute(sql)

        # swap devices 
        root = system.find('swap')
        for child in root:
            device = child.get('device')
            swapfree = child.get('swapfree')
            swapsize = child.get('swapsize')
            swaptype = child.get('swaptype')
            swapused = child.get('swapused')
            sql  = "INSERT INTO swap(server_id,baseline_id,system_id,device,swapfree,swapsize,swaptype,swapused) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,device,swapfree,swapsize,swaptype,swapused)
            database.execute(sql)

        # XXX
        # NETWORK STUFF
        # XXX

        # groups 
        root = system.find('groups')
        for child in root:
            name = child.get('name')
            sql  = "INSERT INTO sysgroup(server_id,baseline_id,system_id,name) "
            sql += "VALUES(%s,%s,%s,\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,name)
            database.execute(sql)

        # users
        root = system.find('users')
        for child in root:
            expire = child.get('expire')
            destination = child.get('destination')
            gid = child.get('gid')
            groups = child.get('groups')
            hashtype = child.get('hashtype')
            home = child.get('home')
            locked = child.get('locked')
            login = child.get('login')
            shell = child.get('shell')
            uid = child.get('uid')
            sql  = "INSERT INTO sysuser(server_id,baseline_id,system_id,expire,destination,gid,groups,hashtype,home,locked,login,shell,uid) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,expire,destination,gid,groups,hashtype,home,locked,login,shell,uid)
            database.execute(sql)

        # language 
        timezone = system.find('regional').get('timezone')
        charset = system.find('regional').get('charset')
        sql  = "INSERT INTO regional(server_id,baseline_id,system_id,timezone,charset) "
        sql += "VALUES(%s,%s,%s,\"%s\",\"%s\")" 
        sql = sql % (server_id,baseline_id,system_id,timezone,charset)
        database.execute(sql)

        # process list
        root = system.find('processes')
        for child in root:
            command = child.get('command')
            cputime = child.get('cputime')
            owner = child.get('owner')
            pcpu = child.get('pcpu')
            pid = child.get('pid')
            pmemory = child.get('pmemory')
            priority = child.get('priority')
            sharedsize = child.get('sharedsize')
            virtsize = child.get('virtsize')
            sql  = "INSERT INTO process(server_id,baseline_id,system_id,command,cputime,owner,pcpu,pid,pmemory,priority,sharedsize,virtsize) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,command,cputime,owner,pcpu,pid,pmemory,priority,sharedsize,virtsize)
            database.execute(sql)

        # services
        root = system.find('services')
        for child in root:
            autostart = child.get('autostart')
            name = child.get('name')
            running = child.get('running')
            sql  = "INSERT INTO service(server_id,baseline_id,system_id,autostart,name,running) "
            sql += "VALUES(%s,%s,%s,\"%s\",\"%s\",\"%s\")" 
            sql = sql % (server_id,baseline_id,system_id,autostart,name,running)
            database.execute(sql)




 
    def save_dbextra(self,database,host,cfg2html,ora2html):
        self.syslog.debug("%s: Save in database " % (host))

        # Get server ID 
        sql = "SELECT id FROM server WHERE LOWER(name) = \"%s\" " % host 
        database.execute(sql)
        result = database.fetchall()
        server_id = '' 
        for row in result:
            server_id = row[0] 
        
        #TODO: check if only one record is returned, rollback if req 
        if database.rowcount() > 1: 
            self.syslog.warn("SQL Duplicate IDs for server %s " % host)

        syslog.debug("SQL result: server %s have ID %s " % (host,server_id))

        sql  = "INSERT INTO extra(server_id,created,cfg2html,ora2html) "
        sql += "VALUES(%s,CURDATE(),\"%s\",\"%s\")" 
        sql = sql % (server_id,cfg2html,ora2html)
        database.execute(sql)
       
   
    
    def worker_thread(self):
       
        #grabs host from queue
        host = self.queue.get()
        self.syslog.debug("%s: Starting worker " % host )

        # 1. GET /cfg2html 
        cfg2html = self.make_request(host,'/cfg2html')

        # 2. GET /ora2html
        ora2html = self.make_request(host,'/ora2html')

        # 3. GET /baseline 
        baseline = self.make_request(host,'/baseline')

        # 4. Insert report to Database
        if cfg2html == None and ora2html == None and baseline == None:
            self.syslog.debug("%s: Agent is not responding" % host )
        else:
            # 4.1 Insert baseline report to database
            data = self.parse_reply(host,baseline)
            if data == None: 
                self.syslog.warn("%s: Unable to parse reply" % host )

            else: 
                baseline = data.find('baseline')

            # 4.2 Insert cfg2html report to database
            data = self.parse_reply(host,cfg2html)
            if data == None: 
                self.syslog.warn("%s: Unable to parse reply" % host )

            else: 
                cfg2html = data.find('cfg2html')

            # 4.3 Insert ora2html report to database
            data = self.parse_reply(host,ora2html)
            if data == None: 
                self.syslog.warn("%s: Unable to parse reply" % host )

            else: 
                ora2html = data.find('ora2html')

            # keep it in b64
            if cfg2html != None and ora2html != None: 
                cfg2html_b64 = cfg2html.text
                ora2html_b64 = ora2html.text

                # TODO: filter input (SQLi etc.)
                database = TeddixDatabase.TeddixDatabase(syslog,cfg)
                self.save_dbextra(database,host,cfg2html_b64,ora2html_b64)
                self.save_dbbaseline(database,host,baseline)
                database.commit()
                database.disconnect()

        self.syslog.debug("%s: Stopping worker" % host)
        self.queue.task_done()


    def create_server(self,syslog,cfg):
        
        self.terminate = False 
        self.queue = Queue.Queue()
             
        try: 
            f = open(cfg.server_serverlist, 'r')
        except Exception, e:
            self.syslog.error("main: Unable to open: %s " % cfg.server_serverlist)
            self.syslog.exception('create_server(): %s' % e )
            exit(20)

        # find duplicates in server_list 
        seen = set()
        line_number = 0
        for line in f:
            line_number += 1  
            line = line.strip()
            line = line.lower()
            if line in seen:
                self.syslog.error("main: duplicate entry: %s on line: %d " % (line,line_number))
                exit(21)
            else:
                seen.add(line)

        # Connect to Database 
        database = TeddixDatabase.TeddixDatabase(syslog,cfg);
        database.execute("SELECT VERSION();")
 
       
        f.seek(0)
        # keep hostlist in sync to DB
        self.syslog.info("main: Checking database integrity ")
        for host in f:
            if not self.terminate: 
                host = host.strip()
                host = host.lower()
                sql = "SELECT id FROM server WHERE LOWER(name) = \"%s\" " % host 
                database.execute(sql)
                count = database.rowcount() 
                
                # TODO: Not working for some reason count == 0 
                self.syslog.info("SQL count = (%s) " % count)
                if count < 1:
                    self.syslog.info("SQL adding new host(%s) to database" % host)
                    sql = "INSERT INTO server(name,created) VALUES (\"%s\",NOW()); " % host 
                    database.execute(sql)
                    database.commit()

                if count > 1: 
                    self.syslog.warn("SQL Cleaning duplicate server names %s " % host)
                    result = database.fetchall()
                    for row in result:
                        server_id = row[0]
                        sql = "DELETE FROM extra WHERE server_id = %s " % server_id 
                        database.execute(sql)
                        sql = "DELETE FROM baseline WHERE server_id = %s " % server_id 
                        database.execute(sql)
                        sql = "DELETE FROM server WHERE id = \"%s\" " % server_id
                        database.execute(sql)

                    sql = "INSERT INTO server(name,created) VALUES (\"%s\",NOW()); " % host 
                    database.execute(sql)
                    database.commit()

        database.disconnect()
        f.close()
    
        syslog.info("main: Entering Server loop" )
        while not self.terminate:
            # start scheduler
            # on scheduled time: 
            #  - read file & create queue 

            #populate queue with data
            syslog.info("main: Started queue run" )

            try: 
                f = open(cfg.server_serverlist, 'r')
            except Exception, e:
                syslog.error("main: Unable to open: %s " % cfg.server_serverlist)
                syslog.exception('create_server(): %s' % e )
                exit(20)

            for host in f:
                if (threading.active_count() > cfg.server_workers) and (not self.terminate): 
                    syslog.debug('main: Reached max active workers count (%d): sleeping ...' % (threading.active_count() -1) )
                while (threading.active_count() > cfg.server_workers) and (not self.terminate): 
                    time.sleep(1)
                
                if not self.terminate:
                    t = threading.Thread(target=self.worker_thread)
                    t.setDaemon(1)
                    t.start()

                    host = host.strip()
                    host = host.lower()
                    self.queue.put(host)

            f.close()
            syslog.info("main: Finished queue run" )

            # wait for all workers to finish their job 
            #Join all existing threads to main thread.
            if threading.active_count() > 1: 
                syslog.debug('main: Waiting for other threads. ')
            while (threading.active_count() > 1) and (not self.terminate):
                time.sleep(1)

            if not self.terminate:
                syslog.info("main: Sleeping for %s " % cfg.server_refresh )
                time.sleep(self.convert_to_seconds(cfg.server_refresh))

        # wait for process to finish their job 
        if threading.active_count() > 1: 
            syslog.debug('main: waiting 30s for remaining %d workers' % (threading.active_count()-1))
            time.sleep(30)
        
        # if there are any workers left, teminate them.
        if threading.active_count() > 1: 
            syslog.info('main: Terminating remaining workers. ')
        for thread in threading.enumerate():
                if thread is not threading.currentThread():
                    syslog.info('main: TODO: killing workerX ')
                    #thread.kill()

        # Stop server
        syslog.info("main: Stopping TeddixServer")


    def __init__(self,syslog,cfg,type="daemon"):
        self.syslog = syslog

        # Switch to working directory
        if not os.path.exists(cfg.global_workdir + '/server'):
            try:
                os.makedirs(cfg.global_workdir + '/server')
            except Exception, e:
                syslog.error("Unable to create workdir: %s " % cfg.global_workdir + '/server' )
                syslog.exception('__init__(): %s' % e )
                exit(20)

        try:
            os.chdir(cfg.global_workdir + '/server')
        except Exception, e:
            syslog.error("Unable to change workdir to %s " % cfg.global_workdir + '/server')
            syslog.exception('__init__(): %s' % e )
            exit(20)

        if not os.access(cfg.global_workdir + '/server', os.R_OK):
            syslog.error("workdir %s needs to be readable" % cfg.global_workdir+ '/server' )
        if not os.access(cfg.global_workdir + '/server', os.W_OK):
            syslog.error("workdir %s needs to be writable" % cfg.global_workdir + '/server')
        if not os.access(cfg.global_workdir + '/server', os.X_OK):
            syslog.error("workdir %s needs to be executable" % cfg.global_workdir + '/server')


        # Start TeddixServer
        if type.lower() == "daemon":
            syslog.info("Starting TeddixServer (@VERSION@) in background " )
            try:
                pw_user = pwd.getpwnam(cfg.server_user)
                pw_group = grp.getgrnam(cfg.server_group)
            except Exception, e:
                syslog.error("user %s or group %s does not exists " % (cfg.server_user,cfg.server_group))
                syslog.exception('__init__(): %s' % e )
                exit(20)

            # Daemon Configuration
            self.TeddixDaemonContext = daemon.DaemonContext(
                working_directory=cfg.global_workdir + '/server',
#                pidfile=lockfile.pidlockfile.PIDLockFile(cfg.agent_pidfile),
                pidfile=TimeoutPIDLockFile(cfg.server_pidfile),
                umask=0o007,
                detach_process=True,
                uid=pw_user[3],
                gid=pw_group[2],
            )

            self.TeddixDaemonContext.signal_map = {
                signal.SIGUSR1: self.sig_handler,
                signal.SIGUSR2: self.sig_handler,
                signal.SIGHUP: self.sig_handler,
                signal.SIGINT: self.sig_handler,
                signal.SIGTERM: self.sig_handler,
            }

            # Start daemon
            try:
                self.TeddixDaemonContext.open()
            except Exception, e:
                syslog.error("Unable to daemonize ")
                syslog.exception('__init__(): %s' % e )
                exit(20)

            self.create_server(syslog,cfg)
            self.TeddixDaemonContext.close()
        else:
            syslog.info("Starting TeddixServer (@VERSION@) in foreground " )

            # Setup sig handlers
            signal.signal(signal.SIGUSR1, self.sig_handler)
            signal.signal(signal.SIGUSR2, self.sig_handler)
            signal.signal(signal.SIGHUP, self.sig_handler)
            signal.signal(signal.SIGINT, self.sig_handler)
            signal.signal(signal.SIGTERM, self.sig_handler)
            self.create_server(syslog,cfg)




def parse_opts():

    # Parse command line args
    parser = OptionParser ()
    parser.add_option ("-c", "--config",
                    action = "store",
                    dest = "configfile",
                    help = "Read configuration FILE")
    parser.add_option ("-f", "--foreground",
                    action = "store_true",
                    dest = "foreground",
                    default=False,
                    help = "Do not demonize")
    opts = parser.parse_args()
    return opts


if __name__ == "__main__":

    # Handle command line args
    (opts, args) = parse_opts()

    # Parse config file
    if opts.configfile is None:
        cfg = TeddixConfigFile.TeddixConfigFile()
    else:
        cfg = TeddixConfigFile.TeddixConfigFile(opts.configfile)

    # Open syslog
    syslog = TeddixLogger.TeddixLogger ("TeddixServer")

    if opts.foreground:
        syslog.open_console()
    else:
        if cfg.global_logging.lower() == "syslog":
            syslog.open_syslog()
        if cfg.global_logging.lower() == "file":
            syslog.open_logfile(cfg.global_logfile)

    syslog.info("Logging subsystem initialized")

    # Check if Script is started as root
    if os.geteuid() != 0:
        syslog.critical("TeddixServer should be started by root")

    # Create Server
    if opts.foreground:
        agent = TeddixServer(syslog,cfg,"nodaemon");
    else:
        agent = TeddixServer(syslog,cfg,"daemon");


