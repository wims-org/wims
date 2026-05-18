#! /usr/bin/env python

import requests
import json
from sys import exit
import base64

WIMS_URL = "http://192.168.23.20:4711/api"

with open("eike.json") as fh:
    data = json.load(fh)

items = {}

for x in data:
    item = {
        "short_name": x["short_name"],
        "tags": x["tags"],
        "code": x["tag_uuid"],
    }
    if x["tag_uuid"] == "04-3D-46-42-CD-66-81":
        print(item)
    resp = requests.post(f"{WIMS_URL}/items", json=item)

    if resp.status_code != 200:
        print(resp.text)
        exit(1)
    database_id = resp.json()["id"]
    print(f"created item with id {database_id}")
    items[x["tag_uuid"]] = resp.json()

for x in data:
    images = []
    for img in x["images"]:
        img = img.split(",", 1)[1]
        img = base64.b64decode(img)
        with open("/tmp/image", "wb") as fh:
            fh.write(img)
        files = {"file": open("/tmp/image", "rb")}
        resp = requests.post(f"{WIMS_URL}/files", files=files)
        if resp.status_code != 200:
            print(resp.text)
            exit(1)
        db_image = resp.json()
        images.append(db_image)

    item = items[x["tag_uuid"]]
    item["files"]= images
    item["short_name"]= x["short_name"]

    if x.get("container_tag_uuid"):
        body = {
            "filters": [
                {
                    "field": "code",
                    "value": x["container_tag_uuid"],
                }
            ]
        }
        resp = requests.post(f"{WIMS_URL}/items/search", json=body)
        if resp.status_code != 200:
            print(resp.text)
            exit(1)
        try:
            db_container = resp.json()[0]
            print(f"found container with id {db_container['id']}")
            item["container"] = db_container
            item["container_id"] = db_container['id']
        except IndexError:
            print(f"found NO container for {x['container_tag_uuid']}")


    if x["tag_uuid"] == "04-3D-46-42-CD-66-81":
        print(item)
    resp = requests.put(f"{WIMS_URL}/items/{item['id']}", json=item)
    if resp.status_code != 200:
        print(resp.text)
        exit(1)
