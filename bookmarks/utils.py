from functools import wraps

from django.contrib.contenttypes.models import ContentType


def memoize(func, cache, num_args):
    """
    Wrap a function so that results for any argument tuple are stored in
    'cache'. Note that the args to the function must be usable as dictionary
    keys.

    Only the first num_args are considered when creating the key.
    """
    @wraps(func)
    def wrapper(*args):
        mem_args = args[:num_args]
        if mem_args in cache:
            return cache[mem_args]
        result = func(*args)
        cache[mem_args] = result
        return result
    return wrapper


_get_content_type_for_model_cache = {}


def get_content_type_for_model(model):
    return ContentType.objects.get_for_model(model)

get_content_type_for_model = memoize(get_content_type_for_model,
    _get_content_type_for_model_cache, 1)


def get_templates(instance, key, name, base='bookmarks'):
    """
    Return a list of template names based on given *instance* and
    bookmark *key*.

    For example, if *name* is 'form.html'::

        bookmarks/[app_name]/[model_name]/[key]/form.html
        bookmarks/[app_name]/[model_name]/form.html
        bookmarks/[app_name]/[key]/form.html
        bookmarks/[app_name]/form.html
        bookmarks/[key]/form.html
        bookmarks/form.html
    """
    app_label = instance._meta.app_label
    module_name = instance._meta.module_name
    return [
        '%s/%s/%s/%s/%s' % (base, app_label, module_name, key, name),
        '%s/%s/%s/%s' % (base, app_label, module_name, name),
        '%s/%s/%s/%s' % (base, app_label, key, name),
        '%s/%s/%s' % (base, app_label, name),
        '%s/%s/%s' % (base, key, name),
        '%s/%s' % (base, name),
    ]
