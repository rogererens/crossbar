###############################################################################
##
##  Copyright (C) 2011-2014 Tavendo GmbH
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Affero General Public License, version 3,
##  as published by the Free Software Foundation.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
##  GNU Affero General Public License for more details.
##
##  You should have received a copy of the GNU Affero General Public License
##  along with this program. If not, see <http://www.gnu.org/licenses/>.
##
###############################################################################


from __future__ import absolute_import

from distutils import log

try:
   from ez_setup import use_setuptools
   use_setuptools()
except Exception as e:
   log.warn("ez_setup failed: {0}".format(e))
finally:
   from setuptools import setup, find_packages


install_requires = ['setuptools>=2.2',
                    'zope.interface>=3.6.0',
                    'twisted>=twisted-13.2',
                    'autobahn[twisted]>=0.8.7',
                    'cryptography>=0.3',
                    'pyOpenSSL>=0.14',
                    'psutil>=1.2.1',
                    'msgpack-python>=0.4.1',
                    'jinja2>=2.7.2']

import sys
if not sys.platform.startswith('win'):
   install_requires.append('setproctitle>=1.1.8')



## Get package version and docstring from crossbar/__init__.py
##
import re
PACKAGE_FILE = "crossbar/__init__.py"
initfile = open(PACKAGE_FILE, "rt").read()

VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, initfile, re.M)
if mo:
   verstr = mo.group(1)
else:
   raise RuntimeError("Unable to find version string in {}.".format(PACKAGE_FILE))

DSRE = r"__doc__ = \"\"\"(.*)\"\"\""
mo = re.search(DSRE, initfile, re.DOTALL)
if mo:
   docstr = mo.group(1)
else:
   raise RuntimeError("Unable to find doc string in {}.".format(PACKAGE_FILE))


setup (
   name = 'crossbar',
   version = verstr,
   description = 'Crossbar.io - Polyglot application router',
   long_description = docstr,
   author = 'Tavendo GmbH',
   author_email = 'autobahnws@googlegroups.com',
   url = 'http://crossbar.io/',
   platforms = ('Any'),
   install_requires = install_requires,
   extras_require = {
      'oracle': ["cx_Oracle>=5.1.2"],
      'postgres': ["psycopg2>=2.5.1"]
   },
   entry_points = {
      'console_scripts': [
         'crossbar = crossbar.node.cli:run'
      ]},
   #packages = ['crossbar'],
   packages = find_packages(),
   include_package_data = True,
   data_files = [('.', ['LICENSE'])],
   zip_safe = False,
   ## http://pypi.python.org/pypi?%3Aaction=list_classifiers
   ##
   classifiers = ["License :: OSI Approved :: GNU Affero General Public License v3",
                  "Development Status :: 3 - Alpha",
                  "Environment :: Console",
                  "Framework :: Twisted",
                  "Intended Audience :: Developers",
                  "Operating System :: OS Independent",
                  "Programming Language :: Python",
                  "Topic :: Internet",
                  "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
                  "Topic :: Communications",
                  "Topic :: Database",
                  "Topic :: Home Automation",
                  "Topic :: Software Development :: Libraries",
                  "Topic :: Software Development :: Libraries :: Application Frameworks",
                  "Topic :: Software Development :: Embedded Systems",
                  "Topic :: System :: Distributed Computing",
                  "Topic :: System :: Networking"],
   keywords = 'crossbar router autobahn autobahn.ws websocket realtime rfc6455 wamp rpc pubsub oracle postgres postgresql'
)
