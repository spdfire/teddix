#!/usr/bin/env python

from distutils.core import setup

setup(name='teddix-server',
      version='2.0',
      description='Teddix inventory',
      author='spdfire',
      author_email='spdfire@plusinfinity.org',
      license="BSD",
      scripts=['src/teddix-server'],
      data_files=[
          ("/usr/share/teddix/",
              ["config/initdb.sql"]
              ),
          ('/usr/share/teddix-server/init.d/', 
              [ 
                  'init.d/teddix-server.debian' ,
                  'init.d/teddix-server.rhel' ,
                  'init.d/teddix-server.generic',
              ]),
        ]
     )
