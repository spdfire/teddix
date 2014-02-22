#!/usr/bin/env python

import re
import os
import urlparse
import base64
import subprocess

# Syslog handler
import TeddixLogger


class TeddixStringParser:

    def isfloat(self,value):
        try:
            float(value)
            return True
        except ValueError:
            return False 

    def isint(self,value):
        try:
            int(value)
            return True
        except ValueError:
            return False 

    def isstr(self,value):
        if value is None:
            return False
        else:
            try:
                tmp = str(value)
                if len(tmp) == 0:
                    return False
                else:
                    return True
            except ValueError:
                return False 

    def isunicode(self,value):
        if not self.isstr(value):
            return False
        else:
            try:
                unicode(value, errors='strict') 
                return True
            except ValueError:
                return False 

    def ishostname(self,value):
        if not self.isstr(value):
            return False
        else:
            match = re.search(r'([a-zA-Z1234567890\.\-]+)',value)
            #hostname = urlparse.urlparse(value).hostname
            if match:
                return True
            else:
                return False

    def isb64(self,value):
        if not self.isstr(value):
            return False
        else:
            match = re.search(r'([a-zA-Z1234567890\=]+)',value)
            try:
                base64.b64decode(value)
                return True
            except ValueError:
                return False 

    def str2int(self,value):
        if not self.isint(value):
            return None
        else:
            try:
                return int(value)
            except ValueError:
                return int(round(float(value)))


    def b64encode(self,value):
        if not self.isstr(value):
            return None
        else:
            return base64.b64encode(value)

    def b64decode(self,value):
        if not self.isbase64(value):
            return None
        else:
            return base64.b64decode(value)



    def str2float(self,value):
        if not self.isfloat(value):
            return None
        else:
            return float(value)

    def str2hostname(self,value):
        if not self.ishostname(value):
            return None
        else:
            #hostname = urlparse.urlparse(value).hostname
            match = re.search(r'([a-zA-Z1234567890\.\-]+)',value)
            if match:
                host = match.group(1)
                host = host.strip()
                host = host.lower()
                return host

    def str2uni(self,value):
        if not self.isstr(value):
            return ''
        else:
            data = str(value)
            parsed = unicode(data, errors='ignore') 
            return parsed
    
    def strsearch(self,regexp,line):
        parsed = self.str2uni(line)
        if parsed == None: 
            return ''
        else:
            match = re.search(r'%s' % regexp , parsed)
            if match:
                return match.group(1)
            else:
                return ''

    def arraysearch(self,regexp,lines):
        i=0
        for i in range(len(lines)):
            tmp = self.strsearch(regexp,lines[i])
            if tmp: 
                return tmp
            i += 1
        return ''


    def readlineyesno(self,path,mode=os.R_OK):
        value = self.readline(path,mode)
        if len(value) == 0:
            return ''

        if self.isstr(value):
            if value == '0':
                return 'No'
            else:
                return 'Yes'
        else:
            return ''

    
    def readline(self,path,mode=os.R_OK):
        if os.access(path, mode):
            f = open(path)
            line = f.readline()
            f.close()
            
            line = line.strip()
            parsed = self.str2uni(line)
            return parsed
        else:
            return ''


    def readlines(self,path,mode=os.R_OK):
        
        line = {}
        if os.access(path, mode):
            f = open(path)
            buf = f.read()
            f.close()

            i = 0 
            for tmp in buf.split('\n'):
                if len(tmp) > 0:
                    r = tmp.strip()
                    line[i] = self.str2uni(r)
                    i += 1
 
            return line


        else:
            return line

    def arrayfilter(self,regexp,lines):
        filtered = {}
        j = 0
        for i in range(len(lines)):
            tmp = self.strsearch(regexp,lines[i])
            if tmp: 
                filtered[j] = lines[i]
                j += 1
            i += 1
        return filtered


    def checkexec(self,cmd):
        searchdir = {}
        searchdir[0] = '/bin'
        searchdir[1] = '/sbin'
        searchdir[2] = '/usr/bin'
        searchdir[3] = '/usr/sbin'
        searchdir[4] = '/usr/local/bin'
        searchdir[5] = '/usr/local/sbin'
        searchdir[6] = '/usr/pkg/bin'
        searchdir[7] = '/usr/pkg/sbin'
        searchdir[8] = '/opt/csw/bin'
        searchdir[9] = '/opt/csw/sbin'

        i = 0 
        for i in range(len(searchdir)):
            path = searchdir[i] + '/' + cmd
            t_path = 'test -x ' + path 
            if subprocess.call(t_path,shell=True) == 0:
                return True
            i += 1 

        return False 

    def readstdout(self,cmd): 
        
        line = {}
        exe = cmd.split(' ')[0]

        if self.checkexec(exe):
            proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout = proc.stdout.read()

            i = 0 
            for tmp in stdout.split('\n'):
                if len(tmp) > 0:
                    r = tmp.strip()
                    line[i] = self.str2uni(r)
                    i += 1
 
            return line
        
        else:
            return line


    def getretval(self,cmd): 
        
        line = {}
        exe = cmd.split(' ')[0]

        if self.checkexec(exe):
            ret = subprocess.call("%s 2>/dev/null >/dev/null" % cmd,shell=True)
            return ret


