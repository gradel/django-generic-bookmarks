import re

from django import template

from bookmarks import handlers, exceptions

register = template.Library()

BOOKMARK_EXPRESSION = re.compile(r"""
    ^ # begin of line
    for\s+(?P<instance>[\w.'"]+) # instance
    (\s+using\s+(?P<key>[\w.]+))? # key
    \s+as\s+(?P<varname>\w+) # varname
    $ # end of line
""", re.VERBOSE)

def _parse_args(parser, token):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        error = u"%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError, error
    # args validation
    match = FILTER_OBJECTS_EXPRESSION.match(arg)
    if not match:
        error = u"%r tag has invalid arguments" % tag_name
        raise template.TemplateSyntaxError, error
    return match.groupdict()
 

 class BaseNode(template.Node):
    def __init__(self, instance, key, varname):
        # instance
        self.instance = template.Variable(instance)
        # key
        self.key_variable = None
        if key is None:
            self.key = None
        elif key[0] in ('"', "'") and key[-1] == key[0]:
            self.key = key[1:-1]
        else:
            self.key_variable = template.Variable(key)
        # varname
        self.varname = varname

    def _get_key(self, context):
        if self.key_variable:
            return self.key_variable.resolve(context)
        return self.key


@register.tag
def bookmark(parser, token):
    """
    Return as a template variable a bookmark object for the given instance
    and key, and for current user.

    Usage:
    
    .. code-block:: html+django

        {% bookmark for *instance* [using *key*] as *varname* %}

    Note that if the key is not given, it will be generated using 
    the handler's *get_key* method, that, if not overridden, returns
    the default key. 

    The template variable will be None if:
        - the user is not authenticated
        - the instance is not bookmarkable
        - the bookmark does not exist
    """
    return BookmarkNode(**_parse_args(parser, token))

class BookmarkNode(BaseNode):   
    def render(self, context):
        # user validation
        request = context['request']
        if request.user.is_anonymous():
            return u''

        # instance and handler
        instance = self.instance.resolve(context)
        handler = handlers.library.get_handler(instance)
        # handler validation
        if handler is None:
            return u''
        
        # key
        key = handler.get_key(request, instance, self._get_key(context))

        # retreiving bookmark
        try:
            context[self.varname] = handler.get(request.user, instance, key)
        except exceptions.DoesNotExist:
            pass
        return u''


@register.tag
def bookmark_form(parser, token):
    """
    Return as a template variable a Django form to add or remove a bookmark 
    for the given instance and key, and for current user.

    Usage:
    
    .. code-block:: html+django

        {% bookmark_form for *instance* [using *key*] as *varname* %}

    Note that if the key is not given, it will be generated using 
    the handler's *get_key* method, that, if not overridden, returns
    the default key. 

    The template variable will be None if:
        - the user is not authenticated
        - the instance is not bookmarkable
        - the key is not allowed
    """
    return BookmarkFormNode(**_parse_args(parser, token))

class BookmarkFormNode(template.Node):
    def render(self, context):
        # user validation
        request = context['request']
        if request.user.is_anonymous():
            return u''

        # instance and handler
        instance = self.instance.resolve(context)
        handler = handlers.library.get_handler(instance)
        # handler validation
        if handler is None:
            return u''
        
        # key validation
        key = handler.get_key(request, instance, self._get_key(context))
        if not handler.allow_key(request, instance, key):
            return u''

        # retreiving form
        form = handler.get_form(request, instance, key))
        context[self.varname] = form
        return u''
