from django.conf.urls.defaults import *

urlpatterns = patterns('bragi.blog.views',
    ('^$', 'BlogIndex'),
    ('^page/(\d+)/$', 'BlogIndex'),
    
    # Admin
    ('^admin/$', 'AdminIndex'),
    ('^admin/login/$', 'Login'),
    ('^admin/logout/$', 'Logout'),
    ('^admin/write/$', 'Write'),
)
