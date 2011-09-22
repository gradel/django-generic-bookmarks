from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('', (r'^bookmarks/', include('bookmarks.urls')))
