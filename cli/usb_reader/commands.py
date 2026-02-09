import serial
import requests
import click

@click.command(name="usb-reader", help="Connect to an USB-Reader")
def start(port:str = "/dev/ttyUSB0", baud:int = 115200):
    try:
        ser = serial.Serial(
            port=port,
            baudrate=baud,
            # parity=serial.PARITY_ODD,
            # stopbits=serial.STOPBITS_TWO,
            # bytesize=serial.SEVENBITS
        )
    except serial.SerialException:
        click.echo(click.style("Couldn't connect to a reader. Wrong port?", fg='red'), err=True)
        return

    print(f"Connected to reader on {port}. Start scanning")

    while(True):
        uid = ser.readline()
        uid = uid.decode("utf-8").strip().upper()
        print(f"Scanned tag: {uid}")

        payload = {
                "reader_id" : "0815",
                "tag_id": uid,
                }

        requests.post("https://localhost:5005/scan", json=payload)


    ser.close()
