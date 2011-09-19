import unittest

from django.db import models
from django.contrib.auth.models import User

from bookmarks import exceptions, backends, handlers

class BookmarkTestModel(models.Model):
    name = models.CharField(max_length=8)
    
    def __unicode__(self):
        return unicode(self.name)


class BookmarkTestMixin(object):
    """
    Mixin for tests.
    """
    def create_user(self, username):
        return User.objects.create(username=username)
    
    def create_instance(self, name):
        return BookmarkTestModel.objects.create(name=name)

    def get_user_instance_key(self, prefix=''):
        user = self.create_user('%suser' % prefix)
        instance = self.create_instance('%sinstance' % prefix)
        key = '%skey' % prefix
        return user, instance, key

    def check_bookmark(self, bookmark, user, instance, key):
        self.assertEqual(bookmark.user, user)
        self.assertEqual(bookmark.content_object, instance)
        self.assertEqual(bookmark.key, key)

    def myAssertItemsEqual(self, a, b):
        """
        The most complete *assertItemsEqual* is only present in Python >= 2.7.
        """
        a_length = len(a)
        self.assertEqual(a_length, len(b))
        self.assertEqual(len([i for i in a if i in b]), a_length)

    def clean(self):
        BookmarkTestModel.objects.all().delete()
        User.objects.all().delete()


# BACKEND TESTS
    
class BaseBackendTest(BookmarkTestMixin):
    def test_add_bookmark(self):
        user, instance, key = self.get_user_instance_key('add')
        bookmark = self.backend.add(user, instance, key)
        self.check_bookmark(bookmark, user, instance, key)

    def test_add_same_bookmark(self):
        user, instance, key = self.get_user_instance_key('addsame')
        bookmark = self.backend.add(user, instance, key)
        self.assertRaises(exceptions.AlreadyExists, 
            self.backend.add, user, instance, key)

    def test_bookmark_exists(self):
        user, instance, key = self.get_user_instance_key('exists')
        self.assertFalse(self.backend.exists(user, instance, key))
        self.backend.add(user, instance, key)
        self.assertTrue(self.backend.exists(user, instance, key))

    def test_remove_bookmark(self):
        user, instance, key = self.get_user_instance_key('remove')
        self.backend.add(user, instance, key)
        self.backend.remove(user, instance, key)
        self.assertFalse(self.backend.exists(user, instance, key))

    def test_remove_missing_bookmark(self):
        user, instance, key = self.get_user_instance_key('missing')
        self.assertRaises(exceptions.DoesNotExist, 
            self.backend.remove, user, instance, key)

    def test_filter_bookmarks(self):
        user1 = self.create_user('user_filter_1')
        user2 = self.create_user('user_filter_2')
        instance1 = self.create_instance('instance_filter_1')
        instance2 = self.create_instance('instance_filter_2')
        key1, key2 = 'key_filter_1', 'key_filter_2'

        bookmark1 = self.backend.add(user1, instance1, key1)
        bookmark2 = self.backend.add(user2, instance1, key1)
        bookmark3 = self.backend.add(user1, instance2, key1)
        bookmark4 = self.backend.add(user1, instance2, key2)
        bookmark5 = self.backend.add(user2, instance1, key2)

        bookmarks_user1 = list(self.backend.filter(user=user1))
        bookmarks_user1_reversed = list(self.backend.filter(user=user1, 
            reversed=True))
        bookmarks_user2_key2 = list(self.backend.filter(user=user2, key=key2))
        bookmarks_instance1 = list(self.backend.filter(instance=instance1))
        bookmarks_instance1_reversed = list(self.backend.filter(
            instance=instance1, reversed=True))
        bookmarks_instance2_user1 = list(self.backend.filter(instance=instance2, 
            user=user1))
        bookmarks_instance1_user2_key1 = list(self.backend.filter(
            instance=instance1, user=user2, key=key1))
        bookmarks_instance1_user1_key2 = list(self.backend.filter(
            instance=instance1, user=user1, key=key2))
        bookmarks_model = list(self.backend.filter(model=BookmarkTestModel))
        
        self.assertEqual(bookmarks_user1, [bookmark1, bookmark3, bookmark4])
        self.assertEqual(bookmarks_user1_reversed, 
            [bookmark4, bookmark3, bookmark1])
        self.assertEqual(bookmarks_user2_key2, [bookmark5])
        self.assertEqual(bookmarks_instance1, [bookmark1, bookmark2, bookmark5])
        self.assertEqual(bookmarks_instance1_reversed, 
            [bookmark5, bookmark2, bookmark1])
        self.assertEqual(bookmarks_instance2_user1, [bookmark3, bookmark4])
        self.assertEqual(bookmarks_instance1_user2_key1, [bookmark2])
        self.assertEqual(bookmarks_instance1_user1_key2, [])
        self.assertEqual(len(bookmarks_model), 5)

    def test_get_bookmark(self):
        user1 = self.create_user('user_get_1')
        user2 = self.create_user('user_get_2')
        instance1 = self.create_instance('instance_get_1')
        instance2 = self.create_instance('instance_get_2')
        key = 'key_get'

        bookmark1 = self.backend.add(user1, instance1, key)
        bookmark2 = self.backend.add(user2, instance1, key)

        self.assertEqual(self.backend.get(user2, instance1, key), bookmark2)
        self.assertRaises(exceptions.DoesNotExist, 
            self.backend.get, user1, instance2, key)

    def test_remove_all_bookmarks_for_instance(self):
        user1 = self.create_user('user_remove_all_1')
        user2 = self.create_user('user_remove_all_2')
        instance1 = self.create_instance('instance_remove_all_1')
        instance2 = self.create_instance('instance_remove_all_2')
        key1, key2 = 'key_remove_all_1', 'key_remove_all_2'

        self.backend.add(user1, instance1, key1)
        self.backend.add(user2, instance1, key1)
        self.backend.add(user1, instance1, key2)
        remaining = self.backend.add(user1, instance2, key1)

        self.backend.remove_all_for(instance1)

        bookmarks_instance1 = list(self.backend.filter(instance=instance1))
        bookmarks_instance2 = list(self.backend.filter(instance=instance2))

        self.assertEqual(bookmarks_instance1, [])
        self.assertEqual(bookmarks_instance2, [remaining])

    def test_bookmark_model(self):
        user, instance, key = self.get_user_instance_key('model')
        self.backend.add(user, instance, key)
        bookmarks = list(self.backend.filter(user=user))
        self.assertTrue(isinstance(bookmarks[0], self.backend.get_model()))

    
