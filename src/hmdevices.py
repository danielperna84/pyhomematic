import os
# Again some config, here just use for logging
CONFIG_DIR_NAME = '.pyhomematic'
if os.name == "nt":
    data_dir = os.getenv('APPDATA')
else:
    data_dir = os.path.expanduser('~')
CONFIG_PATH = os.path.join(data_dir, CONFIG_DIR_NAME)
if not os.path.isdir(CONFIG_PATH):
    os.makedirs(CONFIG_PATH)

import logging
# Just initialize logging like in pyhomematic.py because of lazyness
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(CONFIG_PATH+os.sep+'pyhomematic.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Parameter operations. Actually just needed if we would get the paramset-descriptions to do some auto-configuration magic.
PARAM_OPERATION_READ = 1
PARAM_OPERATION_WRITE = 2
PARAM_OPERATION_EVENT = 4

class HMDevice(object):
    def __init__(self, device_description, proxy, getparamsetdesriptions = False):
        logger.debug("HMDevice.__init__: device_description: " + str(device_description))
        # These properties are available for every device and its channels
        self._ADDRESS = device_description['ADDRESS']
        self._FAMILY = device_description['FAMILY']
        self._FLAGS = device_description['FLAGS']
        self._ID = device_description['ID']
        self._PARAMSETS = device_description['PARAMSETS']
        self._PARAMSET_DESCRIPTIONS = {}
        self._PARENT = device_description['PARENT']
        self._TYPE = device_description['TYPE']
        self._VERSION = device_description['VERSION']
        self.CHILDREN = {}
        self._proxy = proxy
        self._paramsets = {}
        
        if not self._PARENT:
            # These properties only exist for interfaces themselves
            self._CHILDREN = device_description['CHILDREN']
            self._RF_ADDRESS = device_description['RF_ADDRESS']
            
            # Optional properties might not always be present
            if 'CHANNELS' in device_description:
                self._CHANNELS = device_description['CHANNELS']
            else:
                self._CHANNELS = []
            if 'PHYSICAL_ADDRESS' in device_description:
                self._PHYSICAL_ADDRESS = device_description['PHYSICAL_ADDRESS']
            else:
                self._PHYSICAL_ADDRESS = None
            if 'INTERFACE' in device_description:
                self._INTERFACE = device_description['INTERFACE']
            else:
                self._INTERFACE = None
            if 'ROAMING' in device_description:
                self._ROAMING = device_description['ROAMING']
            else:
                self._ROAMING = None
            if 'RX_MODE' in device_description:
                self._RX_MODE = device_description['RX_MODE']
            else:
                self._RX_MODE = None
            if 'FIRMWARE' in device_description:
                self._FIRMWARE = device_description['FIRMWARE']
            else:
                self._FIRMWARE = None
            if 'AVAILABLE_FIRMWARE' in device_description:
                self._AVAILABLE_FIRMWARE = device_description['AVAILABLE_FIRMWARE']
            else:
                self._AVAILABLE_FIRMWARE = None
            if 'UPDATABLE' in device_description:
                self._UPDATABLE = device_description['UPDATABLE']
            else:
                self._UPDATABLE = False
        else:
            # These properties only exist for device-channels
            self._AES_ACTIVE = device_description['AES_ACTIVE']
            self._DIRECTION = device_description['DIRECTION']
            self._INDEX = device_description['INDEX']
            self._LINK_SOURCE_ROLES = device_description['LINK_SOURCE_ROLES']
            self._LINK_TARGET_ROLES = device_description['LINK_TARGET_ROLES']
            self._PARENT_TYPE = device_description['PARENT_TYPE']
            
            # Optional properties of device-channels
            if 'GROUP' in device_description:
                self._GROUP = device_description['GROUP']
            else:
                self._GROUP = None
            if 'TEAM' in device_description:
                self._TEAM = device_description['TEAM']
            else:
                self._TEAM = None
            if 'TEAM_TAG' in device_description:
                self._TEAM_TAG = device_description['TEAM_TAG']
            else:
                self._TEAM_TAG = None
            if 'TEAM_CHANNELS' in device_description:
                self._TEAM_CHANNELS = device_description['TEAM_CHANNELS']
            else:
                self._TEAM_CHANNELS = None

            # Not in specification, but often present
            if 'CHANNEL' in device_description:
                self._CHANNEL = device_description['CHANNEL']
            else:
                self._CHANNEL = None
        
            self.updateParamsets()
    
    @property
    def ADDRESS(self):
        return self._ADDRESS
    
    @property
    def PARENT(self):
        return self._PARENT
    
    @property
    def TYPE(self):
        return self._TYPE
    
    @property
    def PARAMSETS(self):
        return self._paramsets
    
    def getParamsetDescription(self, paramset):
        """
        Descriptions for paramsets are available to determine what can be don with the device.
        """
        try:
            self._PARAMSET_DESCRIPTIONS[paramset] = self._proxy.getParamsetDescription(self._ADDRESS, paramset)
        except Exception as err:
            logger.debug("HMDevice.getParamsetDescription: Exception: " + str(err))
            return False
    
    def updateParamset(self, paramset):
        """
        Devices should not update their own paramsets. They rely on the state of the server. Hence we pull the specified paramset.
        """
        try:
            if paramset:
                returnset = self._proxy.getParamset(self._ADDRESS, paramset)
                if returnset:
                    self._paramsets[paramset] = returnset
                    return True
                else:
                    logger.warning("HMDevice.updateParamset: Paramset empty.")
            return False
        except Exception as err:
            logger.debug("HMDevice.updateParamset: Exception: " + str(err))
            return False
    
    def updateParamsets(self):
        """
        Devices should update their own paramsets. They rely on the state of the server. Hence we pull all paramsets.
        """
        try:
            for ps in self._PARAMSETS:
                self.updateParamset(ps)
            return True
        except Exception as err:
            logger.debug("HMDevice.updateParamsets: Exception: " + str(err))
            return False
    
    def putParamset(self, paramset, data = {}):
        """
        Some devices act upon changes to paramsets.
        A "putted" paramset must not contain all keys available in the specified paramset, just the ones which are writable and should be changed.
        """
        try:
            if paramset in self._PARAMSETS and data:
                self._proxy.putParamset(self._ADDRESS, paramset, data)
                # We update all paramsets to at least have a temporarily accurate state for the device.
                # This might not be true for tasks that take long to complete (lifting a rollershutter completely etc.).
                # For this the server-process has to call the updateParamsets-method when it receives events concerning the device.
                self.updateParamsets()
                return True
            else:
                return False
        except Exception as err:
            logger.debug("HMDevice.putParamset: Exception: " + str(err))
            return False
    
    def setValue(self, key, value):
        """
        Some devices allow to directly set values to perform a specific task.
        """
        try:
            self._proxy.setValue(self._ADDRESS, key, value)
            return True
        except Exception as err:
            logger.debug("HMDevice.setValue: Exception: " + str(err))
            return False
    
    def getValue(self, key):
        """
        Some devices allow to directly get values for specific parameters
        """
        try:
            returnvalue = self._proxy.getValue(self._ADDRESS, key)
            return returnvalue
        except Exception as err:
            logger.debug("HMDevice.setValue: Exception: " + str(err))
            return False
    
    def event(self, key, value):
        """
        Handle the event received by server.
        """
        logger.debug("HMDevice.event: key=%s, value=%s" % (key, value))

# Subclass HMDevice to add specific device types
class HMRollerShutter(HMDevice):
    """Rollershutter device: "ZEL STG RM FEP 230V" by Roto tronic, which is probably the same as the one from Homematic. Need to check that."""
    def current_position(self):
        """Return current position. Return value is float() from 0.0 (0% open) to 1.0 (100% open)."""
        if self._PARENT:
            return self._proxy.getValue(self._PARENT+':1', 'LEVEL')
        else:
            return self.CHILDREN[1].getValue('LEVEL')
    
    def seek(self, position):
        """Seek a specific position by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            logger.debug("HMRollerShutter.seek: Exception %s" % (err, ))
            return False
        if self._PARENT:
            return self._proxy.setValue(self._PARENT+':1', 'LEVEL', position)
        else:
            return self.CHILDREN[1].setValue('LEVEL', position)
    
    def move_up(self):
        """Move the blind up all the way."""
        return self.seek(1.0)
    
    def move_down(self):
        """Move the blind down all the way."""
        return self.seek(0.0)
    
    def stop(self):
        """Stop moving."""
        if self._PARENT:
            return self._proxy.setValue(self._PARENT+':1', 'STOP', True)
        else:
            return self.CHILDREN[1].setValue('STOP', True)
