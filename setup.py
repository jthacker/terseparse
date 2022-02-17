from setuptools import setup

# Load __version__ without importing it (avoids race condition with build)
exec(open('terseparse/version.py').read())

test_deps = [
    'pytest'
]

extras = {
    'test': test_deps
}

setup(name='terseparse',
      description='A minimal boilerplate, composeable wrapper for argument parsing',
      packages=['terseparse'],
      version=__version__,
      url='https://github.com/jthacker/terseparse',
      download_url='https://github.com/jthacker/terseparse/archive/v{}.tar.gz'.format(__version__),
      author='jthacker',
      author_email='thacker.jon@gmail.com',
      keywords=['argument', 'parsing'],
      classifiers=[],
      install_requires=[
          'six >= 1.16'
          ],
      tests_require=test_deps,
      setup_requires=[
          'pytest-runner'
          ],
      extras_require=extras,
      long_description="""
How to Install
--------------

.. code:: bash

    pip install terseparse

""")
