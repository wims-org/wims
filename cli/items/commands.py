import click
import requests

@click.group(name="items", help="Manage items in WIMS")
def command_group():
    pass

@command_group.command()
def create():
    print("not yet implemented")

@command_group.command()
def delete():
    print("not yet implemented")

@command_group.command()
def search(query: str):
    payload = {"query": {"term": query}}
    r = requests.post('http://localhost:5005/items/search', json=payload)
    print(r)
