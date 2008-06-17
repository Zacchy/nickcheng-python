from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^$', 'blog.views.BlogIndex'),
    ('^db/$', 'blog.views.test'),
)
