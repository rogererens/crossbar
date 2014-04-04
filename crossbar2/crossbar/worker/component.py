###############################################################################
##
##  Copyright (C) 2014 Tavendo GmbH
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

from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import ComponentConfig

from twisted.python import log
import pkg_resources



class ComponentModule:
   """
   """

   def __init__(self, session, pid, cbdir):
      self._session = session
      self._pid = pid
      self._cbdir = cbdir
      self._client = None

      self.debug = self._session.factory.options.debug

      session.register(self.start_class, 'crossbar.node.module.{}.component.start_class'.format(self._pid))
      session.register(self.start_wamplet, 'crossbar.node.module.{}.component.start_wamplet'.format(self._pid))


   def start_wamplet(self, wamplet, router):
      """
      Starts a WAMPlet in this component container.
      """
      try:
         dist = wamplet['dist']
         name = wamplet['entry']

         if self.debug:
            log.msg("Worker {}: starting WAMPlet '{}/{}' in realm '{}' ..".format(self._pid, dist, name, router['realm']))

         ## make is supposed to make instances of ApplicationSession
         make = pkg_resources.load_entry_point(dist, 'autobahn.twisted.wamplet', name)

      except Exception as e:
         log.msg("Worker {}: failed to import class - {}".format(e))
         raise ApplicationError("crossbar.error.class_import_failed", str(e))
      else:
         return self._start(make, wamplet.get('extra', None), router)


   def start_class(self, klass, router):
      """
      Starts a class in this component container.
      """
      try:
         klassname = klass['name']

         if self.debug:
            log.msg("Worker {}: starting class '{}' in realm '{}' ..".format(self._pid, klassname, router['realm']))

         import importlib
         c = klassname.split('.')
         mod, kls = '.'.join(c[:-1]), c[-1]
         app = importlib.import_module(mod)

         ## make is supposed to be of class ApplicationSession
         make = getattr(app, kls)

      except Exception as e:
         log.msg("Worker {}: failed to import class - {}".format(e))
         raise ApplicationError("crossbar.error.class_import_failed", str(e))
      else:
         return self._start(make, klass.get('extra', None), router)


   def _start(self, make, extra, router):

      def create():
         cfg = ComponentConfig(realm = router['realm'], extra = extra)
         c = make(cfg)
         return c

      ## create a WAMP-over-WebSocket transport client factory
      ##
      from autobahn.twisted.websocket import WampWebSocketClientFactory
      transport_factory = WampWebSocketClientFactory(create, router['url'], debug = self.debug)
      transport_factory.setProtocolOptions(failByDrop = False)

      ## start a WebSocket client from an endpoint
      ##
      from twisted.internet import reactor
      from twisted.internet.endpoints import TCP4ClientEndpoint, SSL4ClientEndpoint, UNIXClientEndpoint
      from twisted.internet.endpoints import clientFromString

      from crossbar.twisted.tlsctx import TlsClientContextFactory


      if False:
         self._client = clientFromString(reactor, router['endpoint'])
      else:
         try:
            endpoint_config = router.get('endpoint')

            ## a TCP4 endpoint
            ##
            if endpoint_config['type'] == 'tcp':

               ## the host to connect ot
               ##
               host = str(endpoint_config['host'])

               ## the port to connect to
               ##
               port = int(endpoint_config['port'])

               ## connection timeout in seconds
               ##
               timeout = int(endpoint_config.get('timeout', 10))

               if 'tls' in endpoint_config:

                  ctx = TlsClientContextFactory()

                  ## create a TLS client endpoint
                  ##
                  self._client = SSL4ClientEndpoint(reactor,
                                                    host,
                                                    port,
                                                    ctx,
                                                    timeout = timeout)
               else:
                  ## create a non-TLS client endpoint
                  ##
                  self._client = TCP4ClientEndpoint(reactor,
                                                    host,
                                                    port,
                                                    timeout = timeout)

            ## a Unix Domain Socket endpoint
            ##
            elif endpoint_config['type'] == 'unix':

               ## the path
               ##
               path = os.path.abspath(os.path.join(self._cbdir, endpoint_config['path']))

               ## connection timeout in seconds
               ##
               timeout = int(endpoint_config['type'].get('timeout', 10))

               ## create the endpoint
               ##
               self._client = UNIXClientEndpoint(reactor, path, timeout = timeout)

            else:
               raise ApplicationError("crossbar.error.invalid_configuration", "invalid endpoint type '{}'".format(endpoint_config['type']))

         except Exception as e:
            log.msg("endpoint creation failed: {}".format(e))
            raise e


      retry = True
      retryDelay = 1000

      def try_connect():
         if self.debug:
            log.msg("Worker {}: connecting to router ..".format(self._pid))

         d = self._client.connect(transport_factory)

         def success(res):
            if self.debug:
               log.msg("Worker {}: client connected to router".format(self._pid))

         def error(err):
            log.msg("Worker {}: client failed to connect to router - {}".format(self._pid, err))
            if retry:
               log.msg("Worker {}: retrying in {} ms".format(self._pid, retryDelay))
               reactor.callLater(float(retryDelay) / 1000., try_connect)
            else:
               log.msg("Worker {}: giving up.".format(seld._pid))

         d.addCallbacks(success, error)

      try_connect()