from django.conf.urls.defaults import *

from django.contrib import admin
from demTV.models import UserProfile, Show
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^demTvDjango/', include('demTvDjango.foo.urls')),
    (r'^css/images/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/steve/demTV/media/images'}),
    (r'^css/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/steve/demTV/media/css'}),


    # Password reset functionality
    (r'^password_reset/$', 'django.contrib.auth.views.password_reset', {'template_name':'registration/password_reset.html'}),
    (r'^password_reset/done/$', 'django.contrib.auth.views.password_reset_done', {'template_name':'registration/password_reset_done.html'}),
    (r'^reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$', 'django.contrib.auth.views.password_reset_confirm', {'template_name':'registration/password_reset_confirm.html'}),
    (r'^reset/done/$', 'django.contrib.auth.views.password_reset_complete', {'template_name':'registration/password_reset_complete.html'}),

    (r'^xd_receiver\.htm$', 'demTvDjango.demTV.views.xd_receiver'),
    (r'^facebook/', include('facebookconnect.urls')),
    (r'^accounts/profile/$', 'demTvDjango.demTV.views.profile'),
    (r'^accounts/', include('registration.backends.default.urls')),

    (r'^user/(.*)', 'demTvDjango.demTV.views.user'),
    (r'^edituser/(.*)', 'demTvDjango.demTV.views.editUser'),
    # This is in case someone selects a 'None' show
    (r'^show/$', 'demTvDjango.demTV.views.shows'),
    (r'^show/(.*)', 'demTvDjango.demTV.views.show'),
    (r'^editshows/(.*)', 'demTvDjango.demTV.views.editShows'),

    (r'^forum/', include('djangobb_forum.urls', namespace='djangobb')),
    (r'^forum/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/steve/demTV/media/forum'}),

    (r'^time/(?P<day>\d+)/(?P<timeslot>\d+(.\d)?)/$', 'demTvDjango.demTV.views.timeslot'),
    (r'^time/(?P<day>\d+)/$', 'demTvDjango.demTV.views.day'),
    (r'^time/$', 'demTvDjango.demTV.views.time'),

    (r'^lineup/$', 'demTvDjango.demTV.views.lineup'),
    (r'^live/$', 'demTvDjango.demTV.views.live'),
    (r'^shows/$', 'demTvDjango.demTV.views.shows'),
  
    # Static-y pages
    (r'^about/$', 'demTvDjango.demTV.views.about'),
    (r'^contact/$', 'demTvDjango.demTV.views.contact'),
    (r'^jobs/$', 'demTvDjango.demTV.views.jobs'),
    (r'^press/$', 'demTvDjango.demTV.views.press'),
    (r'^privacy/$', 'demTvDjango.demTV.views.privacy'),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^$', 'demTvDjango.demTV.views.home'),
    
)
