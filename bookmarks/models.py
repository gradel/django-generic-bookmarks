import string

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

from bookmarks import managers

class Bookmark(models.Model):
    """
    A user's bookmark for a content object.
    """
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    key = models.CharField(max_length=16)
    
    user = models.ForeignKey(User, blank=True, null=True, 
        related_name='bookmarks')

    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    
    # manager
    objects = managers.BookmarksManager()
    
    class Meta:
        unique_together = ('content_type', 'object_id', 'key', 'user')

    def __unicode__(self):
        return u'Bookmark for %s by %s' % (self.content_object, self.user)
        
        
# IN BULK SELECT QUERIES
    
def annotate_bookmarks(queryset_or_model, key, user, attr='is_bookmarked'):
    """
    Annotate *queryset_or_model* with bookmarks, in order to retreive from
    the database all bookmark values in bulk.
    
    The first argument *queryset_or_model* must be, of course, a queryset
    or a Django model object. The argument *key* is the bookmark key.
    
    The bookmarks are filtered using given *user*.
    
    A boolean is inserted in an attr named *attr* (default='is_bookmarked')
    of each object in the generated queryset.
    
    Usage example::
    
        for article in annotate_bookmarks(Article.objects.all(), 'favourited', 
            myuser, attr='has_a_bookmark'):
            if article.has_a_bookmark:
                print u"Article %s is favourited by user %s" (article, myuser)
    """
    # getting the queryset
    if isinstance(queryset_or_model, models.base.ModelBase):
        queryset = queryset_or_model.objects.all()
    else:
        queryset = queryset_or_model
    # preparing arguments for *extra* query
    opts = queryset.model._meta
    content_type = managers.get_content_type_for_model(queryset.model)
    mapping = {
        'bookmark_table': Bookmark._meta.db_table,
        'model_table': opts.db_table,
        'model_pk_name': opts.pk.name,
        'content_type_id': content_type.pk,
    }
    # building base query
    template = """
    SELECT id FROM ${bookmark_table} WHERE 
    ${bookmark_table}.object_id = ${model_table}.${model_pk_name} AND 
    ${bookmark_table}.content_type_id = ${content_type_id} AND
    ${bookmark_table}.user_id = %s AND
    ${bookmark_table}.key = %s
    """
    select = {score: string.Template(template).substitute(mapping)}
    return queryset.extra(select=select, select_params=[user.pk, key])
    

# ABSTRACT MODELS
    
class BookmarkedModel(models.Model):
    """
    Mixin for bookmarkable models.
    """
    bookmarks = generic.GenericRelation(Bookmark)
    
    class Meta:
        abstract = True 
