from . import _devices
import os
import threading
import json
from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import xmlrpc.client
import logging
LOG = logging.getLogger(__name__)

LOCAL = '127.0.0.1'
LOCALPORT = 7080
REMOTE = '127.0.0.1'
REMOTEPORT = 2001
DEVICEFILE = False # e.g. devices.json
INTERFACE_ID = 'pyhomematic'

# Object holding the methods the XML-RPC server should provide.
class RPCFunctions:
    def __init__(self, devicefile = DEVICEFILE, proxy = False, eventcallback = False):
        LOG.debug("RPCFunctions.__init__")
        self.devicefile = devicefile
        self.eventcallback = eventcallback
        
        # The methods need to know about the proxy to be able to pass it on to the device-objects
        self._proxy = proxy
        
        # Devices w/o channels will be accessible using the device-address as the key
        self.devices = {}
        # Devices including channels will be accessible using the device-address as the key
        self.devices_all = {}
        
        # The plain JSON (actually dicts) are stored as well
        self._devices_raw_dict = {}
        self._devices_raw = []
        
        
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
        """Transform the raw device descriptions into instances of hmdevices.HMDevice or availabe subclass"""
        for dev in self._devices_raw:
            if not dev['PARENT']:
                if not dev['ADDRESS'] in self.devices_all:
                    if dev['TYPE'] in _devices.DEVICETYPES:
                        deviceObject = _devices.DEVICETYPES[dev['TYPE']](dev, self._proxy)
                    else:
                        deviceObject = hmdevices.HMDevice(dev, self._proxy)
                    self.devices_all[dev['ADDRESS']] = deviceObject
                    self.devices[dev['ADDRESS']] = deviceObject
        for dev in self._devices_raw:
            if dev['PARENT']:
                if not dev['ADDRESS'] in self.devices_all:
                    if self.devices_all[dev['PARENT']]._TYPE in _devices.DEVICETYPES:
                        deviceObject = _devices.DEVICETYPES[self.devices_all[dev['PARENT']]._TYPE](dev, self._proxy)
                    else:
                        deviceObject = hmdevices.HMDevice(dev, self._proxy)
                    self.devices_all[dev['ADDRESS']] = deviceObject
                    self.devices[dev['PARENT']].CHILDREN[dev['INDEX']] = deviceObject
        return True
    
    def error(self, interface_id, errorcode, msg):
        """When some error occurs the CCU / Homegear will send it's error message here"""
        LOG.debug("RPCFunctions.error: interface_id = %s, errorcode = %i, message = %s" % ( interface_id, int(errorcode), str(msg) ) )
        return True
    
    def saveDevices(self):
        """We save known devices into a json-file so we don't have to work through the whole list of devices the CCU / Homegear presents us"""
        LOG.debug("RPCFunctions.saveDevices: devicefile: %s, _devices_raw: %s" % (self.devicefile, str(self._devices_raw) ) )
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
        LOG.debug("RPCFunctions.event: interface_id = %s, address = %s, value_key = %s, value = %s" % ( interface_id, address, value_key, str(value) ) )
        self.devices_all[address].event(value_key, value)
        if self.eventcallback:
            self.eventcallback(interface_id = interface_id, address = address, value_key = value_key, value = value)
        return True
    
    def listDevices(self, interface_id):
        """The CCU / Homegear asks for devices known to our XML-RPC server. We respond to that request using this method."""
        LOG.debug("RPCFunctions.listDevices: interface_id = %s, _devices_raw = %s" % ( interface_id, str(self._devices_raw) ) )
        return self._devices_raw
    
    def newDevices(self, interface_id, dev_descriptions):
        """The CCU / Homegear informs us about newly added devices. We react on that and add those devices as well."""
        LOG.debug("RPCFunctions.newDevices: interface_id = %s, dev_descriptions = %s" % ( interface_id, str(dev_descriptions) ) )
        for d in dev_descriptions:
            self._devices_raw.append(d)
            self._devices_raw_dict[d['ADDRESS']] = d
        self.saveDevices()
        self.createDeviceObjects()
        return True
    
    def deleteDevices(self, interface_id, addresses):
        """The CCU / Homegear informs us about removed devices. We react on that and remove those devices as well."""
        LOG.debug("RPCFunctions.deleteDevices: interface_id = %s, addresses = %s" % ( interface_id, str(addresses) ) )
        #TODO: remove known deivce objects as well
        self._devices_raw = [ device for device in self._devices_raw if not device['ADDRESS'] in addresses ]
        self.saveDevices()
        return True
    
    def updateDevice(self, interface_id, address, hint):
        LOG.debug("RPCFunctions.updateDevice: interface_id = %s, address = %s, hint = %s" % ( interface_id, address, str(hint) ) )
        #TODO: Implement updateDevice
        return True
    
    def replaceDevice(self, interface_id, oldDeviceAddress, newDeviceAddress):
        LOG.debug("RPCFunctions.replaceDevice: interface_id = %s, oldDeviceAddress = %s, newDeviceAddress = %s" % ( interface_id, oldDeviceAddress, newDeviceAddress ) )
        #TODO: Implement replaceDevice
        return True
    
    def readdedDevice(self, interface_id, addresses):
        LOG.debug("RPCFunctions.readdedDevices: interface_id = %s, addresses = %s" % ( interface_id, str(addresses) ) )
        #TODO: Implement readdedDevice
        return True

