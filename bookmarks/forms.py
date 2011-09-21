from django import forms
from django.contrib.contenttypes.models import ContentType

class BookmarkForm(forms.Form):
    """
    Form class to handle bookmarks.
    
    The bookmark is identified by *content_type*, *object_id* and *key*.
    The bookmark is added or removed based on the his existance.
    
    You can customize the app giving a custom form class, following
    some rules:
        
        - the form must provide the following fields:

            - content_type_id -> the content type id of the bookmarked instance
            - object_id -> the bookmarked instance id
            - key -> the bookmark key

        - the form must define the following methods:

            - __init__(self, request, backend, *args, **kwargs):
              the *backend* argument is the currently used bookmark backend
              the *args and **kwargs are normal form *args and **kwargs

            - bookmark_exists(self):
              return True if the current user has that instance with that key 
              in his bookmarks

            - instance(self):
              return the current instance to bookmark or None if the
              form data (content_type_id and object_id) is invalid

            - save(self):
              add or remove a bookmark and return it
    """
    content_type_id  = forms.IntegerField(min_value=0, widget=forms.HiddenInput)
    object_id = forms.CharField(widget=forms.HiddenInput)
    key = forms.RegexField(regex=r'^[\w.+-]+$', widget=forms.HiddenInput)

    def __init__(self, request, backend, *args, **kwargs):
        super(BookmarkForm, self).__init__(*args, **kwargs)
        self.request = request
        self.backend = backend
        self._instance = None

    def clean(self):
        """
        Check if an instance with current *content_type_id* and *object_id*
        actually exists in the database.
        Also, check that current user is authenticated.
        """
        if self.request.user.is_anonymous():
            raise forms.ValidationError(u'Invalid user.')
        # data validation
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
                self._instance = ct.get_object_for_this_type(pk=object_id)
            except ct.model_class().DoesNotExist:
                raise forms.ValidationError(u'Invalid instance.')
        # call the parent
        return super(BookmarkForm, self).clean()

    def instance(self):
        """
        Return the bookmarked instance or None if the form is not valid.

        This method validates the form.
        """
        if self.is_valid():
            return self._instance

    def _exists(self):
        key = self.cleaned_data['key']
        return self.backend.exists(self.request.user, self._instance, key)
        
    def bookmark_exists(self):
        """
        Return True if *self.instance* is bookmarked by the current user
        with the current key.

        Raise ValueError if the form is not valid.

        This method validates the form.
        """
        if self.is_valid():
            return self._exists()
        raise ValueError(u'Form is not valid.')

    def save(self):
        """
        Add or remove the bookmark and return it.

        You must call this method only after form validation.
        """
        key = self.cleaned_data['key']
        method = self.backend.remove if self._exists() else self.backend.add
        return method(self.request.user, self._instance, key)
