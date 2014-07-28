#!/usr/bin/env python

from distutils.core import setup

setup(name='teddix-web',
      version='2.0',
      description='Teddix inventory',
      author='spdfire',
      author_email='spdfire@plusinfinity.org',
      license="BSD",
      data_files=[
          # bootstrap css
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/dist/css', 
              [ 
              'src/teddixweb/static/bootstrap-3.1.1/dist/css/bootstrap.min.css' ,
              'src/teddixweb/static/bootstrap-3.1.1/dist/css/bootstrap.css' 
              ]),
          
          # bootstrap javascript
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/dist/js/', 
              [ 
              'src/teddixweb/static/bootstrap-3.1.1/dist/js/bootstrap.min.js',
              'src/teddixweb/static/bootstrap-3.1.1/dist/js/bootstrap.js',
              ]),
          
          # bootstrap login
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/signin', 
              [
              'src/teddixweb/static/bootstrap-3.1.1/docs/examples/signin/signin.css' 
              ]),
              
          # bootstrap footer
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/sticky-footer-navbar', 
              [ 
              'src/teddixweb/static/bootstrap-3.1.1/docs/examples/sticky-footer-navbar/sticky-footer-navbar.css' 
              ]),

          # bootstrap start page
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/starter-template', 
              [ 
              'src/teddixweb/static/bootstrap-3.1.1/docs/examples/starter-template/starter-template.css' 
              ]),

          # bootstrap dashboard
          ('/usr/share/teddix-web/teddixweb/static/bootstrap-3.1.1/docs/examples/dashboard', 
              [ 
              'src/teddixweb/static/bootstrap-3.1.1/docs/examples/dashboard/dashboard.css' 
              ]),

          # teddix addons for bootstrap  
          ('/usr/share/teddix-web/teddixweb/static', 
              [
              'src/teddixweb/static/bootstrap-progressbar.js',
              'src/teddixweb/static/bootstrap-popover.js',
              ]),
 
          # jquery 
          ('/usr/share/teddix-web/teddixweb/static/jquery-2.1.1', 
              [
              'src/teddixweb/static/jquery-2.1.1/jquery-2.1.1.min.js',
              'src/teddixweb/static/jquery-2.1.1/jquery-2.1.1.js',
              ]),
         
          # teddix 
          ('/usr/share/teddix-web', ['src/manage.py']),
          ('/usr/share/teddix-web/teddixweb', 
              [
              'src/teddixweb/__init__.py',
              # 'src/teddixweb/forms.py', 
              'src/teddixweb/settings.py',
              'src/teddixweb/urls.py',
              'src/teddixweb/views.py',
              'src/teddixweb/wsgi.py',
              ]),

          # teddix html templates 
          ('/usr/share/teddix-web/teddixweb/templates', 
              [ 
              'src/teddixweb/templates/base.html',
              'src/teddixweb/templates/notready.html',
              'src/teddixweb/templates/login.html' 
              ]),
          ('/usr/share/teddix-web/teddixweb/templates/statistics', [ 
              'src/teddixweb/templates/statistics/os.html',
              'src/teddixweb/templates/statistics/arch.html',
              'src/teddixweb/templates/statistics/net.html',
              'src/teddixweb/templates/statistics/software.html',
              'src/teddixweb/templates/statistics/patches.html',
              'src/teddixweb/templates/statistics/users.html',
              'src/teddixweb/templates/statistics/groups.html',
              'src/teddixweb/templates/statistics/hardware.html'
              ]),
          ('/usr/share/teddix-web/teddixweb/templates/agents', 
              [ 
              'src/teddixweb/templates/agents/agents.html',
              'src/teddixweb/templates/agents/agent_detail.html',
              'src/teddixweb/templates/agents/agent_edit.html', 
              'src/teddixweb/templates/agents/agent_test.html', 
              'src/teddixweb/templates/agents/connection_test.html' 
              ]),
          ('/usr/share/teddix-web/teddixweb/templates/monitor', 
              [ 
              'src/teddixweb/templates/monitor/dashboard.html',
              ]),
          ('/usr/share/teddix-web/teddixweb/templates/extra', 
              [ 
              'src/teddixweb/templates/extra/extra.html',
              'src/teddixweb/templates/extra/cfg2html.html',
              'src/teddixweb/templates/extra/bootlog.html',
              'src/teddixweb/templates/extra/dmesg.html' 
              ]),
          # teddix images/logos 
          ('/usr/share/teddix-web/teddixweb/static', 
              [ 
              'src/teddixweb/static/teddy-bear.png',
              'src/teddixweb/static/ajax-loader.gif'
              ]),
          # teddix icons 
          ('/usr/share/teddix-web/teddixweb/static/actions', 
              [ 
              'src/teddixweb/static/actions/schedule.png',
              'src/teddixweb/static/actions/restart.png',
              'src/teddixweb/static/actions/network.png',
              'src/teddixweb/static/actions/info.png',
              'src/teddixweb/static/actions/edit.png',
              'src/teddixweb/static/actions/delete.png'
              ]),
          # teddix chart dir  
          ('/usr/share/teddix-web/teddixweb/static/charts', 
              [ 
              'src/teddixweb/static/charts/.keep',
              ]),
          # config file 
          ('/usr/share/teddix', 
              [
              'config/websettings.py'
              ]),
          ('/usr/share/teddix-web/init.d/', 
              [ 
                  'init.d/teddix-web.debian' ,
                  'init.d/teddix-web.generic',
              ]),



          ] 
     )
