#!/usr/bin/env python
#

import os
import re
import sys
import time
import psutil
import platform
import subprocess

# Syslog handler
import TeddixLogger

# Config parser
import TeddixConfigFile


class TeddixHPUX:

    # Get installed packages
    def getpkgs(self):
        return packages

    # Get partitions
    def getpartitions(self):
        return disks

    # Get network interfaces
    def getnics(self):
        return nics

    # Get mac address
    def getmac(self,nic):
        return ''

    # Get ipv4 address  
    def getip(self,nic):
        return ips

    # Get dnsservers 
    def getdns(self):
        return dns

    # Get routes 
    def getroutes(self):
        return routes

    # Get groups 
    def getgroups(self):
        return groups

    # Get users 
    def getusers(self):
        return users

    # Get procs 
    def getprocs(self):
        return procs

