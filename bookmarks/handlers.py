from django.db.models.base import ModelBase
from django.db.models.signals import pre_delete

from bookmarks import settings, backends, forms, exceptions, signals

class Handler(object):
    """
    Encapsulates content bookmarking options for a given model.
    
    This class can be subclassed to specify different behaviour and options
    for bookmarks of a given model, but can also be used directly, just to
    handle default any model using default options. 
    
    The default handler uses the project's settings as options: this 
    way you can register not customized handlers and then modify
    their options just editing the settings file.
    
    Most common bookmarking needs can be handled by subclassing *Handler* 
    and changing the values of pre-defined attributes. 
    The full range of built-in options is as follows.
    
        
    .. py:attribute:: default_key
        
        default key to use for bookmarks when there is only one 
        bookmark-per-content (default: *'main'*)
        
    .. py:attribute:: next_querystring_key
    
        querystring key that can contain the url of the redirection performed 
        after bookmarking (default: *'next'*)
    
    .. py:attribute:: can_remove_bookmarks 
    
        set to False if you want to globally disable bookmarks deletion
        (default: *True*)
    
    .. py:attribute:: form_class
    
        form class that will be used to handle bookmark's adding and removing
        (default: *bookmarks.forms.BookmarkForm*) 
        
    For situations where the built-in options listed above are not sufficient, 
    subclasses of *Handler* can also override the methods which 
    actually perform the bookmarking process, and apply any logic they desire.
    
    See the method's docstrings for a description of how each method is
    used during the bookmarking process.
    """
    default_key = settings.DEFAULT_KEY
    next_querystring_key = settings.NEXT_QUERYSTRING_KEY
    can_remove_bookmarks = settings.CAN_REMOVE_BOOKMARKS
    
    form_class = forms.BookmarkForm
    
    def __init__(self, model, backend):
        self.model = model
        self.backend = backend
        
    # key management
            
    def get_key(self, request, instance):
        """
        Return the bookmark key to be used to save the bookmark if the key
        is not provided by the user (for example with the optional
        argument *using* in templatetags).
        
        Subclasses can return different keys based on the *request* and
        the given target object *instance*.
        
        For example, if you want a different key to be used if the user is
        staff, you can override this method in this way::
        
            def get_key(self, request, instance):
                return 'staff' if request.user.is_superuser else 'normal'

        This method is called only if the user does not provide a bookmark key.
        """
        return self.default_key
        
    def allow_key(self, request, instance, key):
        """
        This method is called when the user tries to bookmark an object 
        using the given bookmark *key* (e.g. when the bookmark view is 
        called with POST data).
        
        The bookmarking process continues only if this method returns True
        (i.e. a valid key is passed).
        
        For example, if you want two different bookmarks for each 
        target object, you can use two forms (each providing a different 
        key, say 'main' and 'other') and then allow those keys::
        
            def allow_key(self, request, instance, key):
                return key in ('main', 'other')        
        """
        return key == self.get_key(request, instance)
    
    # form management
    
    def get_form_class(self, request):
        """
        Return the form class that will be used to add or remove bookmarks.
        This method can be overridden by view-level passed form class.
        """
        return self.form_class
        
    def get_form_kwargs(self, request, instance, key):
        """
        Return the optional kwargs used to instantiate the bookmark form.
        """
        return {}
        
    # adding bookmarks
        
    def pre_add(self, request, form):
        """
        Called just before the bookmark is saved to the db, this method takes
        the *request* and the *form* instance.
        
        Subclasses can use this method to check if the bookamrk can be saved 
        and, if necessary, block the bookmarking process returning False.
        
        This method is called by a *signals.bookmark_will_be_added* 
        receiver always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal: the bookmarking process is killed 
        if just one receiver returns False.
        """
        return request.user.is_authenticated()
        
    def add(self, request, form):
        """
        Save the bookamrk to the database.
        Must return the new saved bookmark.        
        """
        return form.save()
        
    def post_add(self, request, bookmark, created):
        """
        Called just after a bookmark is saved to the db.
        
        This method is called by a *signals.bookmark_was_added* receiver
        always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal.
        
        By default, this method does noting.
        """
        pass
        
    # removing bookmarks
    
    def pre_remove(self, request, form):
        """
        Called just before the bookmark is deleted from the db, 
        this method takes the *request* and the *form* instance.
        
        Subclasses can use this method to check if the bookmark can be deleted 
        and, if necessary, block the bookmark deletion process returning False.
        
        This method is called by a *signals.bookmark_will_be_removed* 
        receiver always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal: the bookmark deletion process 
        is killed if just one receiver returns False.
        """
        return request.user.is_authenticated() and self.can_remove_bookmarks
        
    def remove(self, request, form):
        """
        Delete the bookmark from the database.
        """
        form.delete()
        
    def post_remove(self, request, bookmark):
        """
        Called just after a bookmark is deleted to from db.
        
        This method is called by a *signals.bookmark_was_removed* receiver
        always attached to the handler.
        It's up to the developer if override this method or just connect
        another listener to the signal.
        
        By default, this method does noting.
        """
        pass
        
    # view callbacks
    
    def ajax_response(self, request, bookmark, created):
        """
        Called by *self.response* when the request is ajax.
        Return a json reponse containing::
        
            {
                'key': 'the_bookamrk_key',
                'bookmark_id': bookmark.id,
                'user_id': <the id of the bookmarker>,
            }
        """
        from django.http import HttpResponse
        from django.utils import simplejson as json
        data = {
            'key': bookmark.key,
            'bookmark_id': bookmark.id,
            'user_id': bookmark.user_id,
        }
        return HttpResponse(json.dumps(data), content_type="application/json")
        
    def normal_response(self, request, bookmark, created):
        """
        Called by *success_response* when the request is not ajax.
        Return a redirect response.
        """
        from django.shortcuts import redirect
        next = request.REQUEST.get('next') or request.META.get('HTTP_REFERER') or '/'
        return redirect(next)
                
    def response(self, request, bookmark, created):
        """
        Callback used by the bookmarking views, called when the user 
        successfully added or removed a bookmark. 
        Must return a Django http response (usually a redirect, or
        some json if the request is ajax).
        """
        method = self.ajax_response if request.is_ajax() else self.normal_response
        return method(request, bookmark, created)
        
    def fail(self, request, errors):
        """
        Callback used by the bookmarking views, called when bookmark form 
        did not validate. Must return a Django http response.
        """
        from django.http import HttpResponseBadRequest
        return HttpResponseBadRequest('Invalid data in bookmark form.')
    
    # receivers
        
    def deleting_target_object(self, sender, instance, **kwargs):
        """
        The target object *instance* of the model *sender*, is being deleted,
        so we must delete all the bookmarks related to that instance.
        
        This receiver is usually connected by the bookmark registry, when 
        a handler is registered.
        """
        self.backend.remove_all_for(instance)
            
     
