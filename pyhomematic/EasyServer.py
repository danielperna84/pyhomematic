import sys

from pyhomematic import Server as _homematic
from pyhomematic.Server import LOCAL
from pyhomematic.Server import LOCALPORT
from pyhomematic.Server import REMOTE
from pyhomematic.Server import REMOTEPORT
from pyhomematic.Server import DEVICEFILE
from pyhomematic.Server import INTERFACE_ID

# Import device-storage
from pyhomematic.Server import devices
from pyhomematic.Server import devices_all
from pyhomematic.Server import devices_raw
from pyhomematic.Server import devices_raw_dict

import logging
LOG = logging.getLogger(__name__)
if sys.version_info.major < 3:
    LOG.critical("Python > 2 required!")
    raise Exception

Server = None


def start(*args, **kwargs):
    """
    Start the server thread if it wasn't created with autostart = True.
    """
    global Server
    if args:
        LOG.debug("args: %s" % str(args))
    if kwargs:
        LOG.debug("kwargs: %s" % str(kwargs))
    if Server:
        try:
            Server.start()
            Server.proxyInit()
            return True
        except Exception as err:
            LOG.critical("Failed to start server")
            LOG.debug(str(err))
            Server.stop()
            Server = None
            return False
    else:
        LOG.warning("No server available to start")
        return False


def stop(*args, **kwargs):
    """
    Stop the server thread.
    """
    global Server
    if args:
        LOG.debug("args: %s" % str(args))
    if kwargs:
        LOG.debug("kwargs: %s" % str(kwargs))
    if Server:
        try:
            Server.stop()
            Server = None
            return True
        except Exception as err:
            LOG.critical("Failed to stop server")
            LOG.debug(str(err))
            return False
    else:
        LOG.warning("No server available to stop")
        return False


def create_server(local=LOCAL,
                  localport=LOCALPORT,
                  remote=REMOTE,
                  remoteport=REMOTEPORT,
                  devicefile=DEVICEFILE,
                  interface_id=INTERFACE_ID,
                  autostart=False,
                  eventcallback=False,
                  systemcallback=False,
                  resolvenames=False,
                  resolveparamsets=False):
    """
    Helper-function to quickly create the server thread to which the CCU / Homegear will emit events.
    Without spacifying the remote-data we'll assume we're running Homegear on localhost on the default port.
    """
    global Server, LOCAL, LOCALPORT, REMOTE, REMOTEPORT, DEVICEFILE, INTERFACE_ID
    LOG.debug("create_server: Creating server object")

    try:
        Server = _homematic.ServerThread(local=local,
                                         localport=localport,
                                         remote=remote,
                                         remoteport=remoteport,
                                         devicefile=devicefile,
                                         interface_id=interface_id,
                                         eventcallback=eventcallback,
                                         systemcallback=systemcallback,
                                         resolvenames=resolvenames,
                                         resolveparamsets=resolveparamsets)

        LOCAL = _homematic.LOCAL
        LOCALPORT = _homematic.LOCALPORT
        REMOTE = _homematic.REMOTE
        REMOTEPORT = _homematic.REMOTEPORT
        DEVICEFILE = _homematic.DEVICEFILE
        INTERFACE_ID = _homematic.INTERFACE_ID
    except Exception as err:
        LOG.critical("Failed to create server")
        LOG.debug(str(err))

    if autostart:
        start()
