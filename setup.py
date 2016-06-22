from setuptools import setup

# Load __version__ without importing it (avoids race condition with build)
exec(open('terseparse/version.py').read())

setup(name='terseparse',
      description='A minimal boilerplate, composeable wrapper for argument parsing',
      packages=['terseparse'],
      version=__version__,
      url='https://github.com/jthacker/terseparse',
      download_url='https://github.com/jthacker/terseparse/archive/v1.1.0.tar.gz',
      author='jthacker',
      author_email='thacker.jon@gmail.com',
      keywords=['argument', 'parsing'],
      classifiers=[],
      install_requires=[
          'six >= 1.10.0'
          ],
      tests_require=[
          'pytest'
          ],
      setup_requires=[
          'pytest-runner'
          ],
      long_description="""
How to Install
--------------

.. code:: bash

    pip install terseparse

""")
