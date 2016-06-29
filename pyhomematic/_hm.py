import os
import threading
import json
import urllib.request
import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import logging
from pyhomematic import devicetypes
from pyhomematic.devicetypes.generic import HMChannel

LOG = logging.getLogger(__name__)

# Constants
LOCAL = '127.0.0.1'
LOCALPORT = 7080
REMOTE = '127.0.0.1'
REMOTEPORT = 2001
DEVICEFILE = False  # e.g. devices.json
INTERFACE_ID = 'pyhomematic'
XML_API_URL = '/config/xmlapi/devicelist.cgi'
JSONRPC_URL = '/api/homematic.cgi'
RPC_USERNAME = 'Admin'
RPC_PASSWORD = ''


# Device-storage
devices = {}
devices_all = {}
devices_raw = []
devices_raw_dict = {}
working = False


# Object holding the methods the XML-RPC server should provide.
class RPCFunctions(object):
    def __init__(self,
                 devicefile=DEVICEFILE,
                 proxy=False,
                 remote_ip=False,
                 remote_port=False,
                 eventcallback=False,
                 systemcallback=False,
                 resolvenames=False,
                 resolveparamsets=False,
                 rpcusername=False,
                 rpcpassword=False):
        global devices, devices_all, devices_raw, devices_raw_dict
        LOG.debug("RPCFunctions.__init__")
        self.devicefile = devicefile
        self.eventcallback = eventcallback
        self.systemcallback = systemcallback
        self.resolvenames = resolvenames
        self.resolveparamsets = resolveparamsets
        self.rpcusername = rpcusername
        self.rpcpassword = rpcpassword

        # Only required to access device names from Homematic CCU
        self._remote_ip = remote_ip
        self._remote_port = remote_port

        # The methods need to know about the proxy to be able to pass it on to the device-objects
        self._proxy = proxy

        # Devices w/o channels will be accessible using the device-address as the key
        self.devices = devices
        # Devices including channels will be accessible using the device-address + channel as the key
        self.devices_all = devices_all

        # The plain JSON (actually dicts) are stored as well
        self._devices_raw_dict = devices_raw_dict
        self._devices_raw = devices_raw

        # If there are stored devices, we load them instead of getting them from the server.
        if self.devicefile:
            LOG.debug("RPCFunctions.__init__: devicefile = %s" % (self.devicefile, ))
            if os.path.isfile(self.devicefile):
                with open(self.devicefile, 'r') as f:
                    fc = f.read()
                    if fc:
                        self._devices_raw = json.loads(fc)

        for device in self._devices_raw:
            self._devices_raw_dict[device['ADDRESS']] = device
        LOG.debug("RPCFunctions.__init__: devices_raw = %s" % (str(self._devices_raw), ))

        # Create the "interactive" device-objects and store them in self._devices and self._devices_all
        self.createDeviceObjects()

    def createDeviceObjects(self):
        """Transform the raw device descriptions into instances of devicetypes.generic.HMDevice or availabe subclass."""
        global working

        working = True
        # First create parent object
        for dev in self._devices_raw:
            if not dev['PARENT']:
                if not dev['ADDRESS'] in self.devices_all:
                    if dev['TYPE'] in devicetypes.SUPPORTED:
                        deviceObject = devicetypes.SUPPORTED[dev['TYPE']](dev, self._proxy, self.resolveparamsets)
                        LOG.debug("RPCFunctions.createDeviceObjects: create %s  as SUPPORTED device for %s" % (dev['ADDRESS'], dev['TYPE']))
                    else:
                        deviceObject = devicetypes.UNSUPPORTED(dev, self._proxy, self.resolveparamsets)
                        LOG.debug("RPCFunctions.createDeviceObjects: create %s  as UNSUPPORTED device for %s" % (dev['ADDRESS'], dev['TYPE']))
                    self.devices_all[dev['ADDRESS']] = deviceObject
                    self.devices[dev['ADDRESS']] = deviceObject
        # Then create all children for parent
        for dev in self._devices_raw:
            if dev['PARENT']:
                if not dev['ADDRESS'] in self.devices_all:
                    deviceObject = HMChannel(dev, self._proxy, self.resolveparamsets)
                    self.devices_all[dev['ADDRESS']] = deviceObject
                    self.devices[dev['PARENT']].CHANNELS[dev['INDEX']] = deviceObject
        if self.devices_all and self.resolvenames:
            self.addDeviceNames()
        working = False
        if self.systemcallback:
            self.systemcallback('createDeviceObjects')
        return True

    def error(self, interface_id, errorcode, msg):
        """When some error occurs the CCU / Homegear will send it's error message here"""
        LOG.debug("RPCFunctions.error: interface_id = %s, errorcode = %i, message = %s" % (interface_id, int(errorcode), str(msg)))
        if self.systemcallback:
            self.systemcallback('error', interface_id, errorcode, msg)
        return True

    def saveDevices(self):
        """We save known devices into a json-file so we don't have to work through the whole list of devices the CCU / Homegear presents us"""
        LOG.debug("RPCFunctions.saveDevices: devicefile: %s, _devices_raw: %s" % (self.devicefile, str(self._devices_raw)))
        if self.devicefile:
            try:
                with open(self.devicefile, 'w') as df:
                    df.write(json.dumps(self._devices_raw))
                return True
            except Exception as err:
                LOG.debug("RPCFunctions.saveDevices: Exception saving _devices_raw: %s" % (str(err), ))
                LOG.warning("RPCFunctions.saveDevices: Exception saving _devices_raw")
                return False
        else:
            return True

    def event(self, interface_id, address, value_key, value):
        """If a device emits some sort event, we will handle it here."""
        LOG.debug("RPCFunctions.event: interface_id = %s, address = %s, value_key = %s, value = %s" % (interface_id, address, value_key.upper(), str(value)))
        self.devices_all[address].event(interface_id, value_key.upper(), value)
        if self.eventcallback:
            self.eventcallback(interface_id=interface_id, address=address, value_key=value_key.upper(), value=value)
        return True

    def listDevices(self, interface_id):
        """The CCU / Homegear asks for devices known to our XML-RPC server. We respond to that request using this method."""
        LOG.debug("RPCFunctions.listDevices: interface_id = %s, _devices_raw = %s" % (interface_id, str(self._devices_raw)))
        if self.systemcallback:
            self.systemcallback('listDevices', interface_id)
        return self._devices_raw

    def newDevices(self, interface_id, dev_descriptions):
        """The CCU / Homegear informs us about newly added devices. We react on that and add those devices as well."""
        LOG.debug("RPCFunctions.newDevices: interface_id = %s, dev_descriptions = %s" % (interface_id, str(dev_descriptions)))
        for d in dev_descriptions:
            self._devices_raw.append(d)
            self._devices_raw_dict[d['ADDRESS']] = d
        self.saveDevices()
        self.createDeviceObjects()
        if self.systemcallback:
            self.systemcallback('newDevices', interface_id, dev_descriptions)
        return True

    def deleteDevices(self, interface_id, addresses):
        """The CCU / Homegear informs us about removed devices. We react on that and remove those devices as well."""
        LOG.debug("RPCFunctions.deleteDevices: interface_id = %s, addresses = %s" % (interface_id, str(addresses)))
        #TODO: remove known device objects as well
        self._devices_raw = [device for device in self._devices_raw if not device['ADDRESS'] in addresses]
        self.saveDevices()
        if self.systemcallback:
            self.systemcallback('deleteDevice', interface_id, addresses)
        return True

    def updateDevice(self, interface_id, address, hint):
        LOG.debug("RPCFunctions.updateDevice: interface_id = %s, address = %s, hint = %s" % (interface_id, address, str(hint)))
        #TODO: Implement updateDevice
        if self.systemcallback:
            self.systemcallback('updateDevice', interface_id, address, hint)
        return True

    def replaceDevice(self, interface_id, oldDeviceAddress, newDeviceAddress):
        LOG.debug("RPCFunctions.replaceDevice: interface_id = %s, oldDeviceAddress = %s, newDeviceAddress = %s" % (interface_id, oldDeviceAddress, newDeviceAddress))
        #TODO: Implement replaceDevice
        if self.systemcallback:
            self.systemcallback('replaceDevice', interface_id, oldDeviceAddress, newDeviceAddress)
        return True

    def readdedDevice(self, interface_id, addresses):
        LOG.debug("RPCFunctions.readdedDevices: interface_id = %s, addresses = %s" % (interface_id, str(addresses)))
        #TODO: Implement readdedDevice
        if self.systemcallback:
            self.systemcallback('readdedDevice', interface_id, addresses)
        return True

    def jsonRpcPost(self, method, params={}, timeout=5):
        LOG.debug("RPCFunctions.jsonRpcPost: Method: %s" % method)
        try:
            payload = json.dumps({"method": method, "params": params, "jsonrpc": "1.1", "id": 0}).encode('utf-8')

            headers = {"Content-Type": 'application/json',
                       "Content-Length": len(payload)}
            apiendpoint = "http://%s%s" % (self._remote_ip, JSONRPC_URL)
            LOG.debug("RPCFunctions.jsonRpcPost: API-Endpoint: %s" % apiendpoint)
            req = urllib.request.Request(apiendpoint, payload, headers)
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                return json.loads(resp.read().decode('utf-8'))
            else:
                LOG.error("RPCFunctions.jsonRpcPost: Status: %i" % resp.status)
                return {'error': resp.status, 'result': {}}
        except Exception as err:
            LOG.error("RPCFunctions.jsonRpcPost: Exception: %s" % str(err))
            return {'error': str(err), 'result': {}}

    def addDeviceNames(self):
        """ If XML-API (http://www.homematic-inside.de/software/addons/item/xmlapi) is installed on CCU this function will add names to CCU devices """
        LOG.debug("RPCFunctions.addDeviceNames")

        #First try to get names from metadata when nur credentials are set
        if self.resolvenames == 'metadata':
            for address in self.devices:
                try:
                    name = self.devices[address]._proxy.getMetadata(address, 'NAME')
                    self.devices[address].NAME = name
                    for address, device in self.devices[address].CHANNELS.items():
                        device.NAME = name
                        self.devices_all[device.ADDRESS].NAME = name
                except Exception as err:
                    LOG.debug("RPCFunctions.addDeviceNames: Unable to get name for %s from metadata." % str(address))

        # Then try to get names via JSON-RPC
        elif self.resolvenames == 'json' and self.rpcusername and self.rpcpassword:
            LOG.debug("RPCFunctions.addDeviceNames: Getting names via JSON-RPC")
            try:
                session = False
                params = {"username": self.rpcusername, "password": self.rpcpassword}
                response = self.jsonRpcPost("Session.login", params)
                if response['error'] is None and response['result']:
                    session = response['result']

                if not session:
                    LOG.warning("RPCFunctions.addDeviceNames: Unable to open session.")
                    return

                params = {"_session_id_": session}
                response = self.jsonRpcPost("Interface.listInterfaces", params)
                interface = False
                if response['error'] is None and response['result']:
                    for i in response['result']:
                        if i['port'] == self._remote_port:
                            interface = i['name']
                            break
                LOG.debug("RPCFunctions.addDeviceNames: Got interface: %s" % interface)
                if not interface:
                    params = {"_session_id_": session}
                    response = self.jsonRpcPost("Session.logout", params)
                    return

                params = {"_session_id_": session}
                response = self.jsonRpcPost("Device.listAllDetail", params)

                if response['error'] is None and response['result']:
                    LOG.debug("RPCFunctions.addDeviceNames: Resolving devicenames")
                    for i in response['result']:
                        try:
                            if i.get('address') in self.devices:
                                self.devices[i['address']].NAME = i['name']
                        except Exception as err:
                            LOG.warning("RPCFunctions.addDeviceNames: Exception: %s" % str(err))

                params = {"_session_id_": session}
                response = self.jsonRpcPost("Session.logout", params)
            except Exception as err:
                params = {"_session_id_": session}
                response = self.jsonRpcPost("Session.logout", params)
                LOG.warning("RPCFunctions.addDeviceNames: Exception: %s" % str(err))

        #Then try to get names from XML-API
        elif self.resolvenames == 'xml':
            try:
                response = urllib.request.urlopen("http://%s%s" % (self._remote_ip, XML_API_URL), timeout=5)
                device_list = response.read().decode("ISO-8859-1")
            except Exception as err:
                LOG.warning("RPCFunctions.addDeviceNames: Could not access XML-API: %s" % (str(err), ))
                return
            device_list_tree = ET.ElementTree(ET.fromstring(device_list))
            for device in device_list_tree.getroot():
                address = device.attrib['address']
                name = device.attrib['name']
                if address in self.devices:
                    self.devices[address].NAME = name
                    for address, device in self.devices[address].CHANNELS.items():
                        device.NAME = name
                        self.devices_all[device.ADDRESS].NAME = name

