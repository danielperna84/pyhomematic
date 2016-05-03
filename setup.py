from distutils.core import setup

def readme():
  with open('README.rst') as f:
    return f.read()

setup(
  name = 'pyhomematic',
  packages = ['pyhomematic'],
  version = '0.0.9',
  description = 'Homematic interface',
  long_description=readme(),
  author = 'Daniel Perna',
  author_email = 'danielperna84@gmail.com',
  license='MIT',
  url = 'https://github.com/danielperna84/pyhomematic',
  download_url = 'https://github.com/danielperna84/pyhomematic/tarball/0.0.9',
  keywords = ['homematic', 'automation', 'smarthome'],
  classifiers = ["Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "Intended Audience :: Developers"],
    platforms = "Any"
)
