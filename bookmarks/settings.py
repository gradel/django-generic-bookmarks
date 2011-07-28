from django.conf import settings

# default bookmark model (the one shipped with the application)
BACKEND = getattr(settings, 'GENERIC_BOOKMARKS_BACKEND', None)

# default key to use for bookmarks when there is only one bookmark-per-content
DEFAULT_KEY = getattr(settings, 'GENERIC_BOOKMARKS_DEFAULT_KEY', 'main')

# querystring key that can contain the url of the redirection 
# performed after adding or removing bookmarks
NEXT_QUERYSTRING_KEY = getattr(settings, 
    'GENERIC_BOOKMARKS_NEXT_QUERYSTRING_KEY', 'next')

# set to False if you want to globally disable bookmarks deletion
CAN_REMOVE_BOOKMARKS = getattr(settings, 
    'GENERIC_BOOKMARKS_CAN_REMOVE_BOOKMARKS', True)