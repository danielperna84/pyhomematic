import time
import sys
import logging
import click
from pyhomematic import HMConnection


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
@click.option("--timer", "-t", default=30, help="Time in sec for waiting of events (debug)")
@click.option("--debug", "-d", is_flag=True, help="Use DEBUG instead INFO for logger")
def cli(local, localport, remote, remoteport, address, channel, timer, debug):

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

        print("Show metadata from %s" % address)
        print("Elements: %i / Childs: %i" % (device.ELEMENT, len(device.CHANNELS)))

    # do nothing for show & debug events
    print("Now waiting for events/callback")
    time.sleep(timer)

    # end
    pyhomematic.stop()

if __name__ == "__main__":
    cli()
