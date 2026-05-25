from helper import print_pydantic_error
import click
import requests
from prettytable import PrettyTable


@click.group(name="users", help="Manages users in WIMS")
def command_group():
    pass


@command_group.command()
@click.pass_obj
def list(config):
    table = PrettyTable()
    table.field_names = ["ID", "Username", "Email"]
    table.align = "l"
    resp = requests.get(f"{config['wims']['url']}/users")
    if resp.status_code == 200:
        for r in resp.json():
            table.add_row(
                [
                    r["id"],
                    r["username"],
                    r["email"],
                ]
            )
        print(table)
    else:
        print("BACKEND ERROR")
        print(resp.status_code)
        print(resp.text)


@command_group.command()
@click.pass_obj
def create(config):
    username = input("Username: ")
    email = input("Email: ")
    data = {
        "username": username,
        "email": email,
    }
    resp = requests.post(f"{config['wims']['url']}/users", json=data)
    if resp.status_code == 200:
        data = resp.json()
        print(f"User created with ID '{data['id']}'")
    elif resp.status_code == 422:
        print("Invalid data provided")
        print_pydantic_error(resp.json())
    else:
        print(f"ERROR: {resp.status_code}")
        print(resp.text)


@command_group.command()
@click.pass_obj
@click.argument("id")
def delete(config, id):
    resp = requests.delete(f"{config['wims']['url']}/users/{id}")
    if resp.status_code == 200:
        print("User deletd")
    elif resp.status_code == 404:
        print("No user found with this id")
    else:
        print(f"ERROR: {resp.status_code}")
        print(resp.text)
