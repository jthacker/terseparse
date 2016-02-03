from distutils.core import setup
from terseparse import __version__

setup(name='terseparse',
      description='A minimal boilerplate, composeable wrapper for argument parsing',
      packages=['terseparse'],
      version=__version__,
      url='https://github.com/jthacker/terseparse',
      download_url='https://github.com/jthacker/terseparse/archive/v1.0.3.tar.gz',
      author='jthacker',
      author_email='thacker.jon@gmail.com',
      keywords=['argument', 'parsing'],
      classifiers=[],
      install_requires=[],
      long_description="""
How to Install
--------------

.. code:: bash

    pip install terseparse

""")
