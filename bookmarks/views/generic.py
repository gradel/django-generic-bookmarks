"""
Class based generic views.
These views are only available if you are using Django >= 1.3.
"""
from django.views.generic.detail import DetailView

class BookmarkersView(DetailView):
    """
    Can be used to render a list of users that bookmarked a given object.

    For example, you can add in your *urls.py* a view displaying all
    users that bookmarked a single active article::
    
        from bookmarks.views.generic import BookmarkersView
        
        urlpatterns = patterns('',
            url(r'^(?P<slug>[-\w]+)/bookmarkers/$', BookmarkersView.as_view(
                queryset=Article.objects.filter(is_active=True)),
                name="article_bookmarkers"),
        )

    # TODO: manage key

    Two context variables will be present in the template:
        - *object*: the bookmarked article
        - *users*: all the users having that article in their bookmarks
        
    The default template suffix is ``'_bookmarkers'``, and so the template
    used in our example is ``article_bookmarkers.html``.
    """
    context_users_name = 'users'
    template_name_suffix = '_bookmarkers'
    
    def get_context_users_name(self, obj):
        """
        Get the variable name to use for the users.
        """
        return self.context_users_name
        
    def get_users(self, obj, request):
        """
        Return a queryset of users having *obj* as a bookmark.
        """
        # TODO
        pass
        
    def get(self, request, **kwargs):
        # TODO
        pass
        

class BookmarksView(DetailView):
    """
    Can be used to render a list of objects bookmarked by a given user.

    For example, you can add in your *urls.py* a view displaying all
    objects bookmarked by a single active user::
    
        from bookmarks.views.generic import BookmarksView
        
        urlpatterns = patterns('',
            url(r'^(?P<pk>\d+)/bookmarks/$', BookmarksView.as_view(
                queryset=User.objects.filter(is_active=True)),
                name="user_bookmarks"),
        )

    # TODO: manage key

    Two context variables will be present in the template:
        - *object*: the user
        - *bookmarks*: all the objects bookmarked by the given user
        
    The default template suffix is ``'_bookmarks'``, and so the template
    used in our example is ``user_bookmarks.html``.
    """
    context_objects_name = 'bookmarks'
    template_name_suffix = '_bookmarks'
    
    def get_context_objects_name(self, obj):
        """
        Get the variable name to use for the bookmarked objects.
        """
        return self.context_objects_name
        
    def get_objects(self, user, request):
        """
        Return a queryset of objects bookmarked by *user*.
        """
        # TODO
        pass
        
    def get(self, request, **kwargs):
        # TODO
        pass