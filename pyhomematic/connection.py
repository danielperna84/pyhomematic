import sys
import logging

from pyhomematic import _hm

LOG = logging.getLogger(__name__)


class HMConnection(object):
    def __init__(self,
                 local=_hm.LOCAL,
                 localport=_hm.LOCALPORT,
                 remote=_hm.REMOTE,
                 remoteport=_hm.REMOTEPORT,
                 devicefile=_hm.DEVICEFILE,
                 interface_id=_hm.INTERFACE_ID,
                 autostart=False,
                 eventcallback=False,
                 systemcallback=False,
                 resolvenames=False,
                 resolveparamsets=False,
                 rpcusername=_hm.RPC_USERNAME,
                 rpcpassword=_hm.RPC_PASSWORD):
        """
        Helper function to quickly create the server thread to which the CCU / Homegear will emit events.
        Without specifying the remote data we'll assume we're running Homegear on localhost on the default port.
        """
        LOG.debug("HMConnection: Creating server object")

        # Device-storage
        self.devices = _hm.devices
        self.devices_all = _hm.devices_all
        self.devices_raw = _hm.devices_raw
        self.devices_raw_dict = _hm.devices_raw_dict

        try:
            self._server = _hm.ServerThread(local=local,
                                            localport=localport,
                                            remote=remote,
                                            remoteport=remoteport,
                                            devicefile=devicefile,
                                            interface_id=interface_id,
                                            eventcallback=eventcallback,
                                            systemcallback=systemcallback,
                                            resolvenames=resolvenames,
                                            rpcusername=rpcusername,
                                            rpcpassword=rpcpassword,
                                            resolveparamsets=resolveparamsets)

        except Exception as err:
            LOG.critical("Failed to create server")
            LOG.debug(str(err))

        if autostart:
            self.start()

    def start(self, *args, **kwargs):
        """
        Start the server thread if it wasn't created with autostart = True.
        """
        if args:
            LOG.debug("args: %s" % str(args))
        if kwargs:
            LOG.debug("kwargs: %s" % str(kwargs))
        try:
            self._server.start()
            self._server.proxyInit()
            return True
        except Exception as err:
            LOG.critical("Failed to start server")
            LOG.debug(str(err))
            self._server.stop()
            return False

    def stop(self, *args, **kwargs):
        """
        Stop the server thread.
        """
        if args:
            LOG.debug("args: %s" % str(args))
        if kwargs:
            LOG.debug("kwargs: %s" % str(kwargs))
        try:
            self._server.stop()
            self._server = None
            return True
        except Exception as err:
            LOG.critical("Failed to stop server")
            LOG.debug(str(err))
            return False
