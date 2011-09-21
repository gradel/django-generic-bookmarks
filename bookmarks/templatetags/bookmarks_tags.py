import re

from django import template
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from bookmarks import handlers, exceptions

register = template.Library()

def _parse_args(parser, token, expression):
    try:
        tag_name, arg = token.contents.split(None, 1)
    except ValueError:
        error = u"%r tag requires arguments" % token.contents.split()[0]
        raise template.TemplateSyntaxError, error
    # args validation
    match = expression.match(arg)
    if not match:
        error = u"%r tag has invalid arguments" % tag_name
        raise template.TemplateSyntaxError, error
    return match.groupdict()

def _get_templates(instance, name, default=None):
    app_label = instance._meta.app_label
    module_name = instance._meta.module_name
    return [
        '%s/%s/%s' % (app_label, module_name, name),
        '%s/%s' % (app_label, name),
        default or name,
    ]
 

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



BOOKMARK_EXPRESSION = re.compile(r"""
    ^ # begin of line
    for\s+(?P<instance>[\w.]+) # instance
    (\s+using\s+(?P<key>[\w.'"]+))? # key
    \s+as\s+(?P<varname>\w+) # varname
    $ # end of line
""", re.VERBOSE)

@register.tag
def bookmark(parser, token):
    """
    Return as a template variable a bookmark object for the given instance
    and key, and for current user.

    Usage:
    
    .. code-block:: html+django

        {% bookmark for *instance* [using *key*] as *varname* %}
    
    The key can be given hardcoded (surrounded by quotes) 
    or as a template variable.
    Note that if the key is not given, it will be generated using 
    the handler's *get_key* method, that, if not overridden, returns
    the default key. 

    The template variable will be None if:
        - the user is not authenticated
        - the instance is not bookmarkable
        - the bookmark does not exist
    """
    return BookmarkNode(**_parse_args(parser, token, BOOKMARK_EXPRESSION))

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


BOOKMARK_FORM_EXPRESSION = re.compile(r"""
    ^ # begin of line
    for\s+(?P<instance>[\w.]+) # instance
    (\s+using\s+(?P<key>[\w.'"]+))? # key
    (\s+as\s+(?P<varname>\w+))? # varname
    $ # end of line
""", re.VERBOSE)

@register.tag
def bookmark_form(parser, token):
    """
    Return, as html or as a template variable, a Django form to add or remove 
    a bookmark for the given instance and key, and for current user.

    Usage:
    
    .. code-block:: html+django

        {% bookmark_form for *instance* [using *key*] [as *varname*] %}
    
    The key can be given hardcoded (surrounded by quotes) 
    or as a template variable.
    Note that if the key is not given, it will be generated using 
    the handler's *get_key* method, that, if not overridden, returns
    the default key. 

    If the *varname* is used then it will be a context variable 
    containing the form.
    Otherwise the form is rendered using the first template found in the order
    that follows:

        [app_name]/[model_name]/bookmark_form.html
        [app_name]/bookmark_form.html
        bookmarks/form.html
    
    The *app_name* and *model_name* refer to the instance given as
    argument to this templatetag.

    Example:

    .. code-block:: html+django

        {% bookmark_form for myinstance using 'mykey' as bookmark_form %}
        <form action="{% url bookmarks_bookmark %}" method="post" accept-charset="UTF-8">
            {% csrf_token %}
            {{ form }}
            {% if user.is_authenticated %}
                <input type="submit" value="{% if form.bookmark_exist %}remove{% else %}add{% endif %}" />
            {% else %}
                Let the user log in.
            {% endif %}
        </form>

    The template variable (or the html) will be None if:
        - the user is not authenticated
        - the instance is not bookmarkable
        - the key is not allowed
    """
    return BookmarkFormNode(**_parse_args(parser, token, 
        BOOKMARK_FORM_EXPRESSION))

class BookmarkFormNode(BaseNode):

    template = 'bookmarks/form.html'

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
        print "NOW!"
        form = handler.get_form(request, instance, key)
        if self.varname is None:
            # rendering the form
            ctx = template.RequestContext(request, {
                'form': form,
                'login_url': settings.LOGIN_URL,
                'next': REDIRECT_FIELD_NAME,
            })
            template = _get_templates(instance, 'bookmark_form.html',
                default=self.template)
            return template.loader.render_to_string(template, ctx)
        else:
            # form as template variable
            context[self.varname] = form
            return u''
