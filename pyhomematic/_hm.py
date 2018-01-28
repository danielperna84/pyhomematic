import os
import threading
import json
import urllib.request
import xml.etree.ElementTree as ET
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import socket
import logging
from pyhomematic import devicetypes
from pyhomematic.devicetypes.generic import HMChannel

LOG = logging.getLogger(__name__)

# Constants
LOCAL = '0.0.0.0'
LOCALPORT = 0
REMOTES = {
    'default': {
        'ip': '127.0.0.1',
        'port': 2001,
        'path': '',
        'username': 'Admin',
        'password': '',
        'resolvenames': False,
        'connect': True,
    }}
DEVICEFILE = False  # e.g. devices.json
INTERFACE_ID = 'pyhomematic'
XML_API_URL = '/config/xmlapi/devicelist.cgi'
JSONRPC_URL = '/api/homematic.cgi'
BACKEND_UNKNOWN = 0
BACKEND_CCU = 1
BACKEND_HOMEGEAR = 2


# Device-storage
devices = {}
devices_all = {}
devices_raw = {}
devices_raw_dict = {}
working = False


# Object holding the methods the XML-RPC server should provide.
class RPCFunctions(object):

    def __init__(self,
                 devicefile=DEVICEFILE,
                 proxies={},
                 remotes={},
                 eventcallback=False,
                 systemcallback=False,
                 resolveparamsets=False):
        global devices, devices_all, devices_raw, devices_raw_dict
        LOG.debug("RPCFunctions.__init__")
        self.devicefile = devicefile
        self.eventcallback = eventcallback
        self.systemcallback = systemcallback
        self.resolveparamsets = resolveparamsets
        self.remotes = remotes

        # The methods need to know about the proxyies to be able to pass it on
        # to the device-objects
        self._proxies = proxies

        # Devices w/o channels will be accessible using the device-address as
        # the key
        self.devices = devices
        # Devices including channels will be accessible using the
        # device-address + channel as the key
        self.devices_all = devices_all

        # The plain JSON (actually dicts) are stored as well
        self._devices_raw_dict = devices_raw_dict
        self._devices_raw = devices_raw

        for interface_id in proxies:
            LOG.debug("RPCFunctions.__init__: iterating proxy = %s" %
                      (interface_id, ))
            remote = interface_id.split('-')[-1]
            self.devices[remote] = {}
            self.devices_all[remote] = {}
            self._devices_raw[remote] = []
            self._devices_raw_dict[remote] = {}

            # If there are stored devices, we load them instead of getting them
            # from the server.
            if self.devicefile:
                LOG.debug("RPCFunctions.__init__: devicefile = %s" %
                          (self.devicefile, ))
                if os.path.isfile(self.devicefile):
                    with open(self.devicefile, 'r') as fptr:
                        fcontent = fptr.read()
                        if fcontent:
                            self._devices_raw[remote] = json.loads(fcontent)

            for device in self._devices_raw[remote]:
                self._devices_raw_dict[remote][device['ADDRESS']] = device
            LOG.debug("RPCFunctions.__init__: devices_raw = %s" %
                      (str(self._devices_raw[remote]), ))

            # Create the "interactive" device-objects and store them in
            # self._devices and self._devices_all
            self.createDeviceObjects(interface_id)

    def createDeviceObjects(self, interface_id):
        """Transform the raw device descriptions into instances of devicetypes.generic.HMDevice or availabe subclass."""
        global working
        working = True
        remote = interface_id.split('-')[-1]
        LOG.debug(
            "RPCFunctions.createDeviceObjects: iterating interface_id = %s" % (remote, ))
        # First create parent object
        for dev in self._devices_raw[remote]:
            if not dev['PARENT']:
                if dev['ADDRESS'] not in self.devices_all[remote]:
                    try:
                        if dev['TYPE'] in devicetypes.SUPPORTED:
                            deviceObject = devicetypes.SUPPORTED[dev['TYPE']](
                                dev, self._proxies[interface_id], self.resolveparamsets)
                            LOG.debug("RPCFunctions.createDeviceObjects: created %s  as SUPPORTED device for %s" % (
                                dev['ADDRESS'], dev['TYPE']))
                        else:
                            deviceObject = devicetypes.UNSUPPORTED(
                                dev, self._proxies[interface_id], self.resolveparamsets)
                            LOG.debug("RPCFunctions.createDeviceObjects: created %s  as UNSUPPORTED device for %s" % (
                                dev['ADDRESS'], dev['TYPE']))
                        LOG.debug(
                            "RPCFunctions.createDeviceObjects: adding to self.devices_all")
                        self.devices_all[remote][dev['ADDRESS']] = deviceObject
                        LOG.debug(
                            "RPCFunctions.createDeviceObjects: adding to self.devices")
                        self.devices[remote][dev['ADDRESS']] = deviceObject
                    except Exception as err:
                        LOG.critical(
                            "RPCFunctions.createDeviceObjects: Parent: %s", str(err))
        # Then create all children for parent
        for dev in self._devices_raw[remote]:
            if dev['PARENT']:
                try:
                    if dev['ADDRESS'] not in self.devices_all[remote]:
                        deviceObject = HMChannel(
                            dev, self._proxies[interface_id], self.resolveparamsets)
                        self.devices_all[remote][dev['ADDRESS']] = deviceObject
                        self.devices[remote][dev['PARENT']].CHANNELS[
                            dev['INDEX']] = deviceObject
                except Exception as err:
                    LOG.critical(
                        "RPCFunctions.createDeviceObjects: Child: %s", str(err))
        if self.devices_all[remote] and self.remotes[remote].get('resolvenames', False):
            self.addDeviceNames(remote)
        working = False
        if self.systemcallback:
            self.systemcallback('createDeviceObjects')
        return True

    def error(self, interface_id, errorcode, msg):
        """When some error occurs the CCU / Homegear will send it's error message here"""
        LOG.debug("RPCFunctions.error: interface_id = %s, errorcode = %i, message = %s" % (
            interface_id, int(errorcode), str(msg)))
        if self.systemcallback:
            self.systemcallback('error', interface_id, errorcode, msg)
        return True

    def saveDevices(self, remote):
        """We save known devices into a json-file so we don't have to work through the whole list of devices the CCU / Homegear presents us"""
        LOG.debug("RPCFunctions.saveDevices: devicefile: %s, _devices_raw: %s" % (
            self.devicefile, str(self._devices_raw[remote])))
        if self.devicefile:
            try:
                with open(self.devicefile, 'w') as df:
                    df.write(json.dumps(self._devices_raw[remote]))
                return True
            except Exception as err:
                LOG.warning(
                    "RPCFunctions.saveDevices: Exception saving _devices_raw: %s", str(err))
                return False
        else:
            return True

    def event(self, interface_id, address, value_key, value):
        """If a device emits some sort event, we will handle it here."""
        LOG.debug("RPCFunctions.event: interface_id = %s, address = %s, value_key = %s, value = %s" % (
            interface_id, address, value_key.upper(), str(value)))
        self.devices_all[interface_id.split(
            '-')[-1]][address].event(interface_id, value_key.upper(), value)
        if self.eventcallback:
            self.eventcallback(interface_id=interface_id, address=address,
                               value_key=value_key.upper(), value=value)
        return True

    def listDevices(self, interface_id):
        """The CCU / Homegear asks for devices known to our XML-RPC server. We respond to that request using this method."""
        LOG.debug("RPCFunctions.listDevices: interface_id = %s, _devices_raw = %s" % (
            interface_id, str(self._devices_raw)))
        remote = interface_id.split('-')[-1]
        if remote not in self._devices_raw:
            self._devices_raw[remote] = []
        if self.systemcallback:
            self.systemcallback('listDevices', interface_id)
        return self._devices_raw[remote]

    def newDevices(self, interface_id, dev_descriptions):
        """The CCU / Homegear informs us about newly added devices. We react on that and add those devices as well."""
        LOG.debug("RPCFunctions.newDevices: interface_id = %s, dev_descriptions = %s" % (
            interface_id, str(dev_descriptions)))
        remote = interface_id.split('-')[-1]
        if remote not in self._devices_raw:
            self._devices_raw[remote] = []
        if remote not in self._devices_raw_dict:
            self._devices_raw_dict[remote] = {}
        for d in dev_descriptions:
            self._devices_raw[remote].append(d)
            self._devices_raw_dict[remote][d['ADDRESS']] = d
        self.saveDevices(remote)
        self.createDeviceObjects(interface_id)
        if self.systemcallback:
            self.systemcallback('newDevices', interface_id, dev_descriptions)
        return True

    def deleteDevices(self, interface_id, addresses):
        """The CCU / Homegear informs us about removed devices. We react on that and remove those devices as well."""
        LOG.debug("RPCFunctions.deleteDevices: interface_id = %s, addresses = %s" % (
            interface_id, str(addresses)))
        # TODO: remove known device objects as well
        remote = interface_id.split('-')[-1]
        self._devices_raw[remote] = [device for device in self._devices_raw[
            remote] if not device['ADDRESS'] in addresses]
        self.saveDevices(remote)
        if self.systemcallback:
            self.systemcallback('deleteDevice', interface_id, addresses)
        return True

    def updateDevice(self, interface_id, address, hint):
        LOG.debug("RPCFunctions.updateDevice: interface_id = %s, address = %s, hint = %s" % (
            interface_id, address, str(hint)))
        # TODO: Implement updateDevice
        if self.systemcallback:
            self.systemcallback('updateDevice', interface_id, address, hint)
        return True

    def replaceDevice(self, interface_id, oldDeviceAddress, newDeviceAddress):
        LOG.debug("RPCFunctions.replaceDevice: interface_id = %s, oldDeviceAddress = %s, newDeviceAddress = %s" % (
            interface_id, oldDeviceAddress, newDeviceAddress))
        # TODO: Implement replaceDevice
        if self.systemcallback:
            self.systemcallback('replaceDevice', interface_id,
                                oldDeviceAddress, newDeviceAddress)
        return True

    def readdedDevice(self, interface_id, addresses):
        LOG.debug("RPCFunctions.readdedDevices: interface_id = %s, addresses = %s" % (
            interface_id, str(addresses)))
        # TODO: Implement readdedDevice
        if self.systemcallback:
            self.systemcallback('readdedDevice', interface_id, addresses)
        return True

    def jsonRpcPost(self, host, method, params={}):
        LOG.debug("RPCFunctions.jsonRpcPost: Method: %s" % method)
        try:
            payload = json.dumps(
                {"method": method, "params": params, "jsonrpc": "1.1", "id": 0}).encode('utf-8')

            headers = {"Content-Type": 'application/json',
                       "Content-Length": len(payload)}
            apiendpoint = "http://%s%s" % (host, JSONRPC_URL)
            LOG.debug("RPCFunctions.jsonRpcPost: API-Endpoint: %s" %
                      apiendpoint)
            req = urllib.request.Request(apiendpoint, payload, headers)
            resp = urllib.request.urlopen(req)
            if resp.status == 200:
                try:
                    return json.loads(resp.read().decode('utf-8'))
                except ValueError as err:
                    # Workaround for bug in CCU
                    return json.loads(resp.read().decode('utf-8').replace("\\", ""))
            else:
                LOG.error("RPCFunctions.jsonRpcPost: Status: %i" % resp.status)
                return {'error': resp.status, 'result': {}}
        except Exception as err:
            LOG.error("RPCFunctions.jsonRpcPost: Exception: %s" % str(err))
            return {'error': str(err), 'result': {}}

    def addDeviceNames(self, remote):
        """ If XML-API (http://www.homematic-inside.de/software/addons/item/xmlapi) is installed on CCU this function will add names to CCU devices """
        LOG.debug("RPCFunctions.addDeviceNames")

        # First try to get names from metadata when nur credentials are set
        if self.remotes[remote]['resolvenames'] == 'metadata':
            for address in self.devices[remote]:
                try:
                    name = self.devices[remote][
                        address]._proxy.getMetadata(address, 'NAME')
                    self.devices[remote][address].NAME = name
                    for address, device in self.devices[remote][address].CHANNELS.items():
                        device.NAME = name
                        self.devices_all[remote][device.ADDRESS].NAME = name
                except Exception as err:
                    LOG.debug(
                        "RPCFunctions.addDeviceNames: Unable to get name for %s from metadata." % str(address))

        # Then try to get names via JSON-RPC
        elif (self.remotes[remote]['resolvenames'] == 'json' and
              self.remotes[remote]['username'] and
              self.remotes[remote]['password']):
            LOG.debug("RPCFunctions.addDeviceNames: Getting names via JSON-RPC")
            try:
                session = False
                params = {"username": self.remotes[remote][
                    'username'], "password": self.remotes[remote]['password']}
                response = self.jsonRpcPost(
                    self.remotes[remote]['ip'], "Session.login", params)
                if response['error'] is None and response['result']:
                    session = response['result']

                if not session:
                    LOG.warning(
                        "RPCFunctions.addDeviceNames: Unable to open session.")
                    return

                params = {"_session_id_": session}
                response = self.jsonRpcPost(
                    self.remotes[remote]['ip'], "Interface.listInterfaces", params)
                interface = False
                if response['error'] is None and response['result']:
                    for i in response['result']:
                        if i['port'] == self.remotes[remote]['port']:
                            interface = i['name']
                            break
                LOG.debug(
                    "RPCFunctions.addDeviceNames: Got interface: %s" % interface)
                if not interface:
                    params = {"_session_id_": session}
                    response = self.jsonRpcPost(
                        self.remotes[remote]['ip'], "Session.logout", params)
                    return

                params = {"_session_id_": session}
                response = self.jsonRpcPost(
                    self.remotes[remote]['ip'], "Device.listAllDetail", params)

                if response['error'] is None and response['result']:
                    LOG.debug(
                        "RPCFunctions.addDeviceNames: Resolving devicenames")
                    for i in response['result']:
                        try:
                            if i.get('address') in self.devices[remote]:
                                self.devices[remote][
                                    i['address']].NAME = i['name']
                        except Exception as err:
                            LOG.warning(
                                "RPCFunctions.addDeviceNames: Exception: %s" % str(err))

                params = {"_session_id_": session}
                response = self.jsonRpcPost(
                    self.remotes[remote]['ip'], "Session.logout", params)
            except Exception as err:
                params = {"_session_id_": session}
                response = self.jsonRpcPost(
                    self.remotes[remote]['ip'], "Session.logout", params)
                LOG.warning(
                    "RPCFunctions.addDeviceNames: Exception: %s" % str(err))

        # Then try to get names from XML-API
        elif self.remotes[remote]['resolvenames'] == 'xml':
            try:
                response = urllib.request.urlopen(
                    "http://%s%s" % (self.remotes[remote]['ip'], XML_API_URL), timeout=5)
                device_list = response.read().decode("ISO-8859-1")
            except Exception as err:
                LOG.warning(
                    "RPCFunctions.addDeviceNames: Could not access XML-API: %s" % (str(err), ))
                return
            device_list_tree = ET.ElementTree(ET.fromstring(device_list))
            for device in device_list_tree.getroot():
                address = device.attrib['address']
                name = device.attrib['name']
                if address in self.devices[remote]:
                    self.devices[remote][address].NAME = name
                    for address, device in self.devices[remote][address].CHANNELS.items():
                        device.NAME = name
                        self.devices_all[remote][device.ADDRESS].NAME = name


