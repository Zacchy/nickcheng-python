from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^bragi/', include('bragi.foo.urls')),
    (r'^blog/', include('bragi.blog.urls')),

    # Uncomment this for admin:
    (r'^admin/', include('django.contrib.admin.urls')),
)
