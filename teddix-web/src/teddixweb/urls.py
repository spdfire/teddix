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
    url(r'^hosts/agents/$', 'teddixweb.views.agents_view' ),
#    url(r'^hosts/agents/\d+/delete$', 'teddixweb.views.agent_delete_view' ),
    url(r'^hosts/os/$', 'teddixweb.views.os_view' ),
    url(r'^hosts/architecture/$', 'teddixweb.views.arch_view' ),
    url(r'^hosts/network/$', 'teddixweb.views.net_view' ),
    url(r'^hosts/software/$', 'teddixweb.views.software_view' ),
    url(r'^hosts/patches/$', 'teddixweb.views.patches_view' ),
    url(r'^hosts/users/$', 'teddixweb.views.users_view' ),
    url(r'^hosts/groups/$', 'teddixweb.views.groups_view' ),
    url(r'^hosts/hardware/$', 'teddixweb.views.hardware_view' ),
    url(r'^extra/$', 'teddixweb.views.extra_view' ),
    url(r'^users/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
