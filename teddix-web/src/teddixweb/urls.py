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
    url(r'^users/login/$', 'django.contrib.auth.views.login', {'template_name': 'login.html'}, name='login'),
    url(r'^users/logout/$', 'django.contrib.auth.views.logout', {'template_name': 'login.html'}),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
