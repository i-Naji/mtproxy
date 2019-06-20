try:
    # Use setuptools if available, for install_requires (among other things).
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('README.md') as f:
    long_description = f.read()


setup(name='MTProxy',
      version='0.1.3',
      description='Async Python MTProto Proxy ',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='http://github.com/i-Naji/mtproxy',
      license='MIT',
      author='Naji',
      python_requires='>=3.5',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Framework :: AsyncIO',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
          'Topic :: Internet :: Proxy Servers',
      ],
      keywords=(
          'mtproto proxy async asynchronous'
      ),
      packages=['mtproxy', 'mtproxy.utils', 'mtproxy.mtproto', 'mtproxy.proxy', 'mtproxy.proxy.streams', 'mtproxy.proxy.streams.wappers'],
      install_requires=['cryptography'],
      extras_require={
          'fast': ['uvloop']
      },
      entry_points={
          'console_scripts': [
              'mtproxy = mtproxy.__main__:main'
          ]
      })
