from helper import print_pydantic_error
import click
import requests
from prettytable import PrettyTable


@click.group(name="readers", help="Manage readers in WIMS")
def command_group():
    pass


@command_group.command()
@click.pass_obj
def list(config):
    table = PrettyTable()
    table.field_names = ["ID", "Name", "Reader-ID"]
    table.align = "l"
    resp = requests.get(f"{config['wims']['url']}/readers")
    for r in resp.json():
        table.add_row(
            [
                r["id"],
                r["reader_name"],
                r["reader_id"],
            ]
        )
    print(table)


@command_group.command()
@click.pass_obj
def create(config):
    reader_name = input("Reader Name: ")
    reader_id = input("Reader ID: ")
    data = {
        "reader_name": reader_name,
        "reader_id": reader_id,
    }
    resp = requests.post(f"{config['wims']['url']}/readers", json=data)
    if resp.status_code == 200:
        data = resp.json()
        print(f"Reader created with ID '{data['id']}'")
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
    resp = requests.delete(f"{config['wims']['url']}/readers/{id}")
    if resp.status_code == 200:
        print("Reader deletd")
    elif resp.status_code == 404:
        print("No reader found with this id")
    else:
        print("BACKEND ERROR")
        print(resp.text)
