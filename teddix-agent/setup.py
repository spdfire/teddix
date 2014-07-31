#!/usr/bin/env python

from distutils.core import setup

setup(name='teddix-agent',
      version='2.0',
      description='Teddix inventory',
      author='spdfire',
      author_email='spdfire@plusinfinity.org',
      license="BSD",
      scripts=['src/teddix-agent'],
      data_files=[
          ('/usr/share/teddix-agent/init.d/', 
              [ 
                  'init.d/teddix-agent.debian' ,
                  'init.d/teddix-agent.rhel' ,
                  'init.d/teddix-agent.sunos-smf',
                  'init.d/teddix-agent.generic',
              ]),
        ]
     )
