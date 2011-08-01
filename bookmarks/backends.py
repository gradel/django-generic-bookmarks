try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module
from django.core.exceptions import ImproperlyConfigured

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
    
from bookmarks import settings, models, managers, exceptions

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
                
    def filter_by(self, user, reversed=False, **kwargs):
        """
        Must return all bookmarks added by *user* and corresponding to
        other given *kwargs*.

        The bookmarks must be an iterable (like a Django queryset) of
        *self.get_model()* instances.

        The bookmarks must be ordered by creation date (*created_at*):
        if *reversed* is True, the order must be descending.
        """
        raise NotImplementedError
    
    def filter_for(self, instance, reversed=False, **kwargs):
        """
        Must return all bookmarks added for *instance* and corresponding to
        other given *kwargs*.

        The bookmarks must be an iterable (like a Django queryset) of
        *self.get_model()* instances.

        The bookmarks must be ordered by creation date (*created_at*):
        if *reversed* is True, the order must be descending.
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
                
    def filter_by(self, user, reversed=False, **kwargs):
        lookups = {'user': user}
        lookups.update(kwargs)
        order = '-created_at' if reversed else 'created_at'
        return self.get_model().objects.filter_with_contents(**lookups
            ).order_by(order)
    
    def filter_for(self, instance, reversed=False, **kwargs):
        order = '-created_at' if reversed else 'created_at'
        return self.get_model().objects.filter_for(instance, **kwargs
            ).order_by(order)
        
    def exists(self, user, instance, key):
        return self.filter_for(instance, user=user, key=key).exists()


class MongoBackend(BaseBackend):
    """
    Bookmarks mongodb backend.
    """
    def __init__(self):
        # establishing mongodb connection
        import mongoengine
        self.ConnectionError = mongoengine.connection.ConnectionError
        name = settings.MONGODB["NAME"]
        username = settings.MONGODB.get("USERNAME")
        password = settings.MONGODB.get("PASSWORD")
        parameters = settings.MONGODB.get("PARAMETERS", {})
        try:
            self.db = mongoengine.connect(name, username, password, **parameters)
        except mongoengine.connection.ConnectionError:
            raise exceptions.MongodbConnectionError
    
    def get_model(self):
        import datetime
        from mongoengine import Document, IntField, StringField, DateTimeField
        
        class Bookmark(Document):
            content_type_id = IntField(required=True, min_value=1)
            object_id = IntField(required=True, min_value=1)
            
            key = StringField(required=True, max_length=16)
            
            user_id = IntField(required=True, min_value=1, 
                unique_with=['content_type_id', 'object_id', 'key'])
            
            created_at = DateTimeField(required=True, 
                default=datetime.datetime.now)

            meta = {'indexes': ['user_id', ('content_type_id', 'object_id')]}

            @property
            def user(self):
                return User.objects.get(pk=self.user_id)
            
            @property
            def content_object(self):
                ct = ContentType.objects.get_for_id(self.content_type_id)
                return ct.get_object_for_this_type(pk=self.object_id)
        
        return Bookmark

    def add(self, user, instance, key):
        import mongoengine
        model = self.get_model()
        bookmark = model(
            content_type_id=managers.get_content_type_for_model(instance).id,
            object_id=instance.pk,
            key=key,
            user_id=user.pk
        )
        try:
            bookmark.save()
        except mongoengine.OperationError:
            raise exceptions.AlreadyExists
        return bookmark
        
    def remove(self, user, instance, key):
        # TODO
        #self.get_model().objects.remove(user, instance, key)
        pass
        
    def remove_all_for(self, instance):
        # TODO
        #self.get_model().objects.remove_all_for(instance)
        pass
                
    def filter_by(self, user, reversed=False, **kwargs):
        # TODO
        # lookups = {'user': user}
        # lookups.update(kwargs)
        # order = '-created_at' if reversed else 'created_at'
        # return self.get_model().objects.filter_with_contents(**lookups
        #     ).order_by(order)
        pass
    
    def filter_for(self, instance, reversed=False, **kwargs):
        # TODO
        # order = '-created_at' if reversed else 'created_at'
        # return self.get_model().objects.filter_for(instance, **kwargs
        #     ).order_by(order)
        pass
        
    def exists(self, user, instance, key):
        # TODO
        # return self.filter_for(instance, user=user, key=key).exists()
        pass
        
        
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
