from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('bookmarks.views',
    url(r'^bookmark/$', 'bookmark', name='bookmarks_bookmark'),
)