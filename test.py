import time
import sys
import logging
import click
from pyhomematic import HMConnection
from pyhomematic.devicetypes.sensors import AreaThermostat, ShutterContact, Smoke, Motion
from pyhomematic.devicetypes.helper import HelperLowBat, HelperSabotage, HelperWorking, HelperBatteryState, HelperValveState
from pyhomematic.devicetypes.actors import HMSwitch, HMDimmer


def systemcallback(src, *args):
    print("##### SYSTEMCALLBACK #######")
    print(src)
    for arg in args:
        print(arg)
    print("############################")

def eventcallback(address, interface_id, key, value):
    print("## CALLBACK: %s, %s, %s, %s ##" % (address, interface_id, key, value))


@click.command()
@click.option("--local", "-l", help="Local address for server")
@click.option("--localPort", "-lp", default=8201, help="Local Port for server")
@click.option("--remote", "-r", help="Remote address for CCU/homegear")
@click.option("--remotePort", "-rp", default=2001, help="Remote port for CCU/homegear")
@click.option("--address", "-a", help="Address of homematic device for tests")
@click.option("--channel", "-c", default=1, help="Homematic device channel")
@click.option("--state", "-s", default=1, help="Set STATE value for actors")
@click.option("--timer", "-t", default=30, help="Time in sec for waiting of events (debug)")
@click.option("--debug", "-d", is_flag=True, help="Use DEBUG instead INFO for logger")
def cli(local, localport, remote, remoteport, address, channel, state,
        timer, debug):

    # debug?
    if debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    try:
        # Connect to HM
        pyhomematic = HMConnection(interface_id="test-pyhomatic",
                                   local=local,
                                   localport=localport,
                                   remote=remote,
                                   remoteport=remoteport,
                                   autostart=True,
                                   systemcallback=systemcallback)
    except:
        print("Can't init HMConnection!")
        sys.exit(1)

    sleepcounter = 0

    while not pyhomematic.devices and sleepcounter < 20:
        print("Waiting for devices")
        sleepcounter += 1
        time.sleep(1)
    print(pyhomematic.devices)

    # need test a hm object?
    if address in pyhomematic.devices:
        device = pyhomematic.devices[address]

        print("******************************")
        print("* Show metadata from %s" % address)
        print("* Elements: %i / Childs: %i" % (device.ELEMENT, len(device.CHANNELS)))
        print("* Class: %s" % str(device.__class__))
        print("* Base: %s" % str(device.__class__.__bases__))
        print("* Sensor datapoint: %s" % str(device.SENSORNODE))
        print("* Binary datapoint: %s" % str(device.BINARYNODE))
        print("* Write datapoint: %s" % str(device.WRITENODE))
        print("* Attribute datapoint: %s" % str(device.ATTRIBUTENODE))
        print("******************************")

        # AreaThermostat
        if isinstance(device, AreaThermostat):
            print(" / Temperature: %f" % device.get_temperatur())
            print(" / Humidity: %i" % device.get_humidity())

        # ShutterContact
        if isinstance(device, ShutterContact):
            print(" / Contact open: %s" % str(device.is_open()))

        # Smoke
        if isinstance(device, Smoke):
            print(" / Smoke detect: %s" % str(device.is_smoke()))

        # Motion
        if isinstance(device, Motion):
            print(" / Motion detect: %s" % str(device.is_motion()))
            print(" / Brightness: %i" % device.get_brightness())

        # Switch
        if isinstance(device, HMSwitch):
            print(" / Switch is on: %s" % str(device.is_on(channel)))
            print(" / Changee state to: %s" % str(bool(state)))
            device.set_state(bool(state), channel)
            print(" / Switch is on: %s" % str(device.is_on(channel)))

        ########### Attribute #########
        print(" / RSSI_DEVICE: %i" % device.get_rssi())

        if isinstance(device, HelperLowBat):
            print(" / Low batter: %s" % str(device.low_batt()))

        if isinstance(device, HelperSabotage):
            print(" / Sabotage: %s" % str(device.sabotage()))

        if isinstance(device, HelperWorking):
            print(" / Working: %s" % str(device.is_working()))

        if isinstance(device, HelperValveState):
            print(" / Valve state: %i" % device.valve_state())

        if isinstance(device, HelperBatteryState):
            print(" / Bettery state: %f" % device.battery_state())

    # do nothing for show & debug events
    print("Now waiting for events/callback")
    time.sleep(timer)

    # end
    pyhomematic.stop()

if __name__ == "__main__":
    cli()
