from django.conf.urls.defaults import *

urlpatterns = patterns('',
    ('^$', 'bragi.blog.views.BlogIndex'),
    ('^db/$', 'bragi.blog.views.test'),
)