class LockingServerProxy(xmlrpc.client.ServerProxy):
    """
    ServerProxy implementation with lock when request is executing
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize new proxy for server and get local ip
        """
        self._skipinit = kwargs.pop("skipinit", False)
        self._callbackip = kwargs.pop("callbackip", None)
        self._callbackport = kwargs.pop("callbackport", None)
        self.lock = threading.Lock()
        xmlrpc.client.ServerProxy.__init__(self, *args, **kwargs)
        self._remoteip, self._remoteport = self._ServerProxy__host.split(':')
        self._remoteport = int(self._remoteport)
        LOG.debug("LockingServerProxy.__init__: Getting local ip")
        tmpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        tmpsocket.connect((self._remoteip, self._remoteport))
        self._localip = tmpsocket.getsockname()[0]
        tmpsocket.close()
        LOG.debug("LockingServerProxy.__init__: Got local ip %s" %
                  self._localip)

    def __request(self, *args, **kwargs):
        """
        Call method on server side
        """

        with self.lock:
            parent = xmlrpc.client.ServerProxy
            # pylint: disable=E1101
            return parent._ServerProxy__request(self, *args, **kwargs)

    def __getattr__(self, *args, **kwargs):
        """
        Magic method dispatcher
        """

        return xmlrpc.client._Method(self.__request, *args, **kwargs)

