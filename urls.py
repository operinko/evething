from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	# Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
	# to INSTALLED_APPS to enable admin documentation:
	(r'^admin/doc/', include('django.contrib.admindocs.urls')),
	
	# Uncomment the next line to enable the admin:
	(r'^admin/', include(admin.site.urls)),
	
	# Login/logout crap
	(r'^accounts/login/$',  login),
	(r'^accounts/logout/$', logout),
)

urlpatterns += patterns('evething.thing.views',
	(r'^blueprints/$', 'blueprints'),
	
	(r'^orders/$', 'orders'),
	
	#(r'^status/$', 'status'),
	
	(r'^trade/$', 'trade'),
	(r'^trade/(?P<year>\d{4})-(?P<month>\d{2})/$', 'trade_timeframe'),
	(r'^trade/(?P<period>all)/$', 'trade_timeframe'),
	(r'^trade/(?P<slug>[-\w]+)/$', 'trade_timeframe'),
	
	(r'^transactions/$', 'transactions'),
	(r'^transactions/(?P<item_id>all|\d+)/(?P<year>\d{4})-(?P<month>\d{2})/$', 'transactions_item'),
	url(r'^transactions/(?P<item_id>all|\d+)/(?P<period>all)/$', 'transactions_item', name='transactions-all'),
	(r'^transactions/(?P<item_id>all|\d+)/(?P<slug>[-\w]+)/$', 'transactions_item'),
)

# Redirects
urlpatterns += patterns('django.views.generic.simple',
	('^transactions/(?P<item_id>all|\d+)/$', 'redirect_to', { 'url': '/transactions/%(item_id)s/all/', 'permanent': False }),
)


if settings.DEBUG:
	urlpatterns += patterns('',
		(r'^thing_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
	)
