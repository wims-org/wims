import click

@click.group(name="categories", help="Manage categories in WIMS")
def command_group():
    pass

@command_group.command()
def create():
    print("not yet implemented")

@command_group.command()
def delete():
    print("not yet implemented")

@command_group.command()
def show(query: str):
    print("not yet implemented")
