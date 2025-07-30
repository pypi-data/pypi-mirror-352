import click
from cloudpack import vault


@click.group()
def cli():
    pass


@cli.command()
@click.argument("path", type=click.Path(), default=".")
def init(path):
    """Initialize a new vault"""
    vault.init(path)


@cli.group()
def config():
    """Configure the vault"""
    pass


@config.command()
@click.argument("key")
def get(key):
    """Get a config value"""
    vault.configure("get", key)


@config.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    """Set a configuration value"""
    vault.configure("set", key, value)


@config.command()
def list():
    """List all configuration values"""
    vault.configure("list")


@cli.command()
@click.argument("file", type=click.Path(exists=True))
def add(file):
    """Add a file to the vault"""
    vault.add(file)


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
def unlock(path):
    """Unlock the vault"""
    vault.unlock(path)


@cli.command()
@click.argument("path", type=click.Path(exists=True), default=".")
def lock(path):
    """Lock the vault"""
    vault.lock(path)


@cli.command()
def upload():
    """Upload the vault to the cloud"""
    vault.upload()


if __name__ == "__main__":
    cli()
