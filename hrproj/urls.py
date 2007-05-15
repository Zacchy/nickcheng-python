from django.conf import settings
from django.conf.urls.defaults import *
from django.views.static import serve as static_serve
from django.views.generic.simple import direct_to_template as direct

from hrproj.hr import views

urlpatterns = patterns('',
    # Example:
    # (r'^hrproj/', include('hrproj.apps.foo.urls.foo')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^r/',     include( 'django.conf.urls.shortcut' )),

    # Static files, for development purposes
    (r'^static/(.*)$', static_serve, {'document_root': settings.MEDIA_ROOT}),

    # Application views
    (r'^$', views.index),
    (r'^readers/$',                  views.reader_list),
    (r'^readers/(?P<username>.*)/$', views.reader_detail),
    (r'^tags/$',                     views.tag_list),
    (r'^tags/(?P<slug>.*)/$',        views.tag_detail),
    (r'^books/$',                    views.book_list),
    (r'^books/(?P<slug>.*)/$',       views.book_detail),

)
