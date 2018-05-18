import logging
from pyhomematic.devicetypes.generic import HMDevice
from pyhomematic.devicetypes.misc import HMEvent, Remote
from pyhomematic.devicetypes.helper import (HelperLowBat, HelperSabotage,
                                            HelperLowBatIP, HelperSabotageIP,
                                            HelperBinaryState,
                                            HelperSensorState,
                                            HelperWired)

LOG = logging.getLogger(__name__)


class HMSensor(HMDevice):
    pass


class HMBinarySensor(HMDevice):
    pass


class IPShutterContact(HMBinarySensor, HelperBinaryState, HelperLowBat):
    """Door / Window contact that emits its open/closed state."""
    def is_open(self, channel=None):
        """ Returns True if the contact is open. """
        return self.get_state(channel)

    def is_closed(self, channel=None):
        """ Returns True if the contact is closed. """
        return not self.get_state(channel)

    @property
    def ELEMENT(self):
        if "HM-SCI-3-FM" in self._TYPE:
            return [1, 2, 3]
        return [1]


class ShutterContact(IPShutterContact, HelperSabotage):
    """Door / Window contact that emits its open/closed state."""
    pass


class MaxShutterContact(HMBinarySensor, HelperBinaryState, HelperLowBat):
    """Door / Window contact that emits its open/closed state."""
    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.ATTRIBUTENODE.update({"LOWBAT": [0]})


class TiltSensor(HMBinarySensor, HelperBinaryState, HelperLowBat):
    """Sensor that emits its tilted state."""
    def is_tilted(self, channel=None):
        """ Returns True if the contact is tilted. """
        return self.get_state(channel)

    def is_not_tilted(self, channel=None):
        """ Returns True if the contact is not tilted. """
        return not self.get_state(channel)


class RotaryHandleSensor(HMSensor, HelperSensorState, HelperLowBat, HelperSabotage):
    """Window handle contact."""
    def is_open(self, channel=None):
        """ Returns True if the handle is set to open. """
        return self.get_state(channel) == 2

    def is_closed(self, channel=None):
        """ Returns True if the handle is set to closed. """
        return self.get_state(channel) == 0

    def is_tilted(self, channel=None):
        """ Returns True if the handle is set to tilted. """
        return self.get_state(channel) == 1


class RotaryHandleSensorIP(HMSensor, HelperSensorState, HelperLowBatIP, HelperSabotageIP):
    """Window handle contact."""
    def is_open(self, channel=None):
        """ Returns True if the handle is set to open. """
        return self.get_state(channel) == 2

    def is_closed(self, channel=None):
        """ Returns True if the handle is set to closed. """
        return self.get_state(channel) == 0

    def is_tilted(self, channel=None):
        """ Returns True if the handle is set to tilted. """
        return self.get_state(channel) == 1


class CO2Sensor(HMSensor, HelperSensorState):
    """CO2 Sensor"""
    def is_normal(self, channel=None):
        """ Returns True if CO2 state is normal. """
        return self.get_state(channel) == 0

    def is_added(self, channel=None):
        """ Returns True if CO2 state is added. """
        return self.get_state(channel) == 1

    def is_added_strong(self, channel=None):
        """ Returns True if CO2 state is added strong. """
        return self.get_state(channel) == 2


class WaterSensor(HMSensor, HelperSensorState, HelperLowBat):
    """Watter detect sensor."""

    def is_dry(self, channel=None):
        """Return True if the state is DRY"""
        return self.get_state(channel) == 0

    def is_wet(self, channel=None):
        """Return True if the state is WET"""
        return self.get_state(channel) == 1

    def is_water(self, channel=None):
        """Return True if the state is WATER"""
        return self.get_state(channel) == 2


