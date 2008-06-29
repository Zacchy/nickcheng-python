from django.conf.urls.defaults import *

urlpatterns = patterns('bragi.admin.views',
    ('^$', 'AdminIndex'),
    ('^logout/$', 'Logout'),
)
