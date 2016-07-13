import os
from setuptools import setup, find_packages

def readme():
  with open('README.rst') as f:
    return f.read()

PACKAGE_NAME = 'pyhomematic'
HERE = os.path.abspath(os.path.dirname(__file__))
VERSION = '0.1.9'

PACKAGES = find_packages(exclude=['tests', 'tests.*', 'dist', 'ccu', 'build'])

REQUIRES = []

setup(
    name=PACKAGE_NAME,
    version=VERSION,
    license='MIT License',
    url='https://github.com/danielperna84/pyhomematic',
    download_url='https://github.com/danielperna84/pyhomematic/tarball/'+VERSION,
    author='Daniel Perna',
    author_email='danielperna84@gmail.com',
    description='Homematic interface',
    packages=PACKAGES,
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=REQUIRES,
    keywords=['home', 'automation', 'homematic', 'smarthome'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Topic :: Home Automation'
    ],
)