class PowermeterGas(HMSensor):
    """Powermeter for Gas and energy."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.SENSORNODE.update({"GAS_ENERGY_COUNTER": [1],
                                "GAS_POWER": [1],
                                "ENERGY_COUNTER": [1],
                                "POWER": [1]})

    def get_gas_counter(self, channel=None):
        """Return gas counter."""
        return float(self.getSensorData("GAS_ENERGY_COUNTER", channel))

    def get_gas_power(self, channel=None):
        """Return gas power."""
        return float(self.getSensorData("GAS_POWER", channel))

    def get_energy(self, channel=None):
        """Return energy counter."""
        return float(self.getSensorData("ENERGY_COUNTER", channel))

    def get_power(self, channel=None):
        """Return power counter."""
        return float(self.getSensorData("POWER", channel))


class Smoke(HMBinarySensor, HelperBinaryState):
    """Smoke alarm."""

    def is_smoke(self, channel=None):
        """ Return True if smoke is detected """
        return self.get_state(channel)


class SmokeV2(Smoke, HelperLowBat):
    """Smoke alarm with Battery."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.ATTRIBUTENODE.update({"ERROR_ALARM_TEST": self.ELEMENT,
                                   "ERROR_SMOKE_CHAMBER": self.ELEMENT})


class IPSmoke(HMSensor):
    """HomeMatic IP Smoke sensor"""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"SMOKE_DETECTOR_ALARM_STATUS": self.ELEMENT})


    @property
    def ELEMENT(self):
        return [1]

class GongSensor(HMEvent):
    """Wireless Gong Sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"PRESS_SHORT": self.ELEMENT})


class WiredSensor(HMEvent, HelperWired):
    """Wired binary Sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        self.EVENTNODE.update({"SENSOR": self.ELEMENT})

    @property
    def ELEMENT(self):
        return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    def get_state(self, channel=None):
        """ Returns current state of sensor """
        return bool(self.getBinaryData("SENSOR", channel))


class FillingLevel(HMSensor):
    """Filling level sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"FILLING_LEVEL": self.ELEMENT})

    def get_level(self, channel=None):
        """ Return filling level from 0 to 100 % """
        return int(self.getSensorData("FILLING_LEVEL", channel))

    @property
    def ELEMENT(self):
        return [1]


class ValveDrive(HMSensor):
    """Valve drive HM-CC-VD."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"VALVE_STATE": self.ELEMENT})

    def get_level(self, channel=None):
        """ Return valve state from 0% to 99% """
        return int(self.getSensorData("VALVE_STATE", channel))

    @property
    def ELEMENT(self):
        return [1]


