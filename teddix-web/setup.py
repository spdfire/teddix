#!/usr/bin/env python

from distutils.core import setup

setup(name='teddix-web',
      version='2.0',
      description='Teddix inventory',
      author='spdfire',
      author_email='spdfire@plusinfinity.org',
      license="BSD",
      data_files=[('/usr/share/teddix-web', ['src/manage.py']),
          ('/usr/share/teddix-web/teddixweb', [
              'src/teddixweb/__init__.py',
              'src/teddixweb/forms.py',
              'src/teddixweb/settings.py',
              'src/teddixweb/urls.py',
              'src/teddixweb/views.py',
              'src/teddixweb/wsgi.py',
              ]),
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/dist/css', [ 'src/teddixweb/static/bootstrap-3.1.1/dist/css/bootstrap.min.css' ]),
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/signin', [ 'src/teddixweb/static/bootstrap-3.1.1/docs/examples/signin/signin.css' ]),
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/starter-template', [ 'src/teddixweb/static/bootstrap-3.1.1/docs/examples/starter-template/starter-template.css' ]),
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/sticky-footer-navbar', [ 'src/teddixweb/static/bootstrap-3.1.1/docs/examples/sticky-footer-navbar/sticky-footer-navbar.css' ]),
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/dist/js/', [ 'src/teddixweb/static/bootstrap-3.1.1/dist/js/bootstrap.min.js' ]),
          ('/usr/share/teddix-web/teddixweb/templates', [ 
              'src/teddixweb/templates/base.html',
              'src/teddixweb/templates/login.html' ]),
          ('/usr/share/teddix-web/teddixweb/templates/hosts', [ 
              'src/teddixweb/templates/hosts/agents.html',
              'src/teddixweb/templates/hosts/arch.html',
              'src/teddixweb/templates/hosts/groups.html',
              'src/teddixweb/templates/hosts/hardware.html',
              'src/teddixweb/templates/hosts/net.html',
              'src/teddixweb/templates/hosts/os.html',
              'src/teddixweb/templates/hosts/software.html',
              'src/teddixweb/templates/hosts/users.html'
              ]),

          ] 
     )
