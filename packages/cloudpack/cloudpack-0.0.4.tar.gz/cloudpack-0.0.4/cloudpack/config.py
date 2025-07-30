from pathlib import Path
from configparser import ConfigParser


def save(config: ConfigParser, path: Path) -> None:
    """
    Saves a configuration file to the given path.
    """
    config_path = path / "config.ini"
    with open(config_path, "w") as f:
        config.write(f)


def load(path: Path) -> ConfigParser:
    """
    Loads a configuration file from the given path.
    """
    config_path = path / "config.ini"
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    config = ConfigParser()
    config.read(config_path)
    return config


def list(config: ConfigParser) -> None:
    """
    Lists all configuration values.
    """
    for section in config.sections():
        for key, value in config.items(section):
            print(f"{section}.{key} = {value}")
        print()


def get(config: ConfigParser, key: str) -> str:
    """
    Gets a configuration value by key.
    """
    section, option = key.split(".", 1)
    return config.get(section, option)


def set(config: ConfigParser, key: str, value: str) -> None:
    """
    Sets a configuration value by key.
    """
    section, option = key.split(".", 1)
    config.set(section, option, value)
