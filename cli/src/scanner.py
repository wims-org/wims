import serial
import typer
import requests

app = typer.Typer()

@app.command()
def start(port:str = "/dev/ttyUSB0", baud:int = 115200):

    print(f"Starting scanner on {port}")

    ser = serial.Serial(
        port=port,
        baudrate=baud,
        # parity=serial.PARITY_ODD,
        # stopbits=serial.STOPBITS_TWO,
        # bytesize=serial.SEVENBITS
    )

    while(True):
        uid = ser.readline()
        uid = uid.decode("utf-8").strip().upper()
        print(f"Scanned tag: {uid}")

        payload = {
                "reader_id" : "0815",
                "tag_id": uid,
                }

        requests.post("https://wims.projects.fleaz.me/api/scan", json=payload)


    ser.close()
