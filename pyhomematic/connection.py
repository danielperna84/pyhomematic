import logging

from pyhomematic import _hm

LOG = logging.getLogger(__name__)


class HMConnection(object):
    def __init__(self,
                 local=_hm.LOCAL,
                 localport=_hm.LOCALPORT,
                 remotes=_hm.REMOTES,
                 remote=None,
                 remoteport=None,
                 devicefile=_hm.DEVICEFILE,
                 interface_id=_hm.INTERFACE_ID,
                 autostart=False,
                 eventcallback=False,
                 systemcallback=False,
                 resolvenames=None,
                 resolveparamsets=False,
                 rpcusername=None,
                 rpcpassword=None):
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

        if remote and remoteport:
            remotes['default']['ip'] = remote
            remotes['default']['port'] = remoteport
            if resolvenames:
                remotes['default']['resolvenames'] = resolvenames
            if rpcusername:
                remotes['default']['username'] = rpcusername
            if rpcpassword:
                remotes['default']['password'] = rpcpassword


        try:
            self._server = _hm.ServerThread(local=local,
                                            localport=localport,
                                            remotes=remotes,
                                            devicefile=devicefile,
                                            interface_id=interface_id,
                                            eventcallback=eventcallback,
                                            systemcallback=systemcallback,
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

            # Device-storage clear
            self.devices.clear()
            self.devices_all.clear()
            self.devices_raw.clear()
            self.devices_raw_dict.clear()

            return True
        except Exception as err:
            LOG.critical("Failed to stop server")
            LOG.debug(str(err))
            return False

    def reconnect(self):
        """Reinit all RPC proxy."""
        if self._server is not None:
            self._server.proxyInit()

    def getAllSystemVariables(self, remote):
        """Get all system variables from CCU / Homegear"""
        if self._server is not None:
            return self._server.getAllSystemVariables(remote)

    def getSystemVariable(self, remote, name):
        """Get single system variable from CCU / Homegear"""
        if self._server is not None:
            return self._server.getSystemVariable(remote, name)

    def deleteSystemVariable(self, remote, name):
        """Delete a system variable from CCU / Homegear"""
        if self._server is not None:
            return self._server.deleteSystemVariable(remote, name)

    def setSystemVariable(self, remote, name, value):
        """Set a system variable on CCU / Homegear"""
        if self._server is not None:
            return self._server.setSystemVariable(remote, name, value)

    def getServiceMessages(self, remote):
        """Get service messages from CCU / Homegear"""
        if self._server is not None:
            return self._server.getServiceMessages(remote)

    def rssiInfo(self, remote):
        """Get RSSI information for all devices from CCU / Homegear"""
        if self._server is not None:
            return self._server.rssiInfo(remote)

    def setInstallMode(self, remote, on=True, t=60, mode=1, address=None):
        """Activate or deactivate installmode on CCU / Homegear"""
        if self._server is not None:
            return self._server.setInstallMode(remote, on, t, mode, address)

    def getInstallMode(self, remote):
        """Get remaining time in seconds install mode is active from CCU / Homegear"""
        if self._server is not None:
            return self._server.getInstallMode(remote)

    def getAllMetadata(self, remote, address):
        """Get all metadata of device"""
        if self._server is not None:
            return self._server.getAllMetadata(remote, address)

    def getMetadata(self, remote, address, key):
        """Get metadata of device"""
        if self._server is not None:
            # pylint: disable=E1121
            return self._server.getAllMetadata(remote, address, key)

    def setMetadata(self, remote, address, key, value):
        """Set metadata of device"""
        if self._server is not None:
            # pylint: disable=E1121
            return self._server.getAllMetadata(remote, address, key, value)

    def deleteMetadata(self, remote, address, key):
        """Delete metadata of device"""
        if self._server is not None:
            # pylint: disable=E1121
            return self._server.deleteMetadata(remote, address, key)

    def listBidcosInterfaces(self, remote):
        """Return all available BidCos Interfaces"""
        if self._server is not None:
            return self._server.listBidcosInterfaces(remote)

    def homegearCheckInit(self, remote):
        """Check if proxy is still initialized"""
        if self._server is not None:
            return self._server.homegearCheckInit(remote)
