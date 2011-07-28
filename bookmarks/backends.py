try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured
    
from bookmarks import settings, models

class BaseBackend(object):
    """
    Base bookmarks backend.
    
    Users may want to change *settings.GENERIC_BOOKMARKS_BACKEND*
    and customize the backend implementing all the methods defined here.
    """
    def get_model(self):
        """
        Must return the bookmark model (a Django model or anything you like).
        Instances of this model must have the following attributes:
        
            - user (who made the bookmark, a Django user instance)
            - key (the bookmark key, as string)
            - content_type (a Django content_type instance)
            - object_id (a pk for the bookmarked object)
            - content_object (the bookmarked object as a Django model instance)
            
        """
        raise NotImplementedError
        
    def add(self, user, instance, key):
        """
        Must create a bookmark for *instance* by *user* using *key*.
        Must return the created bookmark (as a *self.get_model()* instance).
        Must raise *exceptions.AlreadyExists* if the bookmark already exists.
        """
        raise NotImplementedError
        
    def remove(self, user, instance, key):
        """
        Must remove the bookmark identified by *user*, *instance* and *key*.
        Must raise *exceptions.DoesNotExist* if the bookmark does not exist.
        """
        raise NotImplementedError
        
    def remove_all_for(self, instance):
        """
        Must delete all the bookmarks related to given *instance*.
        """
        raise NotImplementedError
                
    def filter_by(self, user, **kwargs):
        """
        Must return all bookmarks added by *user* and corresponding to
        other given *kwargs*.
        The bookmarks must be an iterable (like a Django queryset) of
        *self.get_model()* instances.
        """
        raise NotImplementedError
    
    def filter_for(self, instance, **kwargs):
        """
        Must return all bookmarks added for *instance* and corresponding to
        other given *kwargs*.
        The bookmarks must be an iterable (like a Django queryset) of
        *self.get_model()* instances.
        """
        raise NotImplementedError
        
    def exists(self, user, instance, key):
        """
        Must return True if a bookmark given by *user* for *instance*
        using *key* exists, False otherwise.
        """
        raise NotImplementedError
        

class Backend(BaseBackend):
    """
    Bookmarks Django model backend.

    This is used by default if no other backend is specified.
    
    Users may want to subclass this backend to customize things.
    """
    def get_model(self):
        return models.Bookmark
        
    def add(self, user, instance, key):
        return self.get_model().objects.add(user, instance, key)
        
    def remove(self, user, instance, key):
        self.get_model().objects.remove(user, instance, key)
        
    def remove_all_for(self, instance):
        self.get_model().objects.remove_all_for(instance)
                
    def filter_by(self, user, **kwargs):
        lookups = {'user': user}
        lookups.update(kwargs)
        return self.get_model().objects.filter_with_contents(**lookups)
    
    def filter_for(self, instance, **kwargs):
        return self.get_model().objects.filter_for(instance, **kwargs)
        
    def exists(self, user, instance, key):
        return self.filter_for(instance, user=user, key=key).exists()
        
        
def get_backend():
    if settings.BACKEND is None:
        return Backend()
    i = settings.BACKEND.rfind('.')
    module, attr = settings.BACKEND[:i], settings.BACKEND[i+1:]
    try:
        mod = import_module(module)
    except ImportError, err:
        message = 'Error loading bookmarks backend %s: "%s"'
        raise ImproperlyConfigured(message % (module, err))
    try:
        backend_class = getattr(mod, attr)
    except AttributeError:
        message = 'Module "%s" does not define a bookmarks backend named "%s"'
        raise ImproperlyConfigured(message % (module, attr))
    return backend_class()
