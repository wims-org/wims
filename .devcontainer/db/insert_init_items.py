import json
import requests

with open("init-db-items.json", "r") as file:
    init_data = json.load(file)

    for item in init_data.get("items", []):
        response = requests.post("http://localhost:8000/items", json=item)
        if response.status_code == 200:
            print(f"Successfully inserted item: {item['short_name']}")
        else:
            print(
                f"Failed to insert item: {item['short_name']}. Status code: {response.status_code}, Response: {response.text}"
            )
    for user in init_data.get("users", []):
        response = requests.post("http://localhost:8000/users", json=user)
        if response.status_code == 200:
            print(f"Successfully inserted user: {user['username']}")
        else:
            print(
                f"Failed to insert user: {user['username']}. Status code: {response.status_code}, Response: {response.text}"
            )

    for reader in init_data.get("readers", []):
        response = requests.post("http://localhost:8000/readers", json=reader)
        if response.status_code == 200:
            print(f"Successfully inserted reader: {reader['reader_name']}")
        else:
            print(
                f"Failed to insert reader: {reader['reader_name']}. Status code: {response.status_code}, Response: {response.text}"
            )
