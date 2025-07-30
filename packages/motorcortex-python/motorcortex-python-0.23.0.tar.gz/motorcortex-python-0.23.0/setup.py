#!/usr/bin/python3

#
#   Developer : Alexey Zakharov (alexey.zakharov@vectioneer.com)
#   All rights reserved. Copyright (c) 2020 VECTIONEER.
#


from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

exec(open('motorcortex/version.py').read())

setup(name='motorcortex-python',
      version=__version__,
      description='Python bindings for Motorcortex Engine',
      long_description=long_description,
      long_description_content_type="text/markdown",
      author='Alexey Zakharov',
      author_email='alexey.zakharov@vectioneer.com',
      url='https://www.motorcortex.io',
      license='MIT',
      packages=['motorcortex'],
      install_requires=['pynng==0.8.*',
                        'protobuf==3.20.*'],
      include_package_data=True,
      )