class DefaultBackendTestCase(unittest.TestCase, BaseBackendTest):
    def setUp(self):
        self.backend = backends.ModelBackend()

    def tearDown(self):
        self.clean()


try:
    mongo_backend = backends.MongoBackend()
except ImportError:
    print "Skipping mongo backend tests: you must pip install mongoengine."
except exceptions.MongodbConnectionError:
    print "Skipping mongo backend tests: unable to connect to mongodb."
else:
    class MongoBackendTestCase(unittest.TestCase, BaseBackendTest):            
        def setUp(self):
            self.backend = mongo_backend

        def tearDown(self):
            self.clean()
            self.backend.db.drop_collection('bookmark')


        def test_filter_bookmarks(self):
            pass

        def test_bookmark_model(self):
            pass


# REGISTRY TESTS

class RegistryTestCase(unittest.TestCase, BookmarkTestMixin):
    def setUp(self):
        self.library = handlers.Registry()

    def _get_handler(self):
        class CustomHandler(handlers.Handler):
            pass
        return CustomHandler

    def test_registry(self):
        instance = self.create_instance('handlers')
        model = type(instance)

        self.library.register(model)

        handler = self.library.get_handler(model)
        self.assertTrue(isinstance(handler, handlers.Handler))
        
        self.assertRaises(exceptions.AlreadyHandled, self.library.register,
            model)
        
        self.library.unregister(type(instance))
        self.assertRaises(exceptions.NotHandled, self.library.unregister,
            model)

        self.assertEqual(self.library.get_handler(User), None)
        
        custom_handler = self._get_handler()
        key = 'custom'
        self.library.register([User, model], custom_handler, default_key=key)

        handler = self.library.get_handler(self.create_user('handlers'))
        self.assertTrue(isinstance(handler, custom_handler))
        self.assertEqual(handler.default_key, key)

# TODO: forms, views and templatetag tests
