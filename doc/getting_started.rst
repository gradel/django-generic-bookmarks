Getting started
===============

Requirements
~~~~~~~~~~~~

======  ======
Python  >= 2.5
Django  >= 1.3
======  ======

jQuery >= 1.4 is required if you want to take advantage of *AJAX* features 
described above and in :doc:`templatetags_api`.

Installation
~~~~~~~~~~~~

The Mercurial repository of the application can be cloned with this command::

    hg clone https://frankban@bitbucket.org/frankban/django-generic-bookmarks

The ``bookmarks`` package, included in the distribution, should be
placed on the ``PYTHONPATH``.

Otherwise you can just ``pip install django-generic-bookmarks``.

Configuration
~~~~~~~~~~~~~

Add the request context processor in your *settings.py*, e.g.::
    
    from django.conf.global_settings import TEMPLATE_CONTEXT_PROCESSORS
    TEMPLATE_CONTEXT_PROCESSORS += (
         'django.core.context_processors.request',
    )
    
Add ``'bookmarks'`` to the ``INSTALLED_APPS`` in your *settings.py*.

See :doc:`customization` section in this documentation for other settings 
options.

Add the bookmarks urls to your *urls.py*, e.g.::
    
    (r'^bookmarks/', include('bookmarks.urls')),
    
Time to create the needed database tables using *syncdb* management command::

    ./manage.py syncdb

Quickstart
~~~~~~~~~~

To allow a user to bookmark a Django model instance, the model must be
registered as *bookmarkable*, i.e. the system must know that instances
of that model can be bookmarked by users.

For example, if you have an *Article* model and you want users to add
articles to their favourited, you must register the model as bookmarkable,
e.g.::

For instance, having a *Film* model::

    from bookmarks.handlers import library
    library.register(Article)

You can register models anywhere you like. However, you'll need to make sure 
that the module it's in gets imported early on so that the model gets registered 
before any bookmark is saved by the user.
This makes your app's *models.py* a good place to put the above code.

Under the hood you have registered the *Article* model with a default 
bookmark handler. Handlers are Python classes encapsulating bookmarking options 
for a given model, while *library* is a singleton registry that stores handlers.
For a detailed explanation see :doc:`handlers`.

Now it's time to let your users add an article to his favourites, and this 
is possible using one of the provided templatetags.
In the code below we assume that *article* is the *Article* model instance.

.. code-block:: html+django

    {% load bookmarks_tags %}

    {% bookmark_form for myinstance %}
    
        