class Motion(HMBinarySensor, HMSensor):
    """Motion detection."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION": self.ELEMENT})
        self.SENSORNODE.update({"BRIGHTNESS": self.ELEMENT})

    def is_motion(self, channel=None):
        """ Return True if motion is detected """
        return bool(self.getBinaryData("MOTION", channel))

    def get_brightness(self, channel=None):
        """ Return brightness from 0 (dark ) to 255 (bright) """
        return int(self.getSensorData("BRIGHTNESS", channel))


class MotionV2(Motion, HelperSabotage):
    """Motion detection version 2."""
    pass


class MotionIP(HMBinarySensor, HMSensor):
    """Motion detection indoor (rf ip)"""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION_DETECTION_ACTIVE": [1], "MOTION": [1]})
        self.SENSORNODE.update({"ILLUMINATION": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0], "ERROR_CODE": [0], "SABOTAGE": [0]})

    def is_motion(self, channel=None):
        """ Return True if motion is detected """
        return bool(self.getBinaryData("MOTION", channel))

    def is_motion_detection_active(self, channel=None):
        return bool(self.getBinaryData("MOTION_DETECTION_ACTIVE", channel))

    def get_brightness(self, channel=None):
        """ Return brightness from 0 (dark) to 163830 (bright) """
        return float(self.getSensorData("ILLUMINATION", channel))

    def low_batt(self, channel=None):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOW_BAT", channel)

    def sabotage(self, channel=None):
        """Returns True if the devicecase has been opened."""
        return bool(self.getAttributeData("SABOTAGE", channel))

    @property
    def ELEMENT(self):
        return [0, 1]


class PresenceIP(HMBinarySensor, HMSensor):
    """Presence detection with HmIP-SPI"""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"PRESENCE_DETECTION_STATE": [1]})
        self.SENSORNODE.update({"ILLUMINATION": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "ERROR_CODE": [0],
                                   "SABOTAGE": [0]})

    def is_motion(self, channel=None):
        """ Return True if motion is detected """
        return bool(self.getBinaryData("PRESENCE_DETECTION_STATE", channel))

    def get_brightness(self, channel=None):
        """ Return brightness from 0 (dark) to 163830 (bright) """
        return float(self.getSensorData("ILLUMINATION", channel))

    def low_batt(self, channel=None):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOW_BAT", channel)

    def sabotage(self, channel=None):
        """Returns True if the devicecase has been opened."""
        return bool(self.getAttributeData("SABOTAGE", channel))

    @property
    def ELEMENT(self):
        return [0, 1]


class TiltIP(HMBinarySensor, HMSensor):
    """Tilt detection with HmIP-SAM"""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "ERROR_CODE": [0]})

    def is_motion(self, channel=None):
        """ Return True if motion is detected """
        return bool(self.getBinaryData("MOTION", channel))

    def low_batt(self, channel=None):
        """ Returns if the battery is low. """
        return self.getAttributeData("LOW_BAT", channel)

    @property
    def ELEMENT(self):
        return [0, 1]


class RemoteMotion(Remote, Motion):
    """Motion detection with buttons."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.BINARYNODE.update({"MOTION": [3]})
        self.SENSORNODE.update({"BRIGHTNESS": [3]})

    @property
    def ELEMENT(self):
        return [1, 2]


class LuxSensor(HMSensor):
    """Sensor for messure LUX."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"LUX": [1]})

    def get_lux(self, channel=None):
        """Return messure lux."""
        return float(self.getSensorData("LUX", channel))


class ImpulseSensor(HMEvent):
    """Inpulse sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.EVENTNODE.update({"SEQUENCE_OK": self.ELEMENT})


class AreaThermostat(HMSensor):
    """Wall mount thermostat."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": self.ELEMENT,
                                "HUMIDITY": self.ELEMENT})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("TEMPERATURE", channel))

    def get_humidity(self, channel=None):
        return int(self.getSensorData("HUMIDITY", channel))


class IPAreaThermostat(HMSensor):
    """Wall mount thermostat."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1],
                                "HUMIDITY": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0]})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("ACTUAL_TEMPERATURE", channel))

    def get_humidity(self, channel=None):
        return int(self.getSensorData("HUMIDITY", channel))


class TemperatureSensor(HMSensor):
    """Temperature Sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": self.ELEMENT})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("TEMPERATURE", channel))


class TemperatureDiffSensor(HMSensor):
    """Temperature difference Sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": [1, 2, 3, 4]})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("TEMPERATURE", channel))


