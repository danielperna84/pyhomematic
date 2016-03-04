import os
import logging
LOG = logging.getLogger(__name__)

# Parameter operations. Actually just needed if we would get the paramset-descriptions to do some auto-configuration magic.
PARAM_OPERATION_READ = 1
PARAM_OPERATION_WRITE = 2
PARAM_OPERATION_EVENT = 4

class HMDevice(object):
    def __init__(self, device_description, proxy, getparamsetdesriptions = False):
        LOG.debug("HMDevice.__init__: device_description: " + str(device_description))
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
        self._eventcallbacks = []
        
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
    
    @property
    def RSSI_DEVICE(self):
        if self._PARENT:
            RSSI = self._proxy.getValue(self._PARENT, 'RSSI_DEVICE')
        else:
            RSSI = self.getValue('RSSI_DEVICE')
        return RSSI
    
    def getParamsetDescription(self, paramset):
        """
        Descriptions for paramsets are available to determine what can be don with the device.
        """
        try:
            self._PARAMSET_DESCRIPTIONS[paramset] = self._proxy.getParamsetDescription(self._ADDRESS, paramset)
        except Exception as err:
            LOG.debug("HMDevice.getParamsetDescription: Exception: " + str(err))
            return False
    
    def updateParamset(self, paramset):
        """
        Devices should not update their own paramsets. They rely on the state of the server. Hence we pull the specified paramset.
        """
        try:
            if paramset:
                if self._proxy:
                    returnset = self._proxy.getParamset(self._ADDRESS, paramset)
                    if returnset:
                        self._paramsets[paramset] = returnset
                        return True
                    else:
                        LOG.warning("HMDevice.updateParamset: Paramset empty.")
            return False
        except Exception as err:
            LOG.debug("HMDevice.updateParamset: Exception: " + str(err))
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
            LOG.debug("HMDevice.updateParamsets: Exception: " + str(err))
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
            LOG.debug("HMDevice.putParamset: Exception: " + str(err))
            return False
    
    def setValue(self, key, value):
        """
        Some devices allow to directly set values to perform a specific task.
        """
        try:
            self._proxy.setValue(self._ADDRESS, key, value)
            return True
        except Exception as err:
            LOG.debug("HMDevice.setValue: Exception: " + str(err))
            return False
    
    def getValue(self, key):
        """
        Some devices allow to directly get values for specific parameters
        """
        try:
            returnvalue = self._proxy.getValue(self._ADDRESS, key)
            return returnvalue
        except Exception as err:
            LOG.debug("HMDevice.setValue: Exception: " + str(err))
            return False
    
    def event(self, interface_id, key, value):
        """
        Handle the event received by server.
        """
        LOG.info("HMDevice.event: address=%s, interface_id=%s, key=%s, value=%s" % (self._ADDRESS, interface_id, key, value))
        for callback in self._eventcallbacks:
            LOG.debug("HMDevice.event: Using callback %s " % str(callback))
            callback(self._ADDRESS, interface_id, key, value)
    
    def setEventCallback(self, callback, bequeath = True):
        """
        Set additional event callbacks for the device.
        Set the callback for specific channels or use the device itself and let it bequeath the callback to all of its children.
        Signature for callback-functions: foo(address, interface_id, key, value).
        """
        if hasattr(callback, '__call__'):
            self._eventcallbacks.append(callback)
            if bequeath and not self._PARENT:
                for channel, device in self.CHILDREN.items():
                    device._eventcallbacks.append(callback)

# Subclass HMDevice to add specific device types
class HMRollerShutter(HMDevice):
    """
    ZEL STG RM FEP 230V (by Roto tronic, which is probably the same as the one from Homematic. Need to check that.)
    Rollershutter switch that raises and lowers roller shutters.
    """
    
    @property
    def level(self):
        """Return current position. Return value is float() from 0.0 (0% open) to 1.0 (100% open)."""
        if self._PARENT:
            return self._proxy.getValue(self._PARENT+':1', 'LEVEL')
        else:
            return self.CHILDREN[1].getValue('LEVEL')
    
    @level.setter
    def level(self, position):
        """Seek a specific position by specifying a float() from 0.0 to 1.0."""
        try:
            position = float(position)
        except Exception as err:
            LOG.debug("HMRollerShutter.seek: Exception %s" % (err, ))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT+':1', 'LEVEL', position)
        else:
            self.CHILDREN[1].setValue('LEVEL', position)
    
    def move_up(self):
        """Move the shutter up all the way."""
        self.level = 1.0
    
    def move_down(self):
        """Move the shutter down all the way."""
        self.level = 0.0
    
    def stop(self):
        """Stop moving."""
        if self._PARENT:
            self._proxy.setValue(self._PARENT+':1', 'STOP', True)
        else:
            self.CHILDREN[1].setValue('STOP', True)

