from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^now/$', 'djangotest.views.current_datetime'),
    # Example:
    # (r'^djangotest/', include('djangotest.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
