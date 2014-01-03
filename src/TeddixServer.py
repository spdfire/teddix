#!/usr/bin/env python

# Option parser
from optparse import OptionParser

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
            conn = httplib.HTTPSConnection(host, 45003,timeout=30)
            conn.request("GET", request)
            resp = conn.getresponse()
            conn.close()
        except httplib.BadStatusLine:
            self.syslog.info("%s: Agent did not reply in HTTP " % host)
            self.syslog.warn("%s: Unable to parse reply" % host)
            return 

        except Exception, e:
            self.syslog.error("%s: Unable to connect to server" % host)
            self.syslog.exception('make_request(): %s' % e )
            return 

        if resp.status != httplib.OK: 
            self.syslog.info("%s: Wrong HTTP code" % host)
            self.syslog.warn("%s: Unable to parse reply" % host)
        else: 
            self.syslog.debug("%s: Request \"GET %s\" OK " % (host,request))
            data = resp.read()
            return data

    def save_request(self,request,ofile,host):
        self.syslog.debug("%s: Save request in \"%s\" " % (host,ofile))
        # Switch to working directory
        if not os.path.exists(host):
            try:
                os.makedirs(host)
            except Exception, e:
                syslog.error("%s: Unable to create workdir" % host )
                syslog.exception('save_request(): %s' % e )
                exit(20)

        if not os.access(host, os.R_OK):
            syslog.error("workdir %s needs to be readable" % host )
        if not os.access(host, os.W_OK):
            syslog.error("workdir %s needs to be writable" % host)
        if not os.access(host, os.X_OK):
            syslog.error("workdir %s needs to be executable" % host)

        root = xml.fromstring(request)
        b64 = root.find('data').text
        html = base64.b64decode(b64)
        #print html
        outfile = file(host + '/' + ofile, 'w')
        outfile.write(html)
        outfile.close()


    
    def worker_thread(self):
       
        #grabs host from queue
        host = self.queue.get()
        self.syslog.debug("%s: Starting worker " % host )

        # 1. GET /cfg2html 
        req = self.make_request(host,'/cfg2html')
        self.save_request(req,'cfg2html.html',host)

        # 2. GET /ora2html
        req = self.make_request(host,'/ora2html')
        self.save_request(req,'ora2html.html',host)

        # 3. GET /baseline 
        req = self.make_request(host,'/baseline')
        self.save_request(req,'baseline.xml',host)

        self.syslog.debug("%s: Stopping worker" % host )
        self.queue.task_done()


    def create_server(self,syslog,cfg):

        # Start workers
        if cfg.server_workers == None:
            workers = 10
        else: 
            workers = cfg.server_workers

        if cfg.server_refresh == None:
            refresh = "1d"
        else: 
            refresh = cfg.server_refresh
        
        serverlist = cfg.server_serverlist
            
        self.queue = Queue.Queue()
        self.terminate = False 
            
        syslog.info("main: Entering Server loop" )
        while not self.terminate:
            # start scheduler
            # on scheduled time: 
            #  - read file & create queue 

            #populate queue with data
            syslog.info("main: Started queue run" )

            try: 
                f = open(serverlist, 'r')
            except Exception, e:
                syslog.error("main: Unable to open: %s " % serverlist)
                syslog.exception('__init__(): %s' % e )
                exit(20)

            for host in f:
                while (threading.active_count() > workers) and (not self.terminate): 
                    syslog.debug('main: Reached max active workers count (%d): sleeping...' % threading.active_count())
                    time.sleep(60)
                
                if not self.terminate:
                    t = threading.Thread(target=self.worker_thread)
                    t.setDaemon(1)
                    t.start()

                    self.queue.put(host.strip())

            f.close()
            syslog.info("main: Finished queue run" )

            # wait for all workers to finish their job 
            #Join all existing threads to main thread.
            if threading.active_count() > 1: 
                syslog.debug('main: Waiting for other threads. ')
            while (threading.active_count() > 1) and (not self.terminate):
                time.sleep(1)

            if not self.terminate:
                syslog.info("main: Sleeping for %s " % refresh )
                time.sleep(self.convert_to_seconds(refresh))

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

        # Stop TCP server
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


