import click

from items import commands as items
from users import commands as users
from readers import commands as readers
from categories import commands as categories
from usb_reader import commands as usb_reader

@click.group()
def cli():
    pass

def main():
    cli.add_command(items.command_group)
    cli.add_command(users.command_group)
    cli.add_command(readers.command_group)
    cli.add_command(categories.command_group)
    cli.add_command(usb_reader.start)
    cli()

if __name__ == "__main__":
    main()
