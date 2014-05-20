#!/usr/bin/env python

import os
import platform
import ConfigParser

# teddix parser 
import TeddixParser

class TeddixConfigFile ():
    global_hostname    = platform.node()
    global_logging     = "syslog"
    global_loglevel    = "info"
    global_logfacility = "daemon"
    global_logfile     = "/var/log/teddix.log"
    global_workdir     = "/var/lib/teddix"

    agent_listen      = "0.0.0.0"
    agent_port        = 45003
    agent_user        = "root"
    agent_group       = "root"
    agent_workers     = 10
    agent_crtfile     = "/etc/teddix/agent.crt"
    agent_keyfile     = "/etc/teddix/agent.key"
    agent_pidfile     = "/var/run/teddix-agent.pid"
    agent_cfg2html    = "cfg2html"
    agent_ora2html    = "ora2html"

    server_user       = "root"
    server_group      = "root"
    server_workers    = 10
    server_refresh    = "1d"
    server_pidfile    = "/var/run/teddix-server.pid"
    server_dbtype     = "mysql"
    server_dbhost     = "localhost"
    server_dbport     = 3306
    server_dbuser     = "teddix"
    server_dbpass     = "test123"
    server_dbname     = "teddix"

    def __init__ (self,config=None):

        parser = ConfigParser.ConfigParser()

        if config is None:
            config = "/etc/teddix/teddix.conf"

        if not os.path.exists(config):
            print "Unable to open %s config file!" % config
            exit(1)

        try:
            parser.read(config)
        except:
            print "Unable to open %s config file!" % config
            raise

        # Parse options
        try:
            parser.has_section('global')
            parser.has_section('agent')
            parser.has_section('server')
        except:
            print "Error parsing %s: required sections not found!" % config
            raise

        try:
            if parser.has_option('global','hostname'):
                self.global_logging    = parser.get('global','hostname').strip()
            if parser.has_option('global','logging'):
                self.global_logging    = parser.get('global','logging').strip()
            if parser.has_option('global','loglevel'):
                self.global_loglevel   = parser.get('global','loglevel').strip()
            if parser.has_option('global','logfacility'):
                self.global_logfacility= parser.get('global','logfacility').strip()
            if parser.has_option('global','logfile'):
                self.global_logfile    = parser.get('global','logfile').strip()
            if parser.has_option('global','workdir'):
                self.global_workdir    = parser.get('global','workdir').strip()

            if parser.has_option('agent','listen'):
                self.agent_listen     = parser.get('agent','listen').strip()
            if parser.has_option('agent','port'):
                self.agent_port       = parser.getint('agent','port')
            if parser.has_option('agent','user'):
                self.agent_user       = parser.get('agent','user').strip()
            if parser.has_option('agent','group'):
                self.agent_group       = parser.get('agent','group').strip()
            if parser.has_option('agent','workers'):
                self.agent_workers    = parser.getint('agent','workers')
            if parser.has_option('agent','pidfile'):
                self.agent_pidfile    = parser.get('agent','pidfile').strip()
            if parser.has_option('agent','cfg2html'):
                self.agent_cfg2html   = parser.get('agent','cfg2html').strip()
            if parser.has_option('agent','ora2html'):
                self.agent_ora2html   = parser.get('agent','ora2html').strip()
            if parser.has_option('agent','crtfile'):
                self.agent_ora2html   = parser.get('agent','crtfile').strip()
            if parser.has_option('agent','keyfile'):
                self.agent_ora2html   = parser.get('agent','keyfile').strip()

            if parser.has_option('server','user'):
                self.server_user       = parser.get('server','user').strip()
            if parser.has_option('server','group'):
                self.server_group       = parser.get('server','group').strip()
            if parser.has_option('server','workers'):
                self.server_workers    = parser.getint('server','workers')
            if parser.has_option('server','refresh'):
                self.server_refresh    = parser.get('server','refresh').strip()
            if parser.has_option('server','pidfile'):
                self.server_pidfile    = parser.get('server','pidfile').strip()
            if parser.has_option('server','dbtype'):
                self.server_dbtype     = parser.get('server','dbtype').strip()
            if parser.has_option('server','dbhost'):
                self.server_dbhost     = parser.get('server','dbhost').strip()
            if parser.has_option('server','dbport'):
                self.server_dbport     = parser.getint('server','dbport')
            if parser.has_option('server','dbuser'):
                self.server_dbuser     = parser.get('server','dbuser').strip()
            if parser.has_option('server','dbpass'):
                self.server_dbpass     = parser.get('server','dbpass').strip()
            if parser.has_option('server','dbname'):
                self.server_dbname     = parser.get('server','dbname').strip()

        except:
            print "Error parsing %s: wrong option detected!" % config
            raise

        # Config logic
        # TODO: add more tests
        if self.global_hostname != None and self.global_hostname.lower() == 'localhost':
            print "Error parsing %s: hostname should be fqdn!" % config
            raise



if __name__ == "__main__":
    cfg = TeddixConfigFile("/etc/teddix/teddix.conf")

    print "[global]"
    print "hostname=%s"     % cfg.global_hostname
    print "logging=%s"      % cfg.global_logging
    print "loglevel=%s"     % cfg.global_loglevel
    print "logfacility=%s"  % cfg.global_logfacility
    print "logfile=%s"      % cfg.global_logfile
    print "workdir=%s"      % cfg.global_workdir

    print "[agent]"
    print "listen=%s"       % cfg.agent_listen
    print "port=%s"         % cfg.agent_port
    print "user=%s"         % cfg.agent_user
    print "group=%s"        % cfg.agent_group
    print "workers=%s"      % cfg.agent_workers
    print "pidfile=%s"      % cfg.agent_pidfile
    print "crtfile=%s"      % cfg.agent_crtfile
    print "keyfile=%s"      % cfg.agent_keyfile
    print "cfg2html=%s"     % cfg.agent_cfg2html
    print "ora2html=%s"     % cfg.agent_ora2html

    print "[server]"
    print "user=%s"         % cfg.server_user
    print "group=%s"        % cfg.server_group
    print "workers=%s"      % cfg.server_workers
    print "refresh=%s"      % cfg.server_refresh
    print "pidfile=%s"      % cfg.server_pidfile
    print "dbtype=%s"       % cfg.server_dbtype
    print "dbhost=%s"       % cfg.server_dbhost
    print "dbport=%s"       % cfg.server_dbport
    print "dbuser=%s"       % cfg.server_dbuser
    print "dbpass=%s"       % cfg.server_dbpass
    print "dbname=%s"       % cfg.server_dbname

