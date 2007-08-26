from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^now/$', 'djangotest.views.current_datetime'),
    (r'^ex4_1/$', 'djangotest.ex4_1.ex4_1'),
    # Example:
    # (r'^djangotest/', include('djangotest.foo.urls')),

    # Uncomment this for admin:
#     (r'^admin/', include('django.contrib.admin.urls')),
)
