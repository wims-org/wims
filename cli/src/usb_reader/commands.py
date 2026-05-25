import click
import requests
import serial
from time import sleep


def register_scanner(config):
    payload = {
        "reader_id": config["wims"]["reader_id"],
        "reader_name": config["wims"]["reader_name"],
    }
    requests.post(f"{config['wims']['url']}/readers", json=payload)


@click.group(name="usb-reader", help="Interact with an attached USB-Reader")
def command_group():
    pass


@command_group.command()
@click.pass_obj
def scan(config):
    try:
        ser = serial.Serial(
            port=config["usb-reader"]["port"], baudrate=config["usb-reader"]["baud"]
        )
    except serial.SerialException:
        click.echo(
            click.style("Couldn't connect to a reader. Wrong port?", fg="red"), err=True
        )
        return

    print("Connected to the reader. Start scanning!")

    register_scanner(config)

    try:
        while True:
            uid = ser.readline()
            uid = uid.decode("utf-8").strip().upper()
            print(f"Scanned tag: {uid}")

            payload = {
                "reader_id": "0815",
                "code_value": uid,
                "code_format": "uuid",
            }

            r = requests.post(f"{config['wims']['url']}/scan", json=payload)
            if r.status_code == 200:
                data = r.json()
                print(
                    f" > {data['item_name']} (Location: {data['item_storage_location']})"
                )
            elif r.status_code == 404:
                print(" > New Item")
            else:
                print(" > ERROR")
                print(r.text)

            # To avoid double scanning
            sleep(1)

    except KeyboardInterrupt:
        print("Goodbye")
        ser.close()
