#!/usr/bin/env python

# Option parser
from optparse import OptionParser

# TCPServer
import ssl
import Queue
import socket
import base64
import threading
import SocketServer
import BaseHTTPServer

# Daemon
import subprocess
import inspect
import daemon
import time
import sys
import pwd
import grp
import os

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

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile

# Teddix Baseline
import TeddixInventory

# Default error message template
TEDDIX_ERROR_MESSAGE = """\
<reply>
    <type>ERROR</type>
    <code>%(code)d</code>
    <message>Message: %(message)s</message>
    <data>Error code explanation: %(code)s = %(explain)s</data>
</reply>
"""

TEDDIX_DEFAULT_MESSAGE = """\
<reply>
    <type>SUCCESS</type>
    <code>%(code)d</code>
    <message>Message: %(message)s</message>
    <data>%(data)s</data>
</reply>
"""

TEDDIX_ERROR_CONTENT_TYPE = "text/xml"
TEDDIX_DEFAULT_CONTENT_TYPE = "text/xml"


class TeddixTCPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):

    def send_message(self, code=200, message=None, data=None):
        try:
            short, long = self.responses[code]
        except KeyError:
            short, long = '???', '???'
        if message is None:
            message = short
        explain = long
        # self.log_error("code %d, message %s", code, message)
        content = (self.default_message_format % {'code': code, 'message': message, 'data': data })
        
        self.send_response(code, message)
        self.send_header("Content-Type", self.default_content_type)
        self.send_header('Connection', 'close')
        self.end_headers()
        if self.command != 'HEAD' and code >= 200 and code not in (204, 304):
            self.wfile.write(content)


    def do_GET(self):
        # TODO: remove thread synchronization 
        if self.path == '/cfg2html':
            self.syslog.info("Generating /cfg2html")
            self.lock.acquire()
            try:
                cfg2html = TeddixInventory.TeddixCfg2Html(self.syslog,self.cfg)
                cfg2html.run()
                html = base64.b64encode(cfg2html.create_html())
                self.send_message(200,"Request successful",html)
                self.syslog.info("%s: /cfg2html request sent" % self.address_string())
                self.lock.release()
            except Exception, e:
                self.syslog.warn("%s: /cfg2html request failed" % self.address_string())
                self.syslog.debug("do_GET() %s " % e)
                self.lock.release()

        elif self.path == '/ora2html':
            self.syslog.info("Generating /ora2html")
            self.lock.acquire()
            try:
                ora2html = TeddixInventory.TeddixOra2Html(self.syslog,self.cfg)
                ora2html.run()
                html = base64.b64encode(ora2html.create_html())
                self.send_message(200,"Request successful",html)
                self.syslog.info("%s: /ora2html request sent" % self.address_string())
                self.lock.release()
            except Exception, e:
                self.syslog.warn("%s: /ora2html request failed" % self.address_string())
                self.syslog.debug("do_GET() %s " % e)
                self.lock.release()

        elif self.path == '/baseline':
            self.syslog.info("Generating /baseline")
            self.lock.acquire()
            try:
                baseline = TeddixInventory.TeddixBaseline(self.syslog,self.cfg)
                xml = base64.b64encode(baseline.create_xml())
                self.send_message(200,"Request successful",xml)
                self.syslog.info("%s: /baseline request sent" % self.address_string())
                self.lock.release()
            except Exception, e:
                self.syslog.warn("%s: /baseline request failed" % self.address_string())
                self.syslog.debug("do_GET() %s " % e)
                self.lock.release()

        else:
            self.send_error(501, "Unsupported location (%s)" % self.path)
            self.syslog.warn("Unsupported request from %s" % self.address_string())

    def setup(self):
        self.syslog = self.server.syslog
        self.cfg = self.server.cfg
        self.lock = self.server.lock
        self.timeout = 30

        self.error_message_format = TEDDIX_ERROR_MESSAGE
        self.error_content_type = TEDDIX_ERROR_CONTENT_TYPE

        self.default_message_format = TEDDIX_DEFAULT_MESSAGE
        self.default_content_type = TEDDIX_DEFAULT_CONTENT_TYPE
        
        self.server_version = "Teddix/2.0"
        self.sys_version = "Python/" + sys.version.split()[0] + ' (BaseHTTP/' +  BaseHTTPServer.__version__ +')'

        return BaseHTTPServer.BaseHTTPRequestHandler.setup(self)

    def handle(self):
        self.syslog.info("Connection from %s" % self.address_string() )
        return BaseHTTPServer.BaseHTTPRequestHandler.handle(self)

    def finish(self):
        return BaseHTTPServer.BaseHTTPRequestHandler.finish(self)
    
    def log_request(self, code='-', size='-'):
        self.log_message('request: "%s", size: %s, code: %s',
                         self.requestline, str(size), str(code))

    def log_error(self, format, *args):
        self.log_message(format, *args)

    def log_message(self, format, *args):
        self.syslog.debug("%s: \"%s\"" % (self.address_string(), format%args))

    def address_string(self):
        host, port = self.client_address[:2]
        return str(host)



class TeddixTCPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    numThreads = 10
    terminate = False

    def __init__(self, syslog, cfg, server_address, threads=10):
        self.syslog = syslog
        self.cfg = cfg
        self.numThreads = threads
        self.lock = threading.Lock()

        try:
            BaseHTTPServer.HTTPServer.__init__(self, server_address, TeddixTCPRequestHandler, bind_and_activate=False)
            self.allow_reuse_address = 1

            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket = s
            self.socket = ssl.wrap_socket (s, server_side=True, certfile=cfg.agent_crtfile, keyfile=cfg.agent_keyfile)

            self.server_bind()
            self.server_activate()
        except Exception, e:
            syslog.exception('TeddixTCPServer:__init__(): %s' % e )
            return 255
        return


    def serve_forever(self,workers=10):
        # setup the threadpool
        self.numThreads = workers
        self.requests = Queue.Queue(self.numThreads)


        for x in range(self.numThreads):
            t = threading.Thread(target = self.process_request_thread)
            t.setDaemon(1)
            t.start()

        # server main loop
        while not self.terminate:
            self.handle_request()

        self.server_close()

    def process_request_thread(self):
        while not self.terminate:
            SocketServer.ThreadingMixIn.process_request_thread(self, *self.requests.get())

    def handle_request(self):
        try:
            request, client_address = self.get_request()
        except socket.error:
            return
        if self.verify_request(request, client_address):
            self.requests.put((request, client_address))


class TeddixAgent:
    # Signal handlers
    def sig_handler(self,signum, stackframe):
        if signum == signal.SIGTERM:
            self.syslog.warn("SIGTERM caught - Shutting down TeddixAgent ")
            self.tcpserver.terminate = True
        elif signum == signal.SIGINT:
            self.syslog.warn("SIGINT caught - Shutting down TeddixAgent ")
            self.tcpserver.terminate = True
        elif signum == signal.SIGHUP:
            self.syslog.info("SIGHUP caught - TODO: reload config file ")
        elif signum == signal.SIGUSR1:
            self.syslog.info("SIGUSR1 caught - ignoring ")
        elif signum == signal.SIGUSR2:
            self.syslog.info("SIGUSR2 caught - ignoring ")

    def create_agent(self,syslog,cfg):

        # Start TCP server
        try:
            tcpserver = TeddixTCPServer(syslog, cfg, (cfg.agent_listen, cfg.agent_port))
            self.tcpserver = tcpserver
            ip, port = tcpserver.server_address
            syslog.info("TeddixAgent is listening at %s:%d" % (ip,port))
        except Exception, e:
            syslog.error("TeddixAgent unable to listen on %s:%d" % (cfg.agent_listen,cfg.agent_port))
            syslog.exception('create_agent(): %s' % e )
            return 255

        # Start workers
        if cfg.agent_workers == None:
            workers = 10
        else: 
            workers = cfg.agent_workers 

        syslog.info("Starting %d workers" % workers)
        syslog.info("Entering accept loop" )
        tcpserver.serve_forever(workers)

        # Stop TCP server
        syslog.info("Stopping TeddixAgent")
        #tcpserver.shutdown()


    def __init__(self,syslog,cfg,type="daemon"):
        self.syslog = syslog

        # Switch to working directory
        if not os.path.exists(cfg.global_workdir + '/agent'):
            try:
                os.makedirs(cfg.global_workdir + '/agent')
            except Exception, e:
                syslog.error("Unable to create workdir: %s " % cfg.global_workdir + '/agent' )
                syslog.exception('__init__(): %s' % e )
                exit(20)

        try:
            os.chdir(cfg.global_workdir + '/agent')
        except Exception, e:
            syslog.error("Unable to change workdir to %s " % cfg.global_workdir + '/agent')
            syslog.exception('__init__(): %s' % e )
            exit(20)

        if not os.access(cfg.global_workdir + '/agent', os.R_OK):
            syslog.error("workdir %s needs to be readable" % cfg.global_workdir+ '/agent' )
        if not os.access(cfg.global_workdir + '/agent', os.W_OK):
            syslog.error("workdir %s needs to be writable" % cfg.global_workdir + '/agent')
        if not os.access(cfg.global_workdir + '/agent', os.X_OK):
            syslog.error("workdir %s needs to be executable" % cfg.global_workdir + '/agent')


        # Start TeddixAgent
        if type.lower() == "daemon":
            syslog.info("Starting TeddixAgent (@VERSION@) in background " )
            try:
                pw_user = pwd.getpwnam(cfg.agent_user)
                pw_group = grp.getgrnam(cfg.agent_group)
            except Exception, e:
                syslog.error("user %s or group %s does not exists " % (cfg.agent_user,cfg.agent_group))
                syslog.exception('__init__(): %s' % e )
                exit(20)

            # Daemon Configuration

            self.TeddixDaemonContext = daemon.DaemonContext(
                working_directory=cfg.global_workdir + '/agent',
#                pidfile=lockfile.pidlockfile.PIDLockFile(cfg.agent_pidfile),
                pidfile=TimeoutPIDLockFile(cfg.agent_pidfile),
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

            self.create_agent(syslog,cfg)
            self.TeddixDaemonContext.close()
        else:
            syslog.info("Starting TeddixAgent (@VERSION@) in foreground " )

            # Setup sig handlers
            signal.signal(signal.SIGUSR1, self.sig_handler)
            signal.signal(signal.SIGUSR2, self.sig_handler)
            signal.signal(signal.SIGHUP, self.sig_handler)
            signal.signal(signal.SIGINT, self.sig_handler)
            signal.signal(signal.SIGTERM, self.sig_handler)
            self.create_agent(syslog,cfg)


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
    syslog = TeddixLogger.TeddixLogger ("TeddixAgent")

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
        syslog.critical("TeddixAgent should be started by root")

    # check if cert is readable 
    if not os.access(cfg.agent_crtfile, os.R_OK):
        syslog.critical("unable to open certificate file: %s " % cfg.agent_crtfile )
    if not os.access(cfg.agent_keyfile, os.R_OK):
        syslog.critical("unable to open key file: %s " % cfg.agent_keyfile )

    # Create Agent
    if opts.foreground:
        agent = TeddixAgent(syslog,cfg,"nodaemon");
    else:
        agent = TeddixAgent(syslog,cfg,"daemon");


