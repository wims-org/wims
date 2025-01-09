import os
from uuid import UUID

import requests
import websockets
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect

import app_config
from models.database import Item
from models.forms import ItemForm

app = Flask(__name__)
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"
# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)
# Flask-WTF requires this line
# TODO enable; Disable CSRF protection for now
app.config["WTF_CSRF_ENABLED"] = False


csrf = CSRFProtect(app)
csrf.init_app(app)

reader: str | None = None


def get_config() -> app_config.Config:
    if os.environ["FLASK_ENV"] == "development":
        return app_config.DevelopmentConfig()
    elif os.environ["FLASK_ENV"] == "testing":
        return app_config.TestingConfig()
    elif os.environ["FLASK_ENV"] == "production":
        return app_config.ProductionConfig()
    else:
        return app_config.Config()


def get_item_by_rfid(rfid: str) -> ItemForm | None:
    # Implement the logic to get item by RFID
    # This is a placeholder implementation
    item_data = {
        "container_tag_id": UUID("123e4567-e89b-12d3-a456-426614174000"),
        "short_name": "Sample Item",
        "description": "This is a sample item description.",
        "amount": 10,
        "category_tags": ["sample", "item"],
        "images": ["image1.jpg", "image2.jpg"],
        "storage_location": "Warehouse A",
        "storage_location_tag_id": "67890",
        "current_location": "Shelf B",
        "borrowed_by": None,
        "cost_per_item": 100.0,
        "manufacturer": "Sample Manufacturer",
        "model_number": "SM1234",
        "upc": "123456789012",
        "asin": "B000123456",
        "serial_number": "SN1234567890",
        "vendor": "Sample Vendor",
        "shop_url": "http://example.com",
        "container_size": "Medium",
        "consumable": False,
        "documentation": "http://example.com/doc",
    }
    return Item(**item_data)


def get_websocket(reader_id: str) -> websockets.WebSocketClientProtocol:
    if not reader_id:
        return None
    if "websocket" not in session:
        session["websocket"] = WebSocketClient(get_config(), reader_id)
    return session["websocket"]


@app.route("/", methods=["GET", "POST"])
def index() -> str | Response:
    reader = request.args.get("reader") or "04-04-46-42-CD-66-81"
    session["reader"] = reader
    # get_websocket(reader)

    return redirect(url_for("menu", reader=reader, rfid="123e4567-e89b-12d3-a456-426614174000"))


@app.route("/menu", methods=["GET", "POST"])
def menu() -> str | tuple[str, int]:
    reader = request.args.get("reader")
    rfid = request.args.get("rfid")
    return render_template("menu.html", reader=reader, rfid=rfid)


def update_item(item: Item) -> None:
    backend_uri = get_config().BACKEND_URI
    endpoint = f"{backend_uri}/item"
    try:
        response = requests.post(endpoint, json=item.model_dump(mode="json"))
        response.raise_for_status()
        flash("Item updated successfully!", "success")
        print("Item updated successfully!", "success")

    except requests.RequestException as e:
        flash(f"Failed to update item: {e}", "danger")
        print(f"Failed to update item: {e}", "danger")


def create_item(item: Item) -> None:
    backend_uri = get_config().BACKEND_URI
    endpoint = f"{backend_uri}/item"
    try:
        response = requests.put(endpoint, json=item.model_dump(mode="json"))
        response.raise_for_status()
        flash("Item created successfully!", "success")
        print("Item created successfully!", "success")
    except requests.RequestException as e:
        flash(f"Failed to create item: {e}", "danger")
        print(f"Failed to create item: {e}", "danger")


@app.route("/item", methods=["GET", "POST"])
def item() -> str | tuple[str, int]:
    reader = request.args.get("reader")
    rfid = request.args.get("rfid")
    print(f"{reader=}, {rfid}")
    if not reader or not rfid:
        return redirect(url_for("index"))
    # Assuming you have a function to get item by RFID
    item_data = get_item_by_rfid(rfid)

    if item_data:
        item_form = ItemForm(
            container_tag_id=str(item_data.container_tag_id),
            short_name=item_data.short_name,
            description=item_data.description,
            amount=item_data.amount,
            category_tags=item_data.category_tags,
            images=item_data.images,
            storage_location=item_data.storage_location,
            storage_location_tag_id=item_data.storage_location_tag_id,
            current_location=item_data.current_location,
            borrowed_by=item_data.borrowed_by,
            cost_per_item=item_data.cost_per_item,
            manufacturer=item_data.manufacturer,
            model_number=item_data.model_number,
            upc=item_data.upc,
            asin=item_data.asin,
            serial_number=item_data.serial_number,
            vendor=item_data.vendor,
            shop_url=item_data.shop_url,
            container_size=item_data.container_size,
            consumable=item_data.consumable,
            documentation=item_data.documentation,
        )
    else:
        item_form = ItemForm()
    message = "Hello"
    if item_form.validate_on_submit():
        # Implement the logic to handle the item form submission
        message = f"Item '{item_data.short_name}' has been submitted."
        item = Item(
            container_tag_id=UUID(item_form.container_tag_id.data),
            short_name=item_form.short_name.data,
            description=item_form.description.data,
            amount=int(item_form.amount.data),
            category_tags=item_form.category_tags.data.split(","),
            images=item_form.images.data.split(","),
            storage_location=item_form.storage_location.data,
            storage_location_tag_id=item_form.storage_location_tag_id.data,
            current_location=item_form.current_location.data,
            borrowed_by=item_form.borrowed_by.data,
            cost_per_item=float(item_form.cost_per_item.data) if item_form.cost_per_item.data else None,
            manufacturer=item_form.manufacturer.data,
            model_number=item_form.model_number.data,
            upc=item_form.upc.data,
            asin=item_form.asin.data,
            serial_number=item_form.serial_number.data,
            vendor=item_form.vendor.data,
            shop_url=item_form.shop_url.data,
            container_size=item_form.container_size.data,
            consumable=item_form.consumable.data.lower() == "true",
            documentation=item_form.documentation.data,
        )
        # update_item(item)
        create_item(item)
        return redirect(url_for("item", reader=reader, rfid=rfid))
    return render_template("item.html", reader=reader, rfid=rfid, item_form=item_form, message=message)


def read_tag(reader: str) -> str:
    reader = request.args.get("reader")
    rfid = request.args.get("rfid")
    if not reader or not rfid:
        return redirect(url_for("index"))
    # Implement the logic to read a tag
    return render_template("read_tag.html", reader=reader)


@app.route("/stream")
def stream() -> str:  # todo add reader: str
    reader = request.args.get("reader")
    def generate():
        backend_uri = get_config().BACKEND_URI
        endpoint = f"{backend_uri}/stream?reader={reader}"
        with requests.get(endpoint, stream=True) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk

    return Response(generate(), content_type="text/event-stream")


@app.route("/tag/<tag_id>")
def tag(reader: str) -> str:
    # Implement the logic to modify a tag
    return render_template("tag.html", reader=reader)


@app.route("/create_user")
def user(reader: str) -> str:
    # Implement the logic to create a new user
    return render_template("create_user.html", reader=reader)


def page_not_found(e: Exception) -> tuple[str, int]:
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e: Exception) -> tuple[str, int]:
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
