import click
from pyhomematic import HMConnection

@click.command()
@click.option("--local", "-l", help="Local address for server")
@click.option("--localPort", "-lp", default=8201 help="Local Port for server")
@click.option("--remote", "-r", help="Remote address for CCU/homegear")
@click.option("--remotePort", "-rp", default=2001 help="Remote port for CCU/homegear")
@click.option("--address", "-a", help="Address of homematic device for tests")
@click.option("--channel", "-c", default=1 help="Homematic device channel")
def cli(local):
