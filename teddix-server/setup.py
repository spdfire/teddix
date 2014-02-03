#!/usr/bin/env python

from distutils.core import setup

setup(name='teddix-server',
      version='2.0',
      description='Teddix inventory',
      author='spdfire',
      author_email='spdfire@plusinfinity.org',
      license="BSD",
      scripts=['src/teddix-server'],
      # TODO: fix config file 
      data_files=[('/etc/teddix',['config/serverlist']),
          ('/etc/init.d', ['init.d/teddix-server'])]
     )
