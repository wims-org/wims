from helper import print_pydantic_error
import click
import serial
import requests
import webbrowser
from prettytable import PrettyTable
from pprint import pprint


@click.group(name="items", help="Manage items in WIMS")
def command_group():
    pass


def print_item_table(items):
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Description", "Category", "Location", "Content"]
    table.align = "l"
    for i in items:
        category = "-"
        location = "-"
        content = "-"

        if i["category"]:
            category = i["category"]["title"]
        if i["container"]:
            location = i["container"]["short_name"]
        if i["content"]:
            content = len(i["content"])

        table.add_row(
            [
                i["id"],
                i["short_name"],
                i["description"],
                category,
                location,
                content,
            ]
        )
    print(table)


@command_group.command()
@click.pass_obj
def list(config):
    resp = requests.get(f"{config['wims']['url']}/items")
    if resp.status_code == 200:
        print_item_table(resp.json())


@command_group.command()
@click.pass_obj
@click.argument("id")
def show(config, id):
    resp = requests.get(f"{config['wims']['url']}/items/{id}")
    pprint(resp.json())
    # TODO: Better output


@command_group.command()
@click.pass_obj
def create(config):
    try:
        ser = serial.Serial(
            port=config["usb-reader"]["port"], baudrate=config["usb-reader"]["baud"]
        )
    except serial.SerialException:
        click.echo(click.style("Couldn't connect to a reader!", fg="red"), err=True)
        return

    print("Please scan the tag")
    try:
        uid = ser.readline()
        uid = uid.decode("utf-8").strip().upper()
        print(f"Tag: {uid}")
    except KeyboardInterrupt:
        print("Goodbye")

    ser.close()

    short_name = input("Name: ")
    description = input("Description: ")
    category = input("Category ID (leave empty for no category): ")
    if category == "":
        category = None
    container = input("Parent item ID (leave empty for no parent): ")
    if container == "":
        container = None

    data = {
        "code": uid,
        "short_name": short_name,
        "description": description,
        "container_id": int(container),
        "category_id": int(category),
    }

    resp = requests.post(f"{config['wims']['url']}/items", json=data)

    if resp.status_code == 200:
        data = resp.json()
        print(f"Item created with ID '{data['id']}'")
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
    resp = requests.delete(f"{config['wims']['url']}/items/{id}")
    if resp.status_code == 200:
        print("Items deletd")
    elif resp.status_code == 404:
        print("No items found with this id")
    else:
        print("BACKEND ERROR")
        print(resp.text)


@command_group.command()
@click.argument("query")
def search(query: str):
    payload = {"term": query}
    resp = requests.post("http://localhost:5005/items/search", json=payload)
    if resp.status_code == 200:
        print_item_table(resp.json())

@command_group.command()
@click.pass_obj
@click.argument("id")
def open(config, id):
    url = f"{config['wims']['url']}/items/{id}"
    webbrowser.open(url, new=0, autoraise=True)
