#!/usr/bin/env python

import re
import urlparse
import base64

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
        try:
            str(value)
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

