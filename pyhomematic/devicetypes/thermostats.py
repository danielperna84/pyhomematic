import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.sensors import AreaThermostat
from pyhomematic.devicetypes.helper import HelperValveState, HelperBatteryState, HelperLowBat, HelperLowBatIP

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
        self.COMFORT_MODE = 4
        self.LOWERING_MODE = 5
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
        elif setmode == self.COMFORT_MODE:
            mode = 'COMFORT_MODE'
        elif setmode == self.LOWERING_MODE:
            mode = 'LOWERING_MODE'
        else:
            LOG.warning("Thermostat.MODE.setter: Invalid mode: %s" % str(setmode))
        if mode:
            self.actionNodeData(mode, set_data)

    @property
    def AUTOMODE(self):
        """ Return auto mode state. """
        return self.mode == self.AUTO_MODE

    @property
    def MANUMODE(self):
        """ Return manual mode state. """
        return self.mode == self.MANU_MODE

    @property
    def PARTYMODE(self):
        """ Return party mode state. """
        return self.mode == self.PARTY_MODE

    @property
    def BOOSTMODE(self):
        """ Return boost state. """
        return self.mode == self.BOOST_MODE

    @property
    def COMFORTMODE(self):
        """ Return comfort state. """
        return self.mode == self.COMFORT_MODE

    @property
    def LOWERINGMODE(self):
        """ Return lowering state. """
        return self.mode == self.LOWERING_MODE


class ThermostatGroup(HMThermostat):
    """
    HM-CC-VG-1
    Thermostatgroups made up out of multiple supported thermostats
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1]})
        self.WRITENODE.update({"SET_TEMPERATURE": [1]})
        self.ACTIONNODE.update({"AUTO_MODE": [1],
                                "MANU_MODE": [1],
                                "BOOST_MODE": [1],
                                "COMFORT_MODE": [1],
                                "LOWERING_MODE": [1]})
        self.ATTRIBUTENODE.update({"VALVE_STATE": [1],
                                   "CONTROL_MODE": [1]})


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
                                "BOOST_MODE": [4],
                                "COMFORT_MODE": [4],
                                "LOWERING_MODE": [4]})
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
                                "BOOST_MODE": [2],
                                "COMFORT_MODE": [2],
                                "LOWERING_MODE": [2]})
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

class IPThermostat(HMThermostat, HelperLowBatIP, HelperValveState):
    """
    HPIM-eTRV
    ClimateControl-Radiator Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1]})
        self.WRITENODE.update({"SET_POINT_TEMPERATURE": [1]})
        self.ACTIONNODE.update({"AUTO_MODE": [1],
                                "MANU_MODE": [1],
                                "CONTROL_MODE": [1],
                                "BOOST_MODE": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "OPERATING_VOLTAGE": [0],
                                   "SET_POINT_MODE": [1],
                                   "BOOST_MODE": [1],
                                   "VALVE_STATE": [1]})

    def get_set_temperature(self):
        """ Returns the current target temperature. """
        return self.getWriteData("SET_POINT_TEMPERATURE")

    def set_temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("Thermostat.set_temperature: Exception %s" % (err,))
            return False
        self.writeNodeData("SET_POINT_TEMPERATURE", target_temperature)

    @property
    def MODE(self):
        """ Return mode. """
        if self.getAttributeData("BOOST_MODE"):
            return self.BOOST_MODE
        else:
            return self.getAttributeData("SET_POINT_MODE")

    @MODE.setter
    def MODE(self, setmode):
        """ Set mode. """
        if setmode == self.BOOST_MODE:
            self.actionNodeData('BOOST_MODE', True)
        elif setmode in [self.AUTO_MODE, self.MANU_MODE]:
            if self.getAttributeData("BOOST_MODE"):
                self.actionNodeData('BOOST_MODE', False)
            self.actionNodeData('CONTROL_MODE', setmode)

    def turnoff(self):
        """ Turn off Thermostat. """
        self.writeNodeData("SET_POINT_TEMPERATURE", self.OFF_VALUE)

class IPThermostatWall(HMThermostat, HelperLowBatIP):
    """
    HmIP-STHD
    ClimateControl-Wall Thermostat that measures temperature and allows to set a target temperature or use some automatic mode.
    """
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1],
                                "HUMIDITY": [1]})
        self.WRITENODE.update({"SET_POINT_TEMPERATURE": [1]})
        self.ACTIONNODE.update({"BOOST_MODE": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "SET_POINT_MODE": [1]})

    def get_set_temperature(self):
        """ Returns the current target temperature. """
        return self.getWriteData("SET_POINT_TEMPERATURE")

    def set_temperature(self, target_temperature):
        """ Set the target temperature. """
        try:
            target_temperature = float(target_temperature)
        except Exception as err:
            LOG.debug("Thermostat.set_temperature: Exception %s" % (err,))
            return False
        self.writeNodeData("SET_POINT_TEMPERATURE", target_temperature)

    def turnoff(self):
        """ Turn off Thermostat. """
        self.writeNodeData("SET_POINT_TEMPERATURE", self.OFF_VALUE)


DEVICETYPES = {
    "HM-CC-VG-1": ThermostatGroup,
    "HM-CC-RT-DN": Thermostat,
    "HM-CC-RT-DN-BoM": Thermostat,
    "HM-TC-IT-WM-W-EU": ThermostatWall,
    "HM-CC-TC": ThermostatWall2,
    "ZEL STG RM FWT": ThermostatWall2,
    "BC-RT-TRX-CyG": MAXThermostat,
    "BC-RT-TRX-CyG-2": MAXThermostat,
    "BC-RT-TRX-CyG-3": MAXThermostat,
    "BC-RT-TRX-CyG-4": MAXThermostat,
    "BC-RT-TRX-CyN": MAXThermostat,
    "BC-TC-C-WM-2": MAXWallThermostat,
    "BC-TC-C-WM-4": MAXWallThermostat,
    "HMIP-eTRV": IPThermostat,
    "HmIP-eTRV": IPThermostat,
    "HmIP-eTRV-2": IPThermostat,
    "HmIP-STHD": IPThermostatWall,
    "HmIP-STH": IPThermostatWall,
    "HmIP-WTH-2": IPThermostatWall,
    "HMIP-WTH": IPThermostatWall,
    "HmIP-WTH": IPThermostatWall,
    "HmIP-BWTH": IPThermostatWall,
}
