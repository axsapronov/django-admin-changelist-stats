# -*- coding: utf-8 -*-

import os
from distutils.core import setup

root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

data_files = []
for dirpath, dirnames, filenames in os.walk('admin_stats'):
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        continue
    elif filenames:
        for f in filenames:
            data_files.append(os.path.join(dirpath[len("admin_stats") + 1:], f))

version = "%s.%s" % __import__('admin_stats').VERSION[:2]

setup(name='django-admin-changelist-stats',
      version=version,
      description='Show stats and aggregation summaries in the Django admin changelist page.',
      author='Francesco Banconi',
      author_email='francesco.banconi@gmail.com',
      url='https://bitbucket.org/frankban/django-admin-changelist-stats/downloads',
      zip_safe=False,
      packages=[
          'admin_stats',
          'admin_stats.templatetags',
      ],
      package_data={'admin_stats': data_files},
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Framework :: Django',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Utilities'
      ],
      )