class Registry(object):
    """
    Registry that stores the handlers for each content type bookmarks system.

    An instance of this class will maintain a list of one or more models 
    registered for being bookmarked, and their associated handler classes.

    To register a model, obtain an instance of *Registry* (this module exports 
    one as *store*), and call its *register* method, passing the model class 
    and a handler class (which should be a subclass of *Handler*). 
    Note that both of these should be the actual classes, not instances 
    of the classes.

    To cease bookmarks handling for a model, call the *unregister* method,
    passing the model class.

    For convenience, both *register* and *unregister* can also accept a list 
    of model classes in place of a single model; this allows easier 
    registration of multiple models with the same *Handler* class.
    """
    def __init__(self):
        self._registry = {}
        self.backend = backends.get_backend()
        self._connect(self.backend.get_model())
        
    def _connect(self, model):
        """
        Pre and post (add or remove) bookmark signals.
        """
        signals.bookmark_will_be_added.connect(self._pre_add, sender=model)
        signals.bookmark_was_added.connect(self._post_add, sender=model)
        signals.bookmark_will_be_removed.connect(self._pre_remove, sender=model)
        signals.bookmark_was_removed.connect(self._post_remove, sender=model)
        
    def _connect_model_signals(self, model, handler):
        """
        Connect the *pre_delete* signal sent by given *model* to
        the *handler* receiver.
        """
        pre_delete.connect(handler.deleting_target_object, sender=model)
    
    def _get_handler_instance(self, model, handler_class, options):
        """
        Return an handler instance for the given *model*.
        """
        handler = handler_class(model, self.backend)
        for k, v in options.items():
            setattr(handler, k, v)
        return handler

    def register(self, model_or_iterable, handler_class=None, **kwargs):
        """
        Register a model or a list of models for bookmark handling, using a 
        particular *handler_class*, e.g.::
        
            from bookmarks.handlers import store, Handler
            # register one model
            store.handle(Article, Handler)
            # register other two models
            store.register([Film, Series], Handler)
        
        If the handler class is not given, the default 
        *bookmarks.handlers.Handler* class will be used.
        
        If *kwargs* are present, they are used to override the handler
        class attributes (using instance attributes), e.g.::
            
            store.register(Article, Handler, 
                can_remove_bookmarks=False, form_class=MyForm)

        Raise *AlreadyHandled* if any of the models are already registered.
        """
        if handler_class is None:
            handler_class = Handler
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model in self._registry:
                raise exceptions.AlreadyHandled(
                    "The model '%s' is already being handled" % 
                    model._meta.module_name)
            handler = self._get_handler_instance(model, handler_class, kwargs)
            self._registry[model] = handler
            self._connect_model_signals(model, handler)
        
    def unregister(self, model_or_iterable):
        """
        Remove a model or a list of models from the list of models that will
        be handled.

        Raise *NotHandled* if any of the models are not currently registered.
        """
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            if model not in self._registry:
                raise exceptions.NotHandled(
                    "The model '%s' is not currently being handled" % 
                    model._meta.module_name)
            del self._registry[model]
            
    def get_handler(self, model_or_instance):
        """
        Return the handler for given model or model instance.
        Return None if model is not registered.
        """
        if isinstance(model_or_instance, ModelBase):
            model = model_or_instance
        else:
            model = type(model_or_instance)
        return self._registry.get(model)

    def _pre_add(self, sender, form, request, **kwargs):
        """
        Apply any necessary pre-save steps to new bookmarks.
        """
        model = type(form.target_object)
        if model in self._registry:
            return self._registry[model].pre_add(request, form)
        return False
        
    def _post_add(self, sender, bookmark, request, **kwargs):
        """
        Apply any necessary post-save steps to new bookmarks.
        """
        model = bookmark.content_type.model_class()
        if model in self._registry:
            return self._registry[model].post_add(request, bookmark)
        
    def _pre_remove(self, sender, form, request, **kwargs):
        """
        Apply any necessary pre-delete bookmark steps.
        """
        model = type(form.target_object)
        if model in self._registry:
            return self._registry[model].pre_remove(request, form)
        return False

    def _post_remove(self, sender, bookmark, request, **kwargs):
        """
        Apply any necessary post-delete bookmark steps.
        """
        model = bookmark.content_type.model_class()
        if model in self._registry:
            return self._registry[model].post_remove(request, bookmark)
            
# import this instance in your code to use in registering models
store = Registry()