# Restrict to particular paths.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/', '/RPC2',)

class ServerThread(threading.Thread):
    """XML-RPC server thread to handle messages from CCU / Homegear"""
    def __init__(   self,
                    local = LOCAL,
                    localport = LOCALPORT,
                    remote = REMOTE,
                    remoteport = REMOTEPORT,
                    devicefile = DEVICEFILE,
                    interface_id = INTERFACE_ID,
                    eventcallback = False):
        LOG.debug("ServerThread.__init__")
        threading.Thread.__init__(self)
        self.interface_id = interface_id
        self.local = local
        self.localport = localport
        self.devicefile = devicefile
        self.eventcallback = eventcallback
        
        # Create proxy to interact with CCU / Homegear
        LOG.info("Creating proxy. Connecting to http://%s:%i" % (remote, int(remoteport)))
        try:
            self.proxy = xmlrpc.client.ServerProxy("http://%s:%i" % (remote, int(remoteport)))
        except:
            LOG.warning("Failed connecting to proxy at http://%s:%i" % (remote, int(remoteport)))
        
        # Setup server to handle requests from CCU / Homegear
        LOG.debug("ServerThread.__init__: Setting up server")
        self.server = SimpleXMLRPCServer( (local, int(localport)),
                            requestHandler=RequestHandler )
        self.server.register_introspection_functions()
        self.server.register_multicall_functions()
        LOG.debug("ServerThread.__init__: Registering RPC functions")
        # We pre-initialize the RPC-Functions so we can access some of its attributes from the server-object
        self.functionObject = RPCFunctions(devicefile = devicefile, proxy = self.proxy, eventcallback = self.eventcallback)
        self.devices_raw = self.functionObject._devices_raw
        self.devices = self.functionObject.devices
        self.devices_all = self.functionObject.devices_all
        
        self.server.register_instance(self.functionObject)

    def run(self):
        LOG.info("Starting server at http://%s:%i" % (self.local, int(self.localport)))
        self.server.serve_forever()
    
    def proxyInit(self):
        """To receive events the proxy has to tell the CCU / Homegear where to send the events. For that we call the init-method."""
        # Call init() with local XML RPC config and interface_id (the name of the receiver) to receive events. XML RPC server has to be running.
        LOG.debug("ServerThread.proxyInit: init(http://%s:%i, '%s')" % (self.local, int(self.localport), self.interface_id) )
        try:
            self.proxy.init("http://%s:%i" % (self.local, int(self.localport)), self.interface_id)
            LOG.info("Proxy initialized")
        except:
            LOG.warning("Failed to initialize proxy")
            raise Exception
    
    def stop(self):
        """To stop the server we de-init from the CCU / Homegear, then shut down our XML-RPC server."""
        if self.proxy:
            LOG.debug("ServerThread.stop: Deregistering proxy")
            try:
                self.proxy.init("http://%s:%i" % (self.local, int(self.localport)))
            except:
                LOG.warning("Failed to deregister proxy")
        LOG.info("Shutting down server")
        self.server.shutdown()
        LOG.debug("ServerThread.stop: Stopping ServerThread")
        self.server.server_close()
        LOG.info("Server stopped")