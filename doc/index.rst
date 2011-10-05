.. django-generic-bookmarks documentation master file, created by
   sphinx-quickstart on Thu Jul 28 11:18:57 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

django-generic-bookmarks
========================

This application provides bookmark's management functionality to 
a Django project.

Using bookmarks, for instance, it is possible to store user's favourited 
contents, or items that user follows, or arguments he wants to be notified
to him.

A bookmark connects users to Django contents in a generic way, without the need
to modify existing models tables, and *django-generic-bookmarks* exposes
a simple API to handle them, yet allowing the management of bookmarks
in complex scenarios too.

The bookmarks can be stored using different backends. 
The default one uses Django models to store user's preferences in the database,
but it is possible to develop customized backends, and the application, 
out of the box, includes also a MongoDB backend.

The source code for this app is hosted on 
https://bitbucket.org/frankban/django-generic-bookmarks

Contents
========

.. toctree::
   :maxdepth: 2

   getting_started
   handlers
   customization
   templatetags_api
   handlers_api
   forms_api
   backends_api
   models_api

Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