class WeatherSensor(HMSensor, HMBinarySensor):
    """Weather sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": self.ELEMENT,
                                "HUMIDITY": self.ELEMENT,
                                "RAIN_COUNTER": self.ELEMENT,
                                "WIND_SPEED": self.ELEMENT,
                                "WIND_DIRECTION": self.ELEMENT,
                                "WIND_DIRECTION_RANGE": self.ELEMENT,
                                "SUNSHINEDURATION": self.ELEMENT,
                                "BRIGHTNESS": self.ELEMENT})
        self.BINARYNODE.update({"RAINING": self.ELEMENT})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("TEMPERATURE", channel))

    def get_humidity(self, channel=None):
        return int(self.getSensorData("HUMIDITY", channel))

    def get_rain_counter(self, channel=None):
        return float(self.getSensorData("RAIN_COUNTER", channel))

    def get_wind_speed(self, channel=None):
        return float(self.getSensorData("WIND_SPEED", channel))

    def get_wind_direction(self, channel=None):
        return int(self.getSensorData("WIND_DIRECTION", channel))

    def get_wind_direction_range(self, channel=None):
        return int(self.getSensorData("WIND_DIRECTION_RANGE", channel))

    def get_sunshineduration(self, channel=None):
        return int(self.getSensorData("SUNSHINEDURATION", channel))

    def get_brightness(self, channel=None):
        return int(self.getSensorData("BRIGHTNESS", channel))

    def is_raining(self, channel=None):
        """ Return True if motion is detected """
        return bool(self.getBinaryData("RAINING", channel))


class IPWeatherSensor(HMSensor, HMBinarySensor):
    """HomeMatic IP Weather sensor."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"ACTUAL_TEMPERATURE": [1],
                                "HUMIDITY": [1],
                                "RAIN_COUNTER": [1],
                                "WIND_SPEED": [1],
                                "WIND_DIR": [1],
                                "WIND_DIR_RANGE": [1],
                                "SUNSHINEDURATION": [1],
                                "ILLUMINATION": [1]})
        self.BINARYNODE.update({"RAINING": [1]})
        self.ATTRIBUTENODE.update({"LOW_BAT": [0],
                                   "ERROR_CODE": [0],
                                   "OPERATING_VOLTAGE": [0],
                                   "TEMPERATURE_OUT_OF_RANGE": [0]})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("ACTUAL_TEMPERATURE", channel))

    def get_humidity(self, channel=None):
        return int(self.getSensorData("HUMIDITY", channel))

    def get_rain_counter(self, channel=None):
        return float(self.getSensorData("RAIN_COUNTER", channel))

    def get_wind_speed(self, channel=None):
        return float(self.getSensorData("WIND_SPEED", channel))

    def get_wind_direction(self, channel=None):
        return int(self.getSensorData("WIND_DIR", channel))

    def get_wind_direction_range(self, channel=None):
        return int(self.getSensorData("WIND_DIR_RANGE", channel))

    def get_sunshineduration(self, channel=None):
        return int(self.getSensorData("SUNSHINEDURATION", channel))

    def get_brightness(self, channel=None):
        return int(self.getSensorData("ILLUMINATION", channel))

    def get_operating_voltage(self, channel=None):
        return float(self.getAttributeData("OPERATING_VOLTAGE", channel))

    def is_raining(self, channel=None):
        return bool(self.getBinaryData("RAINING", channel))

    def is_low_batt(self, channel=None):
        return bool(self.getAttributeData("LOW_BAT", channel))

    def is_temperature_out_of_range(self, channel=None):
        return bool(self.getAttributeData("TEMPERATURE_OUT_OF_RANGE", channel))


class WeatherStation(HMSensor):
    """Weather station."""

    def __init__(self, device_description, proxy, resolveparamsets=False):
        super().__init__(device_description, proxy, resolveparamsets)

        # init metadata
        self.SENSORNODE.update({"TEMPERATURE": self.ELEMENT,
                                "HUMIDITY": self.ELEMENT,
                                "AIR_PRESSURE": self.ELEMENT})

    def get_temperature(self, channel=None):
        return float(self.getSensorData("TEMPERATURE", channel))

    def get_humidity(self, channel=None):
        return int(self.getSensorData("HUMIDITY", channel))

    def get_air_pressure(self, channel=None):
        return int(self.getSensorData("AIR_PRESSURE", channel))


