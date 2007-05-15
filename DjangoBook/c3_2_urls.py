from django.conf.urls.defaults import *
from djangosite.views import current_datetime

urlpatterns = patterns('',
					   (r'^now/$', current_datetime),
					   (r'^now/plus(\d{1,2})hours/$', hours_ahead),
					   )

