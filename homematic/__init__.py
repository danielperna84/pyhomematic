import sys
import logging
LOG = logging.getLogger(__name__)
if sys.version_info.major < 3:
    LOG.warning("Python > 2 required!")
    raise Exception

from . import _server
from ._server import LOCAL
from ._server import LOCALPORT
from ._server import REMOTE
from ._server import REMOTEPORT
from ._server import DEVICEFILE
from ._server import INTERFACE_ID

def create_server(  local = LOCAL,
                    localport = LOCALPORT,
                    remote = REMOTE,
                    remoteport = REMOTEPORT,
                    devicefile = DEVICEFILE,
                    interface_id = INTERFACE_ID,
                    autostart = True,
                    eventcallback = False):
    """Helper-function to quickly create the server thread to which the CCU / Homegear will emit events.
    Without spacifying the remote-data we'll assume we're running Homegear on localhost on the default port."""
    
    LOG.debug("create_server: Creating server object")
    
    try:
        server = _server.ServerThread(  local = local,
                                        localport = localport,
                                        remote = remote,
                                        remoteport = remoteport,
                                        devicefile = devicefile,
                                        interface_id = interface_id,
                                        eventcallback = eventcallback)
    except Exception as err:
        LOG.critical("Failed to create server")
        LOG.debug(str(err))
        return False

    if autostart:
        try:
            server.start()
            server.proxyInit()
        except Exception as err:
            LOG.critical("Failed to start server")
            LOG.debug(str(err))
            server.stop()
            return False
    return server