# Restrict to particular paths.


class RequestHandler(SimpleXMLRPCRequestHandler):
    """We handle requests to / and /RPC2"""
    rpc_paths = ('/', '/RPC2',)


class ServerThread(threading.Thread):
    """XML-RPC server thread to handle messages from CCU / Homegear"""

    def __init__(self,
                 local=LOCAL,
                 localport=LOCALPORT,
                 remotes=REMOTES,
                 devicefile=DEVICEFILE,
                 interface_id=INTERFACE_ID,
                 eventcallback=False,
                 systemcallback=False,
                 resolveparamsets=False):
        LOG.debug("ServerThread.__init__")
        threading.Thread.__init__(self)

        # Member
        self._interface_id = interface_id
        self._local = local
        self._localport = int(localport)
        self._devicefile = devicefile
        self.remotes = remotes
        self.eventcallback = eventcallback
        self.systemcallback = systemcallback
        self.resolveparamsets = resolveparamsets
        self.proxies = {}

        # Create proxies to interact with CCU / Homegear
        LOG.debug("__init__: Creating proxies")
        for remote, host in self.remotes.items():
            # Initialize XML-RPC
            try:
                socket.inet_pton(socket.AF_INET, host['ip'])
            except Exception as err:
                LOG.warning("Skipping proxy: %s" % str(err))
                continue
            if 'path' not in host:
                host['path'] = ""
            LOG.info("Creating proxy %s. Connecting to http://%s:%i%s" %
                     (remote, host['ip'], host['port'], host['path']))
            host['id'] = "%s-%s" % (self._interface_id, remote)
            try:
                self.proxies[host['id']] = LockingServerProxy("http://%s:%i%s" % (host['ip'], host['port'], host['path']),
                                                              callbackip=host.get('callbackip', None),
                                                              callbackport=host.get('callbackport', None),
                                                              skipinit=not host.get('connect', True))
            except Exception as err:
                LOG.warning("Failed connecting to proxy at http://%s:%i%s" %
                            (host['ip'], host['port'], host['path']))
                LOG.debug("__init__: Exception: %s" % str(err))
                raise Exception
            try:
                host['type'] = BACKEND_UNKNOWN
                #if "Homegear" in self.proxies[host['id']].getVersion():
                #    LOG.debug("__init__: Host is Homegear")
                #    host['type'] = BACKEND_HOMEGEAR
                #else:
                #    LOG.debug("__init__: Host is CCU")
                #    host['type'] = BACKEND_CCU
            except Exception as err:
                LOG.warning("__init__: Failed to detect backend type: %s" % str(err))
                host['type'] = BACKEND_UNKNOWN

        if not self.proxies:
            LOG.warning("No proxies available. Aborting.")
            raise Exception

        self._rpcfunctions = RPCFunctions(devicefile=self._devicefile,
                                          proxies=self.proxies,
                                          remotes=self.remotes,
                                          eventcallback=self.eventcallback,
                                          systemcallback=self.systemcallback,
                                          resolveparamsets=self.resolveparamsets)

        # Setup server to handle requests from CCU / Homegear
        LOG.debug("ServerThread.__init__: Setting up server")
        self.server = SimpleXMLRPCServer((self._local, self._localport),
                                         requestHandler=RequestHandler,
                                         logRequests=False)
        self._localport = self.server.socket.getsockname()[1]
        self.server.register_introspection_functions()
        self.server.register_multicall_functions()
        LOG.debug("ServerThread.__init__: Registering RPC functions")
        self.server.register_instance(
            self._rpcfunctions, allow_dotted_names=True)

    def run(self):
        LOG.info("Starting server at http://%s:%i" %
                 (self._local, self._localport))
        self.server.serve_forever()

    def proxyInit(self):
        """
        To receive events the proxy has to tell the CCU / Homegear where to send the events. For that we call the init-method.
        """
        # Call init() with local XML RPC config and interface_id (the name of
        # the receiver) to receive events. XML RPC server has to be running.
        for interface_id, proxy in self.proxies.items():
            if proxy._skipinit:
                continue
            if proxy._callbackip and proxy._callbackport:
                callbackip = proxy._callbackip
                callbackport = proxy._callbackport
            else:
                callbackip = proxy._localip
                callbackport = self._localport
            LOG.debug("ServerThread.proxyInit: init('http://%s:%i', '%s')" %
                      (callbackip, callbackport, interface_id))
            try:
                proxy.init("http://%s:%i" %
                           (callbackip, callbackport), interface_id)
                LOG.info("Proxy initialized")
            except Exception as err:
                LOG.debug("proxyInit: Exception: %s" % str(err))
                LOG.warning("Failed to initialize proxy")
                raise Exception

    def stop(self):
        """To stop the server we de-init from the CCU / Homegear, then shut down our XML-RPC server."""
        stopped = []
        for _, proxy in self.proxies.items():
            if proxy._callbackip and proxy._callbackport:
                callbackip = proxy._callbackip
                callbackport = proxy._callbackport
            else:
                callbackip = proxy._localip
                callbackport = self._localport
            remote = "http://%s:%i" % (callbackip, callbackport)
            LOG.debug("ServerThread.stop: init('%s')" % remote)
            if not callbackip in stopped:
                try:
                    proxy.init(remote)
                    stopped.append(callbackip)
                    LOG.info("Proxy de-initialized: %s" % remote)
                except Exception as err:
                    LOG.debug("proxyInit: Exception: %s" % str(err))
                    LOG.warning("Failed to de-initialize proxy")
                    raise Exception
        self.proxies.clear()
        LOG.info("Shutting down server")
        self.server.shutdown()
        LOG.debug("ServerThread.stop: Stopping ServerThread")
        self.server.server_close()
        LOG.info("Server stopped")

    def parseCCUSysVar(self, data):
        """Helper to parse type of system variables of CCU"""
        if data['type'] == 'LOGIC':
            return data['name'], data['value'] == 'true'
        elif data['type'] == 'NUMBER':
            return data['name'], float(data['value'])
        elif data['type'] == 'LIST':
            return data['name'], int(data['value'])
        else:
            return data['name'], data['value']

    def jsonRpcLogin(self, remote):
        """Login to CCU and return session"""
        session = False
        try:
            params = {"username": self.remotes[remote][
                'username'], "password": self.remotes[remote]['password']}
            response = self._rpcfunctions.jsonRpcPost(
                self.remotes[remote]['ip'], "Session.login", params)
            if response['error'] is None and response['result']:
                session = response['result']

            if not session:
                LOG.warning(
                    "ServerThread.jsonRpcLogin: Unable to open session.")
        except Exception as err:
            LOG.debug(
                "ServerThread.jsonRpcLogin: Exception while logging in via JSON-RPC: %s" % str(err))
        return session

    def jsonRpcLogout(self, remote, session):
        """Logout of CCU"""
        logout = False
        try:
            params = {"_session_id_": session}
            response = self._rpcfunctions.jsonRpcPost(
                self.remotes[remote]['ip'], "Session.logout", params)
            if response['error'] is None and response['result']:
                logout = response['result']
        except Exception as err:
            LOG.debug(
                "ServerThread.jsonRpcLogout: Exception while logging in via JSON-RPC: %s" % str(err))
        return logout

    def getAllSystemVariables(self, remote):
        """Get all system variables from CCU / Homegear"""
        variables = {}
        if self.remotes[remote]['username'] and self.remotes[remote]['password']:
            LOG.debug(
                "ServerThread.getAllSystemVariables: Getting all System variables via JSON-RPC")
            session = self.jsonRpcLogin(remote)
            if not session:
                return
            try:
                params = {"_session_id_": session}
                response = self._rpcfunctions.jsonRpcPost(
                    self.remotes[remote]['ip'], "SysVar.getAll", params)
                if response['error'] is None and response['result']:
                    for var in response['result']:
                        key, value = self.parseCCUSysVar(var)
                        variables[key] = value

                self.jsonRpcLogout(remote, session)
            except Exception as err:
                self.jsonRpcLogout(remote, session)
                LOG.warning(
                    "ServerThread.getAllSystemVariables: Exception: %s" % str(err))
        else:
            try:
                variables = self.proxies[
                    "%s-%s" % (self._interface_id, remote)].getAllSystemVariables()
            except Exception as err:
                LOG.debug(
                    "ServerThread.getAllSystemVariables: Exception: %s" % str(err))
        return variables

    def getSystemVariable(self, remote, name):
        """Get single system variable from CCU / Homegear"""
        var = None
        if self.remotes[remote]['username'] and self.remotes[remote]['password']:
            LOG.debug(
                "ServerThread.getSystemVariable: Getting System variable via JSON-RPC")
            session = self.jsonRpcLogin(remote)
            if not session:
                return
            try:
                params = {"_session_id_": session, "name": name}
                response = self._rpcfunctions.jsonRpcPost(
                    self.remotes[remote]['ip'], "SysVar.getValueByName", params)
                if response['error'] is None and response['result']:
                    try:
                        var = float(response['result'])
                    except Exception as err:
                        var = response['result'] == 'true'

                self.jsonRpcLogout(remote, session)
            except Exception as err:
                self.jsonRpcLogout(remote, session)
                LOG.warning(
                    "ServerThread.getSystemVariable: Exception: %s" % str(err))
        else:
            try:
                var = self.proxies[
                    "%s-%s" % (self._interface_id, remote)].getSystemVariable(name)
            except Exception as err:
                LOG.debug(
                    "ServerThread.getSystemVariable: Exception: %s" % str(err))
        return var

    def deleteSystemVariable(self, remote, name):
        """Delete a system variable from CCU / Homegear"""
        if self.remotes[remote]['username'] and self.remotes[remote]['password']:
            LOG.debug(
                "ServerThread.deleteSystemVariable: Getting System variable via JSON-RPC")
            session = self.jsonRpcLogin(remote)
            if not session:
                return
            try:
                params = {"_session_id_": session, "name": name}
                response = self._rpcfunctions.jsonRpcPost(
                    self.remotes[remote]['ip'], "SysVar.deleteSysVarByName", params)
                if response['error'] is None and response['result']:
                    deleted = response['result']
                    LOG.warning(
                        "ServerThread.deleteSystemVariable: Deleted: %s" % str(deleted))

                self.jsonRpcLogout(remote, session)
            except Exception as err:
                self.jsonRpcLogout(remote, session)
                LOG.warning(
                    "ServerThread.deleteSystemVariable: Exception: %s" % str(err))
        else:
            try:
                return self.proxies["%s-%s" % (self._interface_id, remote)].deleteSystemVariable(name)
            except Exception as err:
                LOG.debug(
                    "ServerThread.deleteSystemVariable: Exception: %s" % str(err))

    def setSystemVariable(self, remote, name, value):
        """Set a system variable on CCU / Homegear"""
        if self.remotes[remote]['username'] and self.remotes[remote]['password']:
            LOG.debug(
                "ServerThread.setSystemVariable: Setting System variable via JSON-RPC")
            session = self.jsonRpcLogin(remote)
            if not session:
                return
            try:
                params = {"_session_id_": session,
                          "name": name, "value": value}
                if value is True or value is False:
                    params['value'] = int(value)
                    response = self._rpcfunctions.jsonRpcPost(
                        self.remotes[remote]['ip'], "SysVar.setBool", params)
                else:
                    response = self._rpcfunctions.jsonRpcPost(
                        self.remotes[remote]['ip'], "SysVar.setFloat", params)
                if response['error'] is None and response['result']:
                    res = response['result']
                    LOG.debug(
                        "ServerThread.setSystemVariable: Result while setting variable: %s" % str(res))
                else:
                    if response['error']:
                        LOG.debug("ServerThread.setSystemVariable: Error while setting variable: %s" % str(
                            response['error']))

                self.jsonRpcLogout(remote, session)
            except Exception as err:
                self.jsonRpcLogout(remote, session)
                LOG.warning(
                    "ServerThread.setSystemVariable: Exception: %s" % str(err))
        else:
            try:
                return self.proxies["%s-%s" % (self._interface_id, remote)].setSystemVariable(name, value)
            except Exception as err:
                LOG.debug(
                    "ServerThread.setSystemVariable: Exception: %s" % str(err))

    def getServiceMessages(self, remote):
        """Get service messages from CCU / Homegear"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].getServiceMessages()
        except Exception as err:
            LOG.debug("ServerThread.getServiceMessages: Exception: %s" % str(err))

    def rssiInfo(self, remote):
        """Get RSSI information for all devices from CCU / Homegear"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].rssiInfo()
        except Exception as err:
            LOG.debug("ServerThread.rssiInfo: Exception: %s" % str(err))

    def setInstallMode(self, remote, on=True, t=60, mode=1, address=None):
        """Activate or deactivate installmode on CCU / Homegear"""
        try:
            args = [on]
            if on and t:
                args.append(t)
                if address:
                    args.append(address)
                else:
                    args.append(mode)

            return self.proxies["%s-%s" % (self._interface_id, remote)].setInstallMode(*args)
        except Exception as err:
            LOG.debug("ServerThread.setInstallMode: Exception: %s" % str(err))

    def getInstallMode(self, remote):
        """Get remaining time in seconds install mode is active from CCU / Homegear"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].getInstallMode()
        except Exception as err:
            LOG.debug("ServerThread.getInstallMode: Exception: %s" % str(err))

    def getAllMetadata(self, remote, address):
        """Get all metadata of device"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].getAllMetadata(address)
        except Exception as err:
            LOG.debug("ServerThread.getAllMetadata: Exception: %s" % str(err))

    def getMetadata(self, remote, address, key):
        """Get metadata of device"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].getMetadata(address, key)
        except Exception as err:
            LOG.debug("ServerThread.getMetadata: Exception: %s" % str(err))

    def setMetadata(self, remote, address, key, value):
        """Set metadata of device"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].setMetadata(address, key, value)
        except Exception as err:
            LOG.debug("ServerThread.setMetadata: Exception: %s" % str(err))

    def deleteMetadata(self, remote, address, key):
        """Delete metadata of device"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].deleteMetadata(address, key)
        except Exception as err:
            LOG.debug("ServerThread.deleteMetadata: Exception: %s" % str(err))

    def listBidcosInterfaces(self, remote):
        """Return all available BidCos Interfaces"""
        try:
            return self.proxies["%s-%s" % (self._interface_id, remote)].listBidcosInterfaces()
        except Exception as err:
            LOG.debug(
                "ServerThread.listBidcosInterfaces: Exception: %s" % str(err))

    def homegearCheckInit(self, remote):
        """Check if proxy is still initialized"""
        rdict = self.remotes.get(remote)
        if not rdict:
            return False
        if rdict.get('type') != BACKEND_HOMEGEAR:
            return False
        try:
            interface_id = "%s-%s" % (self._interface_id, remote)
            return self.proxies[interface_id].clientServerInitialized(interface_id)
        except Exception as err:
            LOG.debug(
                "ServerThread.homegearCheckInit: Exception: %s" % str(err))
            return False
