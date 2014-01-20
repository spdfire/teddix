#!/usr/bin/env python

# Option parser
from optparse import OptionParser

# MySQL
import MySQLdb 

# Set python module dir
#sys.path.append('@pythondir@' + '/teddix')
#sys.path.append('/usr/lib/python2.7/site-packages' + '/teddix')

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile

class TeddixDatabase:
    def connect(self,dbtype,dbhost,dbport,dbuser,dbpass,dbname):
        
        self.syslog.info("Connecting to %s database: %s@%s:%d/%s " % (dbtype,dbuser,dbhost,dbport,dbname))
        # Open database connection
        if dbtype.lower() == "mysql": 
            try:
                db = MySQLdb.connect(host=dbhost,port=dbport,user=dbuser,passwd=dbpass,db=dbname)
            except MySQLdb.Error, e: 
                self.syslog.error("Unable to open database: %s@%s:%d/%s "  % (dbuser,dbhost,dbport,dbname))
                self.syslog.error("Database error: %s" % e)
                return 
            except Exception, e:
                self.syslog.error("Unable to open database: %s@%s:%d/%s "  % (dbuser,dbhost,dbport,dbname))
                self.syslog.exception('connect(): %s' % e )
                return 

        elif dbtype.lower() == "pgsql":
            print "pgsql"
        elif dbtype.lower() == "oracle":
            print "oracle"
        else:
            print "Unknown DB"

        self.syslog.info("Database %s@%s:%d/%s ready " % (dbuser,dbhost,dbport,dbname))
        self.db = db 

    def disconnect(self):
        self.syslog.info("Disconnecting from database" )
        self.cursor.close()
        self.db.close()

    def execute(self,sql):
        # Try to run the query and catch any exception
        self.syslog.debug("SQL execute(): %s " % sql[:250] )
        try:
            self.cursor.execute(sql)
        except Exception, e:
            self.syslog.error("SQL error: %s" % e)
            self.syslog.warn("Starting rollback")
            self.db.rollback()
    
    def fetchall(self):
        self.syslog.debug("SQL fetchall()")
        try:
            result = self.cursor.fetchall()
        except Exception, e:
            self.syslog.warn("Error in SQL fetchall(): %s" % e)
            return 

        return result

    def rowcount(self):
        try:
            result = self.cursor.rowcount
            self.syslog.debug("SQL rowcount(): %s" % result)
        except Exception, e:
            self.syslog.warn("Error in SQL rowcount(): %s" % e)
            return 

        return result

    def insert_id(self):
        try:
            result = self.db.insert_id()
            self.syslog.debug("SQL insert_id(): %s" % result)
        except Exception, e:
            self.syslog.warn("Error in SQL insert_id(): %s" % e)
            return 

        return result


    def commit(self):
        self.syslog.debug("SQL commit()")
        try:
            self.db.commit()
        except Exception, e:
            self.syslog.warn("Error in SQL commit(): %s" % e)
            return 

    def rollback(self):
        self.syslog.debug("SQL rollback()")
        try:
            self.db.rollback()
        except Exception, e:
            self.syslog.warn("Error in SQL rollback(): %s" % e)
            return 

    def __init__(self,syslog,cfg):
        self.syslog = syslog
        self.dbtype = cfg.server_dbtype 
        self.connect(cfg.server_dbtype,cfg.server_dbhost,int(cfg.server_dbport),cfg.server_dbname,cfg.server_dbpass,cfg.server_dbname)
        self.cursor = self.db.cursor()
        self.db.autocommit(False)

def parse_opts():

    # Parse command line args
    parser = OptionParser ()
    parser.add_option ("-c", "--config",
                    action = "store",
                    dest = "configfile",
                    help = "Read configuration FILE")
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
    syslog = TeddixLogger.TeddixLogger ("TeddixDatabase")
    syslog.open_console()

    syslog.info("Logging subsystem initialized")

    database = TeddixDatabase(syslog,cfg);
    database.execute("SELECT VERSION();")
    
    result = database.fetchall()
    for row in result:
        syslog.debug("SQL result: %s " % row)

    database.disconnect()

