from django import forms
from django.contrib.contenttypes.models import ContentType

class BookmarkForm(forms.Form):
    """
    Form class to handle bookmarks.
    
    The bookmark is identified by *content_type*, *object_id* and *key*.
    The bookmark is added or removed based on the his existance.
    
    You can customize the app giving a custom form class, following
    some rules:
    
        - the form must define the *content_type_id*, *object_id* 
          and *key* fields
        - the form's *__init__* method must take a *backend* argument
          and all other normal form's arguments
        - the form must define a *bookmark_exists_for* method, 
          getting a request and returning True if the current user has 
          that instance with that key in his bookmarks
        - the form must define a *save* method, getting a request
          and returning a just added bookmark instance or None if the
          bookmark was removed
        - after the call to the *is_valid* method of the form, and if the
          form is valid, the current instance must be present as
          *instance* attribute of the form
    """
    content_type_id  = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    object_id = forms.CharField(widget=forms.HiddenInput)
    key = forms.RegexField(regex=r'^[\w.+-]+$', widget=forms.HiddenInput)

    def __init__(self, backend, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.backend = backend

    def clean(self):
        """
        Check if an instance with current *content_type_id* and *object_id*
        actually exists in the database.
        Also, that instance will be present in *self.instance*.
        """
        content_type_id = self.cleaned_data.get('content_type_id')
        object_id = self.cleaned_data.get('object_id')
        if content_type_id and object_id:
            # getting content type
            try:
                ct = ContentType.objects.get(pk=content_type_id)
            except ContentType.DoesNotExist:
                raise forms.ValidationError(u'Invalid content type.')
            # getting instance
            try:
                self.instance = ct.get_object_for_this_type(pk=object_id)
            except ct.model_class().DoesNotExist:
                raise forms.ValidationError(u'Invalid instance.')
        # call the parent
        return super(BookmarkForm, self).clean()
    
    def bookmark_exists_for(self, request):
        """
        Return True if the current instance is bookmarked by 
        the user in *request*.

        Raise ValueError if the current user is not authenticated.
        """
        if request.user.is_authenticated():
            key = self.cleaned_data['key']
            return self.backend.exists(request.user, self.instance, key)
        raise ValueError(u'Current user is not authenticated.')

    def save(self, request):
        """
        Add or remove the bookmark.

        Raise ValueError if the current user is not authenticated.
        """
        key = self.cleaned_data['key']
        if self.bookmark_exists_for(request):
            # remove the bookmark
            return self.backend.remove(request.user, self.instance, key)
        return self.backend.add(request.user, self.instance, key)