class HMDoorContact(HMDevice):
    """
    HM-Sec-SC-2
    Door / Window contact that emits its open/closed state.
    """
    @property
    def sabotage(self):
        """ Returns if the devicecase has been opened. """
        if self._PARENT:
            error = self._proxy.getValue(self._PARENT+':1', 'ERROR')
        else:
            error = self.CHILDREN[1].getValue('ERROR')
        if error == 7:
            return True
        else:
            return False
    
    @property
    def low_batt(self):
        """ Returns if the battery is low. """
        return self.getValue('LOWBAT')
    
    @property
    def is_open(self):
        """ Returns if the contact is open. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT+':1', 'STATE')
        else:
            return self.CHILDREN[1].getValue('STATE')
    
    @property
    def is_closed(self):
        """ Returns if the contact is closed. """
        if self._PARENT:
            return not self._proxy.getValue(self._PARENT+':1', 'STATE')
        else:
            return not self.CHILDREN[1].getValue('STATE')
    
    @property
    def state(self):
        """ Returns if the contact is 'open' or 'closed'. """
        if self.is_closed:
            return 'closed'
        else:
            return 'open'

class HMThermostat(HMDevice):
    """
    HM-CC-RT-DN
    ClimateControl-RadiatorThermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    AUTO_MODE = 0
    MANU_MODE = 1
    PARTY_MODE = 2
    BOOST_MODE = 3
        
    @property
    def temperature(self):
        """ Returns the current temperature. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT+':4', 'ACTUAL_TEMPERATURE')
        else:
            return self.CHILDREN[4].getValue('ACTUAL_TEMPERATURE')
    
    @temperature.setter
    def temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("HMThermostat.set_temperature: Exception %s" % (err, ))
            return False
        if self._PARENT:
            self._proxy.setValue(self._PARENT+':4', 'SET_TEMPERATURE', target_temperature)
        else:
            self.CHILDREN[4].setValue('SET_TEMPERATURE', target_temperature)
    
    @property
    def turnoff(self):
        """ Turn off Thermostat. """
        if self._PARENT:
            self._proxy.setValue(self._PARENT+':4', 'SET_TEMPERATURE', 4.5)
        else:
            self.CHILDREN[4].setValue('SET_TEMPERATURE', 4.5)
    
    @property
    def mode(self):
        """ Return mode. """
        if self._PARENT:
            # 1 Manu, 0 Auto, 3 Boost
            return self._proxy.getValue(self._PARENT+':4', 'CONTROL_MODE')
        else:
            return self.CHILDREN[4].getValue("CONTROL_MODE")
    
    @mode.setter
    def mode(self, setmode):
        """ Set mode. """
        if setmode == self.AUTO_MODE:
            mode = 'AUTO_MODE'
        elif setmode == self.MANU_MODE:
            mode = 'MANU_MODE'
        elif setmode == self.PARTY_MODE:
            mode = 'PARTY_MODE'
        elif setmode == self.BOOST_MODE:
            mode = 'BOOST_MODE'
        else:
            return False
        if self._PARENT:
            return self._proxy.setValue(self._PARENT+':4', mode, True)
        else:
            return self.CHILDREN[4].setValue(mode, True)
    
    @property
    def automode(self):
        """ Return auto mode state. """
        return self.mode == self.AUTO_MODE
    
    @automode.setter
    def automode(self, setauto):
        """ Turn on auto mode. """
        self.mode = self.AUTO_MODE
    
    @property
    def manumode(self):
        """ Return manual mode state. """
        return self.mode == self.MANU_MODE
    
    @manumode.setter
    def manumode(self, setmanu):
        """ Turn on manual mode. """
        self.mode = self.MANU_MODE

    @property
    def partymode(self):
        """ Return party mode state. """
        return self.mode == self.PARTY_MODE
    
    @partymode.setter
    def partymode(self, partymode):
        """ Turn on paty mode. """
        self.mode = self.PARTY_MODE
    
    @property
    def boostmode(self):
        """ Return boost state. """
        return self.mode == self.BOOST_MODE
    
    @boostmode.setter
    def boostmode(self, setboost):
        """ Turn on boost mode. """
        self.mode = self.BOOST_MODE
    
    @property
    def battery_state(self):
        """ Returns the current battery state. """
        if self._PARENT:
            return self._proxy.getValue(self._PARENT+':4', 'BATTERY_STATE')
        else:
            return self.CHILDREN[4].getValue('BATTERY_STATE')

DEVICETYPES = {
    "ZEL STG RM FEP 230V" : HMRollerShutter,
    "HM-Sec-SC-2" : HMDoorContact,
    "HM-CC-RT-DN" : HMThermostat,
    "HM-CC-RT-DN-BoM" : HMThermostat
}