class LockingServerProxy(xmlrpc.client.ServerProxy):
    """
    ServerProxy implementeation with lock when request is executing
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize new proxy for server
        """

        self.lock = threading.Lock()
        xmlrpc.client.ServerProxy.__init__(self, *args, **kwargs)

    def __request(self, *args, **kwargs):
        """
        Call method on server side
        """

        with self.lock:
            parent = xmlrpc.client.ServerProxy
            return parent._ServerProxy__request(self, *args, **kwargs)

    def __getattr__(self, *args, **kwargs):
        """
        Magic method dispatcher
        """

        return xmlrpc.client._Method(self.__request, *args, **kwargs)

# Restrict to particular paths.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/', '/RPC2',)

class ServerThread(threading.Thread):
    """XML-RPC server thread to handle messages from CCU / Homegear"""
    def __init__(self,
                 local=LOCAL,
                 localport=LOCALPORT,
                 remote=REMOTE,
                 remoteport=REMOTEPORT,
                 devicefile=DEVICEFILE,
                 interface_id=INTERFACE_ID,
                 eventcallback=False,
                 systemcallback=False,
                 resolvenames=False,
                 rpcusername=RPC_USERNAME,
                 rpcpassword=RPC_PASSWORD,
                 resolveparamsets=False):
        LOG.debug("ServerThread.__init__")
        threading.Thread.__init__(self)

        # Member
        self._interface_id = interface_id
        self._local = local
        self._localport = localport
        self._remote = remote
        self._remoteport = remoteport
        self._devicefile = devicefile
        self.eventcallback = eventcallback
        self.systemcallback = systemcallback
        self.resolvenames = resolvenames
        self.rpcusername = rpcusername
        self.rpcpassword = rpcpassword
        self.resolveparamsets = resolveparamsets

        # Create proxy to interact with CCU / Homegear
        LOG.info("Creating proxy. Connecting to http://%s:%i" % (self._remote, int(self._remoteport)))
        try:
            self.proxy = LockingServerProxy("http://%s:%i" % (self._remote, int(self._remoteport)))
        except Exception as err:
            LOG.warning("Failed connecting to proxy at http://%s:%i" % (self._remote, int(self._remoteport)))
            LOG.debug("__init__: Exception: %s" % str(err))
            raise Exception

        self._rpcfunctions = RPCFunctions(devicefile=self._devicefile,
                                          proxy=self.proxy,
                                          remote_ip=self._remote,
                                          remote_port=self._remoteport,
                                          eventcallback=self.eventcallback,
                                          systemcallback=self.systemcallback,
                                          resolvenames=self.resolvenames,
                                          rpcusername=self.rpcusername,
                                          rpcpassword=self.rpcpassword,
                                          resolveparamsets=self.resolveparamsets)

        # Setup server to handle requests from CCU / Homegear
        LOG.debug("ServerThread.__init__: Setting up server")
        self.server = SimpleXMLRPCServer((self._local, int(self._localport)),
                                         requestHandler=RequestHandler,
                                         logRequests=False)
        self.server.register_introspection_functions()
        self.server.register_multicall_functions()
        LOG.debug("ServerThread.__init__: Registering RPC functions")
        self.server.register_instance(self._rpcfunctions, allow_dotted_names=True)

    def run(self):
        LOG.info("Starting server at http://%s:%i" % (self._local, int(self._localport)))
        self.server.serve_forever()

    def proxyInit(self):
        """
        To receive events the proxy has to tell the CCU / Homegear where to send the events. For that we call the init-method.
        """
        # Call init() with local XML RPC config and interface_id (the name of the receiver) to receive events. XML RPC server has to be running.
        LOG.debug("ServerThread.proxyInit: init(http://%s:%i, '%s')" % (self._local, int(self._localport), self._interface_id))
        try:
            self.proxy.init("http://%s:%i" % (self._local, int(self._localport)), self._interface_id)
            LOG.info("Proxy initialized")
        except Exception as err:
            LOG.debug("proxyInit: Exception: %s" % str(err))
            LOG.warning("Failed to initialize proxy")
            raise Exception

    def stop(self):
        """To stop the server we de-init from the CCU / Homegear, then shut down our XML-RPC server."""
        if self.proxy:
            LOG.debug("ServerThread.stop: Deregistering proxy")
            try:
                self.proxy.init("http://%s:%i" % (self._local, int(self._localport)))
            except Exception as err:
                LOG.warning("Failed to deregister proxy")
                LOG.debug("stop: Exception: %s" % str(err))
        LOG.info("Shutting down server")
        self.server.shutdown()
        LOG.debug("ServerThread.stop: Stopping ServerThread")
        self.server.server_close()
        LOG.info("Server stopped")
