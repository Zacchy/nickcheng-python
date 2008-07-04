from django.conf.urls.defaults import *

urlpatterns = patterns('bragi.blog.views',
    ('^$', 'BlogIndex'),
    ('^page/(\d+)/$', 'BlogIndex'),
    ('^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[\w-]+)/$', 'SingleArticle'),
    
    # Admin
    ('^admin/$', 'AdminIndex'),
    ('^admin/login/$', 'Login'),
    ('^admin/logout/$', 'Logout'),
    ('^admin/write/$', 'Write'),
)

urlpatterns += patterns('bragi.blog.feeds',
    ('^feed/$', 'BlogIndex'),
)