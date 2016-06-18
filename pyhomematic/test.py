import click
from pyhomematic import HMConnection

def systemcallback(src, *args):
    print(src)
    for arg in args:
        print(arg)

def eventcallback(address, interface_id, key, value):
    print("CALLBACK: %s, %s, %s, %s" % (address, interface_id, key, value))


@click.command()
@click.option("--local", "-l", help="Local address for server")
@click.option("--localPort", "-lp", default=8201 help="Local Port for server")
@click.option("--remote", "-r", help="Remote address for CCU/homegear")
@click.option("--remotePort", "-rp", default=2001 help="Remote port for CCU/homegear")
@click.option("--address", "-a", help="Address of homematic device for tests")
@click.option("--channel", "-c", default=1 help="Homematic device channel")
@click.option("--time", "-t", default=30 help="Time in sec for waiting of events (debug)")
def cli(local, localPort, remote, remotePort, address, channel, time):

    try:
        # Connect to HM
        pyhomematic = HMConnection(interface_id="test-pyhomatic",
                                   local=local,
                                   localport=localPort,
                                   remote=remote,
                                   remoteport=remotePort,
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
