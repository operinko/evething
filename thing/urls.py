from django.conf.urls import *

urlpatterns = patterns('everdi.blueprints.views',
    (r'^$',					'index'),
    (r'^(?P<bpi_id>\d+)/$', 'details'),
)
