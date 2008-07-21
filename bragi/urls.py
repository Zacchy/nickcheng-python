from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('',
    (r'^sitemedia/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': settings.STATIC_PATH}),
)

if settings.BLOGHOME:
    urlpatterns += patterns('',
        (r'^', include('bragi.blog.urls')),
    )
else:
    urlpatterns += patterns('',
        (r'^$', 'bragi.views.Index'),
        (r'^blog/', include('bragi.blog.urls')),
    )
