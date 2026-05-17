import click
import yaml
from os import path
from sys import exit
from xdg import XDG_CONFIG_HOME

from items import commands as items
from users import commands as users
from readers import commands as readers
from categories import commands as categories
from usb_reader import commands as usb_reader

default_config = {
    "wims": {
        "reader_id": "1337",
        "reader_name": "ChangeMe",
        "url": "http://localhost:5005",
    },
    "usb-reader": {
        "port": "/dev/ttyUSB0",
        "baud": 115200,
    },
}


def load_config():
    config = default_config
    conf_file = path.join(XDG_CONFIG_HOME, "wims/config.yaml")
    if path.exists(conf_file):
        # Read existing config file
        with open(conf_file) as fh:
            config = yaml.safe_load(fh)
    else:
        # Create config file on first run
        print("This is your first time using the CLI. Welcome :)")
        print(f"We created a default config file at '{conf_file}'")
        print("Please have a look and change it to your needs.")
        with open(conf_file, "w") as fh:
            yaml.safe_dump(default_config, fh)
        exit(0)

    return config


@click.group()
@click.pass_context
def cli(ctx):
    ctx.obj = load_config()


def main():
    cli.add_command(items.command_group)
    cli.add_command(users.command_group)
    cli.add_command(readers.command_group)
    cli.add_command(categories.command_group)
    cli.add_command(usb_reader.command_group)
    cli()


if __name__ == "__main__":
    main()
