import click
from .pingos import PortPing

@click.command()
@click.argument('protocol', type=click.Choice(['tcp', 'udp']))
@click.argument('host')
@click.argument('port', type=int)
@click.option('--timeout', '-t', type=float, default=1.0,
              help='Timeout in seconds for each ping')
@click.option('--count', '-c', type=int, default=None,
              help='Number of packets to send (default: unlimited)')
def main(protocol: str, host: str, port: int, timeout: float, count: int):
    """Ping a specific port using TCP or UDP protocol"""
    try:
        pinger = PortPing(host, port, timeout)
        pinger.ping(protocol, count)
    except KeyboardInterrupt:
        click.echo("\nPing interrupted by user")
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

if __name__ == '__main__':
    main() 