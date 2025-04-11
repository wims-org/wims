# Handheld scanner

A 3d printed RFID scanner to use with WIMS.

## Parts
* ESP32
* SSD1306 Display
* PN532 RFID reader
* Passive piezo buzzer
* 3D printed case
* Some kind of battery

## Installation
```shell
cp esphome/example_secrets.yaml esphome/secrets.yaml
# modify your secrets.yaml
esphome run esphome/firmware.yaml
```
