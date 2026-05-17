from helper import print_pydantic_error
import click
import requests
from prettytable import PrettyTable


@click.group(name="categories", help="Manage categories in WIMS")
def command_group():
    pass


@command_group.command()
@click.pass_obj
def list(config):
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Description"]
    table.align = "l"
    resp = requests.get(f"{config['wims']['url']}/categories")
    for cat in [x for x in resp.json() if x["parent"] is None]:
        table.add_row(
            [
                cat["id"],
                cat["title"],
                cat["description"],
            ]
        )
        for child in cat["children"]:
            table.add_row(
                [
                    child["id"],
                    f"{cat['title']} > {child['title']}",
                    child["description"],
                ]
            )
        table.add_divider()
    print(table)


@command_group.command()
@click.pass_obj
def create(config):
    title = input("Title: ")
    description = input("Description: ")
    parent_id = input("Parent ID (leave empty for top-level): ")
    if parent_id == "":
        parent_id = None

    data = {
        "title": title,
        "description": description,
        "parent_id": parent_id,
    }
    resp = requests.post(f"{config['wims']['url']}/categories", json=data)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Category created with ID '{data['id']}'")
    elif resp.status_code == 422:
        print("Invalid data provided")
        print_pydantic_error(resp.json())
    else:
        print("BACKEND ERROR")
        print(resp.status_code)
        print(resp.text)


@command_group.command()
@click.pass_obj
@click.argument("id")
def delete(config, id):
    resp = requests.delete(f"{config['wims']['url']}/categories/{id}")
    if resp.status_code == 200:
        print("Category deletd")
    elif resp.status_code == 404:
        print("No category found with this id")
    else:
        print("BACKEND ERROR")
        print(resp.text)
