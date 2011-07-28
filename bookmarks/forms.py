from django import forms
from django.contrib.contenttypes.models import ContentType

class BookmarkForm(forms.Form):
    """
    Form class to handle bookmarks.
    
    The bookmark is identified by *content_type*, *object_id*, *key* and *user*.    
    The bookmark is added or removed based on the his existance.
    
    You can customize the app giving a custom form class, following
    some rules:
    
        - the form must define the *content_type*, *object_id* and *key* fields
        - the form's *__init__* method must take as first, second and third
          positional arguments the target object to bookmark, the user 
          and the bookmark key
        - the form must have the following attributes
        - the form must define the *get_bookmark* method, getting the request 
          and returning a bookmark instance (just added or ready to remove).
    """
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.CharField(widget=forms.HiddenInput)
    key = forms.RegexField(regex=r'^[\w.+-]+$', widget=forms.HiddenInput,
        required=False)
    
    def __init__(self, target_object, key, *args, **kwargs):
        self.target_object = target_object
        self.key = key
        super(BookmarkForm, self).__init__(*args, **kwargs)
        
    # TODO: design decision needed
