try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk('bookmarks'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len("bookmarks") + 1:], f))

version = "%s.%s" % __import__('bookmarks').VERSION[:2]


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        content = f.read()
    return content

setup(name='django-generic-bookmarks',
    version=version,
    description='Bookmarks, favourites, likes functionality for Django projects',
    long_description=read("README.rst"),
    author='Francesco Banconi',
    author_email='francesco.banconi@gmail.com',
    url='https://github.com/gradel/django-generic-bookmarks/',
    zip_safe=False,
    install_requires=[
        'future'
    ],
    packages=[
        'bookmarks',
        'bookmarks.templatetags',
        'bookmarks.views',
    ],
    package_data={'bookmarks': data_files},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities'
    ],
)