DEVICETYPES = {
    "HM-Sec-SC": ShutterContact,
    "HM-Sec-SC-2": ShutterContact,
    "HM-Sec-SCo": ShutterContact,
    "ZEL STG RM FFK": ShutterContact,
    "BC-SC-Rd-WM-2": MaxShutterContact,
    "BC-SC-Rd-WM": MaxShutterContact,
    "HM-SCI-3-FM": IPShutterContact,
    "HMIP-SWDO": IPShutterContact,
    "HmIP-SWDO": IPShutterContact,
    "HmIP-SWDO-I": IPShutterContact,
    "HmIP-SRH": RotaryHandleSensorIP,
    "HM-Sec-RHS": RotaryHandleSensor,
    "ZEL STG RM FDK": RotaryHandleSensor,
    "HM-Sec-RHS-2": RotaryHandleSensor,
    "HM-Sec-xx": RotaryHandleSensor,
    "HM-Sec-WDS": WaterSensor,
    "HM-Sec-WDS-2": WaterSensor,
    "HM-ES-TX-WM": PowermeterGas,
    "HM-Sen-DB-PCB": GongSensor,
    "HM-Sec-SD": Smoke,
    "HM-Sec-SD-Generic": Smoke,
    "HM-Sec-SD-2": SmokeV2,
    "HM-Sec-SD-2-Generic": SmokeV2,
    "HmIP-SWSD": IPSmoke,
    "HM-Sen-MDIR-WM55": RemoteMotion,
    "HM-Sen-MDIR-SM": Motion,
    "HM-Sen-MDIR-O": Motion,
    "HM-MD": Motion,
    "HM-Sen-MDIR-O-2": Motion,
    "HM-Sec-MDIR-3": MotionV2,
    "HM-Sec-MDIR-2": MotionV2,
    "HM-Sec-MDIR": MotionV2,
    "263 162": MotionV2,
    "HM-Sec-MD": MotionV2,
    "HmIP-SMI": MotionIP,
    "HmIP-SMO": MotionIP,
    "HmIP-SMO-A": MotionIP,
    "HmIP-SPI": PresenceIP,
    "HM-Sen-LI-O": LuxSensor,
    "HM-Sen-EP": ImpulseSensor,
    "HM-Sen-X": ImpulseSensor,
    "ASH550I": AreaThermostat,
    "ASH550": AreaThermostat,
    "HM-WDS10-TH-O": AreaThermostat,
    "HM-WDS20-TH-O": AreaThermostat,
    "HM-WDS40-TH-I": AreaThermostat,
    "HM-WDS40-TH-I-2": AreaThermostat,
    "263 157": AreaThermostat,
    "263 158": AreaThermostat,
    "IS-WDS-TH-OD-S-R3": AreaThermostat,
    "HM-WDS100-C6-O": WeatherSensor,
    "HM-WDS100-C6-O-2": WeatherSensor,
    "KS550": WeatherSensor,
    "KS888": WeatherSensor,
    "KS550Tech": WeatherSensor,
    "KS550LC": WeatherSensor,
    "HmIP-SWO-PR": IPWeatherSensor,
    "WS550": WeatherStation,
    "WS888": WeatherStation,
    "WS550Tech": WeatherStation,
    "WS550LCB": WeatherStation,
    "WS550LCW": WeatherStation,
    "HM-WDC7000": WeatherStation,
    "HM-Sec-TiS": TiltSensor,
    "HM-CC-SCD": CO2Sensor,
    "263 160": CO2Sensor,
    "HM-WDS30-OT2-SM": TemperatureDiffSensor,
    "HM-WDS30-OT2-SM-2": TemperatureDiffSensor,
    "HM-WDS30-T-O": TemperatureSensor,
    "S550IA": TemperatureSensor,
    "HM-Sen-Wa-Od": FillingLevel,
    "HMW-Sen-SC-12-DR": WiredSensor,
    "HMW-Sen-SC-12-FM": WiredSensor,
    "HM-CC-VD": ValveDrive,
    "ZEL STG RM FSA": ValveDrive,
    "HmIP-SAM": TiltIP,
    "HmIP-STHO": IPAreaThermostat,
    "HmIP-STHO-A": IPAreaThermostat,
}
