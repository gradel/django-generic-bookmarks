from django.utils.functional import memoize
from django.contrib.contenttypes.models import ContentType

_get_content_type_for_model_cache = {}

def get_content_type_for_model(model):
    return ContentType.objects.get_for_model(model)

get_content_type_for_model = memoize(get_content_type_for_model, 
    _get_content_type_for_model_cache, 1)

def get_templates(instance, name, default=None):
    app_label = instance._meta.app_label
    module_name = instance._meta.module_name
    return [
        '%s/%s/%s' % (app_label, module_name, name),
        '%s/%s' % (app_label, name),
        default or name,
    ]
