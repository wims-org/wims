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
cd esphome/

cp example_secrets.yaml secrets.yaml
cp example_reader.yaml reader.yaml

< Modify the two yaml files>

esphome run esphome/reader.yaml

```
