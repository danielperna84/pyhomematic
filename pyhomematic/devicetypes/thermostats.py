import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.sensors import AreaThermostat
from pyhomematic.devicetypes.helper import HelperValveState, HelperBatteryState, HelperLowBat

LOG = logging.getLogger(__name__)


class HMThermostat(HMDevice):
    """
    HM-CC-RT-DN, HM-CC-RT-DN-BoM
    ClimateControl-RadiatorThermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # constante
        self.AUTO_MODE = 0
        self.MANU_MODE = 1
        self.PARTY_MODE = 2
        self.BOOST_MODE = 3
        self.OFF_VALUE = 4.5

        self.mode = None

    def actual_temperature(self):
        """ Returns the current temperature. """
        return self.getSensorData("ACTUAL_TEMPERATURE")

    def get_set_temperature(self):
        """ Returns the current target temperature. """
        return self.getWriteData("SET_TEMPERATURE")

    def set_temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("Thermostat.set_temperature: Exception %s" % (err,))
            return False
        self.writeNodeData("SET_TEMPERATURE", target_temperature)

    def turnoff(self):
        """ Turn off Thermostat. """
        self.writeNodeData("SET_TEMPERATURE", self.OFF_VALUE)

    @property
    def MODE(self):
        """ Return mode. """
        return self.getAttributeData("CONTROL_MODE")

    @MODE.setter
    def MODE(self, setmode):
        """ Set mode. """
        set_data = True
        mode = None
        if setmode == self.AUTO_MODE:
            mode = 'AUTO_MODE'
        elif setmode == self.MANU_MODE:
            mode = 'MANU_MODE'
            set_data = self.get_set_temperature()
        elif setmode == self.BOOST_MODE:
            mode = 'BOOST_MODE'
        else:
            LOG.warning("Thermostat.MODE.setter: Invalid mode: %s" % str(setmode))
        if mode:
            self.actionNodeData(mode, set_data)

    @property
    def AUTOMODE(self):
        """ Return auto mode state. """
        return self.mode == self.AUTO_MODE

    @AUTOMODE.setter
    def AUTOMODE(self, setauto):
        """ Turn on auto mode. """
        self.mode = self.AUTO_MODE

    @property
    def MANUMODE(self):
        """ Return manual mode state. """
        return self.mode == self.MANU_MODE

    @MANUMODE.setter
    def MANUMODE(self, setmanu):
        """ Turn on manual mode. """
        self.mode = self.MANU_MODE

    @property
    def PARTYMODE(self):
        """ Return party mode state. """
        return self.mode == self.PARTY_MODE

    @property
    def BOOSTMODE(self):
        """ Return boost state. """
        return self.mode == self.BOOST_MODE

    @BOOSTMODE.setter
    def BOOSTMODE(self, setboost):
        """ Turn on boost mode. """
        self.mode = self.BOOST_MODE


class Thermostat(HMThermostat, HelperBatteryState, HelperValveState):
    """
    HM-CC-RT-DN, HM-CC-RT-DN-BoM
    ClimateControl-Radiator Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [4]})
        self.WRITENODE.update({"SET_TEMPERATURE": [4]})
        self.ACTIONNODE.update({"AUTO_MODE": [4],
                                "MANU_MODE": [4],
                                "BOOST_MODE": [4]})
        self.ATTRIBUTENODE.update({"VALVE_STATE": [4],
                                   "BATTERY_STATE": [4],
                                   "CONTROL_MODE": [4]})


class ThermostatWall(HMThermostat, AreaThermostat, HelperBatteryState):
    """
    HM-TC-IT-WM-W-EU
    ClimateControl-Wall Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [2],
                                "ACTUAL_HUMIDITY": [2]})
        self.WRITENODE.update({"SET_TEMPERATURE": [2]})
        self.ACTIONNODE.update({"AUTO_MODE": [2],
                                "MANU_MODE": [2],
                                "BOOST_MODE": [2]})
        self.ATTRIBUTENODE.update({"CONTROL_MODE": [2], "BATTERY_STATE": [2]})


class ThermostatWall2(HMThermostat, AreaThermostat, HelperBatteryState):
    """
    HM-CC-TC
    ClimateControl-Wall Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": [1],
                                "HUMIDITY": [1]})
        self.WRITENODE.update({"SETPOINT": [2]})


class MAXThermostat(HMThermostat, HelperLowBat, HelperValveState):
    """
    BC-RT-TRX-CyG, BC-RT-TRX-CyG-2, BC-RT-TRX-CyG-3, BC-RT-TRX-CyG-4
    ClimateControl-Radiator Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1]})
        self.WRITENODE.update({"SET_TEMPERATURE": [1]})
        self.ACTIONNODE.update({"AUTO_MODE": [1],
                                "MANU_MODE": [1],
                                "BOOST_MODE": [1]})
        self.ATTRIBUTENODE.update({"LOWBAT": [0],
                                   "CONTROL_MODE": [1],
                                   "VALVE_STATE": [1]})
        
class MAXWallThermostat(HMThermostat, HelperLowBat):
    """
    BC-TC-C-WM-4
    ClimateControl-Wall Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1]})
        self.WRITENODE.update({"SET_TEMPERATURE": [1]})
        self.ACTIONNODE.update({"AUTO_MODE": [1],
                                "MANU_MODE": [1],
                                "BOOST_MODE": [1]})
        self.ATTRIBUTENODE.update({"LOWBAT": [0], "CONTROL_MODE": [1]})

DEVICETYPES = {
    "HM-CC-RT-DN": Thermostat,
    "HM-CC-RT-DN-BoM": Thermostat,
    "HM-TC-IT-WM-W-EU": ThermostatWall,
    "HM-CC-TC": ThermostatWall2,
    "ZEL STG RM FWT": ThermostatWall2,
    "BC-RT-TRX-CyG": MAXThermostat,
    "BC-RT-TRX-CyG-2": MAXThermostat,
    "BC-RT-TRX-CyG-3": MAXThermostat,
    "BC-RT-TRX-CyG-4": MAXThermostat,
    "BC-TC-C-WM-4": MAXWallThermostat
}
