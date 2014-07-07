#!/usr/bin/env python


import logging, os
import platform

class TeddixLogger ():
    name    = None
    level   = logging.DEBUG
    facility= "daemon"
    logfile = "/var/log/teddix.log"
    maxlogsize=0
    logger  = None

    def open_ntlogger(self):
        from logging.handlers import NTEventLogHandler
        try:
            # setup logger level
            self.logger.setLevel (logging.DEBUG)

            # setup formatter
            fmt = logging.Formatter ("%(asctime)s: %(name)s: %(levelname)s: %(message)s")
            # Create NT Event log handler and set level to INFO
            nh = NTEventLogHandler (self.name)
            nh.setLevel (self.level)
            #add formatter to nh
            nh.setFormatter (fmt)
            #add nh to logger
            self.logger.addHandler (nh)
        except:
            print "Unable to Open NT Eventlog!"
            raise

    def open_syslog(self):
        from logging.handlers import SysLogHandler
        try:
            # setup logger level
            self.logger.setLevel (logging.DEBUG)

            # setup formatter
            fmt = logging.Formatter ("%(name)s: %(levelname)s: %(message)s")

            system = platform.system()
            if system == "Linux":
                fh = SysLogHandler (address="/dev/log",facility=self.facility)
            else:
                # In Solaris, /dev/log is a stream device, but python expects it to be
                # a unix domain socket. So we use the default UDP port address. 
                fh = SysLogHandler(facility=self.facility)

            # set log level to INFO
            fh.setLevel (logging.DEBUG)
            #add formatter to fh
            fh.setFormatter (fmt)
            #add fh to logger
            self.logger.addHandler(fh)
        except:
            print "Unable to Open syslog!"
            raise

    def open_logfile(self):
        #from logging.handlers import RotatingFileHandler
        #from logging.handlers import FileHandler
        try:
            # setup logger level
            self.logger.setLevel (logging.DEBUG)

            # setup formatter
            fmt = logging.Formatter ("%(asctime)s: %(name)s: %(levelname)s: %(message)s")

            # Create logfile handler and set level to INFO
            #fh = logging.RotatingFileHandler(self.logfile,maxBytes=self.maxlogsize)
            fh = logging.FileHandler(self.logfile)
            fh.setLevel (self.level)
            #add formatter to fh
            fh.setFormatter (fmt)
            #add fh to logger
            self.logger.addHandler(fh)
        except:
            print "Unable to Open logfile: %s !" %self.logfile
            raise

    def open_console(self):
        try:
            # setup logger level
            self.logger.setLevel (logging.DEBUG)

            # setup formatter
            fmt = logging.Formatter ("%(asctime)s: %(name)s: %(levelname)s: %(message)s")

            # Create logfile handler and set level to INFO
            fh = logging.StreamHandler()
            fh.setLevel (self.level)
            #add formatter to fh
            fh.setFormatter (fmt)
            #add fh to logger
            self.logger.addHandler(fh)
        except:
            print "Unable to open console!"
            raise

    def critical(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.critical(msg)
        exit(128);

    def error(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.error(msg)

    def warn(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.warn(msg)

    def info(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.info(msg)

    def debug(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.debug(msg)

    def exception(self,msg):
        if not self.name:
            print "Logger not initalized!"
            raise
        self.logger.exception(msg)


    def __init__ (self,name):

        self.name = name
        self.logger = logging.getLogger(self.name)



if __name__ == "__main__":

    logger = TeddixLogger ("MyTest")
    logger.open_console()
    #logger.open_syslog()
    #logger.open_logfile()
    #logger.open_ntlogger()

    logger.debug("debug message")
    logger.info("info message")
    logger.warn("warn message")
    logger.error("error message")
    logger.critical("critical message")

