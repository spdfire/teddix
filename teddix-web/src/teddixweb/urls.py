from django.conf.urls import patterns, include, url
from teddixweb import views 

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'teddixweb.views.home', name='home'),
    # url(r'^teddixweb/', include('teddixweb.foo.urls')),

    url(r'^$', 'teddixweb.views.base_view', name='base_view'),

    url(r'^monitor/dashboard/$', 'teddixweb.views.dashboard_view', name='dashboard_view'),
    url(r'^monitor/reports/$', 'teddixweb.views.notready_view'),
    url(r'^monitor/trends/$', 'teddixweb.views.notready_view'),
    url(r'^monitor/audit/$', 'teddixweb.views.notready_view'),

    url(r'^statistics/os/$', 'teddixweb.views.os_view' ),
    url(r'^statistics/architecture/$', 'teddixweb.views.arch_view' ),
    url(r'^statistics/network/$', 'teddixweb.views.net_view' ),
    url(r'^statistics/software/$', 'teddixweb.views.software_view' ),
    url(r'^statistics/patches/$', 'teddixweb.views.patches_view' ),
    url(r'^statistics/users/$', 'teddixweb.views.users_view' ),
    url(r'^statistics/groups/$', 'teddixweb.views.groups_view' ),
    url(r'^statistics/hardware/$', 'teddixweb.views.hardware_view' ),
    
    url(r'^agents/$', 'teddixweb.views.agents_view' ),
    
    url(r'^extra/$', 'teddixweb.views.extra_view' ),
    url(r'^connection/$', 'teddixweb.views.connection_view' ),
    
    url(r'^users/profile/$', 'teddixweb.views.notready_view'),
    url(r'^users/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #url(r'^admin/', include(admin.site.urls)),
    
    url(r'^admin/users/$', 'teddixweb.views.notready_view'),
    url(r'^admin/groups/$', 'teddixweb.views.notready_view'),
    url(r'^admin/roles/$', 'teddixweb.views.notready_view'),
    url(r'^admin/auth/$', 'teddixweb.views.notready_view'),
    url(r'^admin/settings/$', 'teddixweb.views.notready_view'),
)
