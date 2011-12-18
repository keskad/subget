#!/usr/bin/python
from distutils.core import setup

setup(name='subget',
      version='1.0.1',
      package_dir={'': 'src'},      
      packages=['subgetlib', 'subgetcore']
     )
