# WIMS Scanner

## Handheld scanner

A 3d printed RFID scanner to use with WIMS.

### Parts
* ESP32
* SSD1306 Display
* PN532 RFID reader
* Passive piezo buzzer
* 3D printed case
* Some kind of battery

### Installation

```shell
cp esphome/example_secrets.yaml esphome/secrets.yaml
# modify your secrets.yaml
esphome run esphome/firmware.yaml
```

## USB Scanner

If you wan't to use a super simple scanner for WIMS, you can build one using an Arduino and a RFID reader board
The current code is for an Arduino Nano and a RC522 reader, but can easily be adapted for different boards or reader.

Heads up: In contrast to the first reader, this one has no connectivity except Serial over USB, and therefore can only
be used together with the wims CLI tool.

### Installation

```shell
cd usb-reader
platformio run -t upload
```
