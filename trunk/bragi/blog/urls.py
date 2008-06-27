from django.conf.urls.defaults import *

urlpatterns = patterns('bragi.blog.views',
    ('^$', 'BlogIndex'),
    ('^page/(\d+)/$', 'BlogIndex'),
    ('^db/$', 'test'),
)
