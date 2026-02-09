import click

@click.group(name="readers", help="Manage readers in WIMS")
def command_group():
    print("not yet implemented")

@command_group.command()
def create():
    print("not yet implemented")

@command_group.command()
def delete():
    print("not yet implemented")
