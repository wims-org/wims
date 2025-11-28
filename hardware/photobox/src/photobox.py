#!/usr/bin/env python3
import os
import subprocess
import board, busio
from adafruit_pn532.i2c import PN532_I2C
from picamera2 import Picamera2
from PIL import Image, ImageDraw, ImageFont, ImageChops
import io, base64, requests, tempfile
from time import sleep
import RPi.GPIO as GPIO

# GPIO für Button einrichten (z.B. GPIO17, Pin 11)
BUTTON_1 = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_2 = 23
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_3 = 22
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)

BUTTON_4 = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(BUTTON_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# 0) sicherstellen, dass 'fbi' und 'fbset' installiert sind:
#    sudo apt update && sudo apt install fbi fbset

# Hilfsfunktion: aktuelle Framebuffer-Auflösung aus fbset parsen
def get_fb_resolution():
    return 320, 240

def asset_img_confirm(
    size: int = 256,
    circle_color: tuple = (76, 175, 80, 255),
    check_color: tuple = (255, 255, 255, 255),
    check_width_ratio: float = 0.15
    ) -> Image.Image:
    """
    Erzeugt ein Image mit einem grünen Kreis und einem weißen Bestätigungshaken.
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([(0, 0), (size - 1, size - 1)], fill=circle_color)
    check = [
        (size * 0.25, size * 0.52),
        (size * 0.45, size * 0.72),
        (size * 0.75, size * 0.28)
    ]
    draw.line(check, fill=check_color, width=int(size * check_width_ratio), joint='curve')
    return img

def asset_img_cancel(
    size: int = 256,
    circle_color: tuple = (220, 53, 69, 255),  # Bootstrap Red
    x_color: tuple = (255, 255, 255, 255),
    x_width_ratio: float = 0.15
    ) -> Image.Image:
    """
    Erzeugt ein Image mit einem roten Kreis und einem weißen X (Cancel).
    """
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([(0, 0), (size - 1, size - 1)], fill=circle_color)
    # X-Koordinaten
    offset = size * 0.28
    draw.line([(offset, offset), (size - offset, size - offset)], fill=x_color, width=int(size * x_width_ratio))
    draw.line([(size - offset, offset), (offset, size - offset)], fill=x_color, width=int(size * x_width_ratio))
    return img

def show_splash(fb_w, fb_h):
    """Zeigt den Splashscreen an."""
    # Splashscreen anzeigen
    splash = Image.new("RGB", (fb_w, fb_h), (10, 20, 60))  # dunkelblau
    draw = ImageDraw.Draw(splash)
    # Schriftgröße dynamisch anpassen
    splash_font_size = int(fb_w * 0.8)
    try:
        splash_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", splash_font_size)
    except:
        splash_font = ImageFont.load_default()
    text = "WIMS"
    bbox = draw.textbbox((0, 0), text, font=splash_font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    # zentrieren, 80% Breite
    scale = (fb_w * 0.8) / text_w
    font_size = int(splash_font_size * scale)
    try:
        splash_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        splash_font = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), text, font=splash_font)
    text_w, text_h = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (fb_w - text_w) // 2
    y = 30  # 30 Pixel Abstand vom oberen Rand
    draw.text((x, y), text, font=splash_font, fill=(255,255,255))

    # Zusatzzeile darunter
    subtitle = "Tag scannen um Bild aufzunehmen"
    subtitle_font_size = int(font_size * 0.15)
    try:
        subtitle_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", subtitle_font_size)
    except:
        subtitle_font = ImageFont.load_default()
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_w, subtitle_h = subtitle_bbox[2] - subtitle_bbox[0], subtitle_bbox[3] - subtitle_bbox[1]
    subtitle_x = (fb_w - subtitle_w) // 2
    subtitle_y = y + text_h + 26  # 18px Abstand unter Haupttext
    draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(255,255,255))
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        splash.save(tmp, format="JPEG")
        splash_path = tmp.name
    subprocess.run([
        "sudo", "fbi",
        "-T", "2",
        "-d", "/dev/fb0",
        "-noverbose",
        "-a",
        splash_path
    ])

def trim(im):
    min_width, min_height = 1024, 768
    extra = 100

    bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
    diff = ImageChops.difference(im, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        # Expand bbox by extra pixels, but not outside image bounds
        left = max(bbox[0] - extra, 0)
        upper = max(bbox[1] - extra, 0)
        right = min(bbox[2] + extra, im.width)
        lower = min(bbox[3] + extra, im.height)
        # Ensure minimum crop size
        crop_w = right - left
        crop_h = lower - upper
        if crop_w < min_width:
            pad = (min_width - crop_w) // 2
            left = max(left - pad, 0)
            right = min(right + pad + (min_width - crop_w) % 2, im.width)
        if crop_h < min_height:
            pad = (min_height - crop_h) // 2
            upper = max(upper - pad, 0)
            lower = min(lower + pad + (min_height - crop_h) % 2, im.height)
        return im.crop((left, upper, right, lower))
    else:
        return im

# Display‑Auflösung ermitteln
fb_w, fb_h = get_fb_resolution()

# 1) NFC initialisieren
i2c   = busio.I2C(board.SCL, board.SDA)
pn532 = PN532_I2C(i2c, debug=False)
pn532.SAM_configuration()

# 2) Kamera initialisieren (mit Autofokus für Pi Cam v3)
picam2 = Picamera2()
cfg = picam2.create_still_configuration(main={"size": (3456, 2592)}, controls={"AfMode": 2})  # AfMode 2 = Continuous autofocus
picam2.configure(cfg)
picam2.start()
sleep(1)  # kurze Wartezeit, damit Autofokus initialisieren kann

# 3) HTTP-Ziel
URL     = "http://wims.s24/api/items"
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}

# 4) Font laden
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 12)
except:
    font = ImageFont.load_default()

print(f"Framebuffer: {fb_w}x{fb_h}")
print("Bereit - NFC-Tag an den Reader halten…")

show_splash(fb_w, fb_h)


while True:
    # 4) auf Tag warten
    uid = None
    while uid is None:
        uid = pn532.read_passive_target(timeout=1.0)
    tag_uuid = "-".join(f"{b:02X}" for b in uid)
    print(f"→ Gefunden: {tag_uuid}")

    # 5) Item-Infos von REST-API holen
    api_url = f"http://192.168.23.20/api/items/{tag_uuid}"
    try:
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        item_info = response.json()
        print("Item-Info:", item_info["short_name"])

        # Prüfe, ob ein Bild in item_info["images"] vorhanden ist
        img = None
        if "images" in item_info and item_info["images"]:
            img_data = item_info["images"][0]
            if img_data.startswith("data:image"):
                # base64-Teil extrahieren
                b64data = img_data.split(",", 1)[1]
                print("Bilddaten gefunden, dekodiere…")
                # base64 dekodieren und in PIL Image umwandeln
                img_bytes = base64.b64decode(b64data)
                img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
                #img = trim(img)
        # Wenn kein Bild vorhanden, neues Foto aufnehmen
        if img is None:
            arr = picam2.capture_array()
            img = Image.fromarray(arr)
            #img = trim(img)  # optional: Ränder entfernen
    except Exception:
        print("Item nicht gefunden, item wird angelegt")
    
        arr = picam2.capture_array()
        img = Image.fromarray(arr)
        img = trim(img)  # optional: Ränder entfernen

    # 5) Foto aufnehmen + skalieren auf FB-Auflösung
    #arr = picam2.capture_array()
    #img = Image.fromarray(arr)
    #img = trim(img)  # optional: Ränder entfernen
    #img.fromarray(arr).convert("RGB").save(orig_buf, format="JPEG", quality=75, optimize=True, progressive=True)
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=75, optimize=True, progressive=True)
    img_bytes = buffer.getvalue()
    data_uri = "data:image/jpg;base64," + base64.b64encode(img_bytes).decode("ascii")
    #img.thumbnail((fb_w, fb_h), Image.LANCZOS)

    # 6) neues Canvas für Overlay erstellen
    canvas = Image.new("RGB", (fb_w, fb_h), (0, 0, 0))
    # zentriert das Foto im Canvas
    # x = (fb_w - img.width)//2
    # y = (fb_h - img.height)//2
    # Bild proportional auf FB-Auflösung skalieren und zentrieren
    img.thumbnail((fb_w, fb_h), Image.LANCZOS)
    x = (fb_w - img.width) // 2
    y = (fb_h - img.height) // 2
    img = img.convert("RGB")  # sicherstellen, dass es RGB ist
    # und auf Canvas zeichnen
    # oder direkt auf (0, 0) wenn es die gleiche Größe hat  
    canvas.paste(img, (x, y))

    draw = ImageDraw.Draw(canvas)
    # Beispiel: Tag‑UUID oben links
    draw.text((80, 10), tag_uuid, font=font, fill=(255,255,255))
    # Hier kannst Du später beliebige weitere UI‑Elemente malen:
    # draw.rectangle(...), draw.text(...), Buttons, Icons, ...

    # Erzeuge den Emoji-Check mit Größe 128×128
    confirm_img = asset_img_confirm(size=20)
    # Positioniere ihn bei (x=50, y=50) auf dem Canvas
    canvas.paste(confirm_img, (10, 10), confirm_img)

    # Erzeuge den Emoji-Check mit Größe 128×128
    cancel_img = asset_img_cancel(size=20)
    # Positioniere ihn bei (x=50, y=50) auf dem Canvas
    canvas.paste(cancel_img, (10, 65), cancel_img)


    # 7) Canvas als temporäre JPG speichern
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        canvas.save(tmp, format="JPEG")
        tmp_path = tmp.name

    # 8) Anzeige mit fbi
    subprocess.run([
        "sudo", "fbi",
        "-T", "2",
        "-d", "/dev/fb0",
        "-noverbose",
        "-a",
        tmp_path
    ])
    print("Bitte Button drücken, um fortzufahren…")
    print("Button 1: Bild hochladen, Button 2: ohne Upload fortfahren, Button 4: Raspberry Pi herunterfahren")
    while GPIO.input(BUTTON_1) and GPIO.input(BUTTON_2) and GPIO.input(BUTTON_4):
        sleep(0.05)

    # Shutdown falls Button 4 gedrückt wurde
    if not GPIO.input(BUTTON_4):
        print("Button 4 gedrückt – Raspberry Pi wird heruntergefahren…")
        subprocess.run(["sudo", "shutdown", "-h", "now"])
        break

    subprocess.run(["sudo", "killall", "fbi"])

    if not GPIO.input(BUTTON_1):
        # 10) JSON-Payload & POST
        payload = {
            "tag_uuid": tag_uuid,
            "short_name": "gimme a name",
            "amount": 1,
            "item_type": "what am i",
            "tags": ["review"],
            "container_tag_uuid": "1D-5F-77-03-05-10-80",
            "images": [data_uri]
        }
        resp = requests.post(URL, json=payload, headers=HEADERS)
        print(f"→ Server: {resp.status_code} {resp.reason}")
    else:
        print("Upload übersprungen, Zyklus wird neu gestartet.")

    # 11) Debounce: warten, bis Tag entfernt
    print("Bitte Tag entfernen…")
    while pn532.read_passive_target(timeout=1.0) is not None:
        sleep(0.5)
    print("Bereit für den nächsten Zyklus.\n")
    show_splash(fb_w, fb_h)

# ganz am Ende, vor Programmende:
GPIO.cleanup()

