import json
import requests

api_url = "http://localhost:8081/api"

with open("init-db-items.json", "r") as file:
    init_data = json.load(file)

    # Insert categories, resolving parent_title -> parent_id
    title_to_id: dict[str, int] = {}
    for category in init_data.get("categories", []):
        payload = {k: v for k, v in category.items() if k != "parent_title"}
        if parent_title := category.get("parent_title"):
            payload["parent_id"] = title_to_id.get(parent_title)
        response = requests.post(f"{api_url}/categories", json=payload)
        if response.status_code == 200:
            created = response.json()
            title_to_id[category["title"]] = created["id"]
            print(f"Successfully inserted category: {category['title']}")
        else:
            print(
                f"Failed to insert category: {category['title']}. Status code: {response.status_code}, Response: {response.text}"
            )

    for item in init_data.get("items", []):
        response = requests.post(f"{api_url}/items", json=item)
        if response.status_code == 200:
            print(f"Successfully inserted item: {item['short_name']}")
        else:
            print(
                f"Failed to insert item: {item['short_name']}. Status code: {response.status_code}, Response: {response.text}"
            )
    for user in init_data.get("users", []):
        response = requests.post(f"{api_url}/users", json=user)
        if response.status_code == 200:
            print(f"Successfully inserted user: {user['username']}")
        else:
            print(
                f"Failed to insert user: {user['username']}. Status code: {response.status_code}, Response: {response.text}"
            )

    for reader in init_data.get("readers", []):
        response = requests.post(f"{api_url}/readers", json=reader)
        if response.status_code == 200:
            print(f"Successfully inserted reader: {reader['reader_name']}")
        else:
            print(
                f"Failed to insert reader: {reader['reader_name']}. Status code: {response.status_code}, Response: {response.text}"
            )
