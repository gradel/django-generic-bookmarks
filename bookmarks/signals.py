from django.dispatch import Signal

# fired before a bookmark is added
bookmark_will_be_added = Signal(providing_args=['form', 'request'])
# fired after a bookmark is added
bookmark_was_added = Signal(providing_args=['bookmark', 'request'])
# fired before a bookmark is removed
bookmark_will_be_removed = Signal(providing_args=['form', 'request'])
# fired after a bookmark is removed
bookmark_was_removed = Signal(providing_args=['bookmark', 'request'])
