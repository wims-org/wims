import os
from logging.config import dictConfig

import requests
from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap5
from flask_cors import CORS
from flask_wtf import CSRFProtect

import app_config
from models.database import Item
from models.forms import ItemForm

dictConfig(
    {
        "version": 1,
        "formatters": {
            "default": {
                "format": "[%(levelname)s]: %(module)s: %(message)s",
            }
        },
        "handlers": {
            "wsgi": {
                "class": "logging.StreamHandler",
                "stream": "ext://flask.logging.wsgi_errors_stream",
                "formatter": "default",
            }
        },
        "root": {"level": "DEBUG", "handlers": ["wsgi"]},
    }
)

app = Flask(__name__)
app.secret_key = "tO$&!|0wkamvVia0?n$NqIRVWOG"
# Bootstrap-Flask requires this line
bootstrap = Bootstrap5(app)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5002",
                "http://localhost:5000",
                "http://localhost:5005",
                "http://localhost:8000",
                "http://localhost",
                "https://localhost",
                "http://localhost:8080",
            ]
        }
    },
)


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
    try:
        app.logger.debug(f"Get: {rfid}")
        backend_uri = get_config().BACKEND_URI
        res = requests.get(f"{backend_uri}/item/{rfid}")
        app.logger.debug(f"Response: {res}")
        if res.status_code == 404:
            return None
        return Item(**res.json())
    except requests.RequestException as e:
        app.logger.error(f"Failed to get item by RFID: {e}")
    return None


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
        app.logger.debug("Item updated successfully!", "success")

    except requests.RequestException as e:
        flash(f"Failed to update item: {e}", "danger")
        app.logger.debug(f"Failed to update item: {e}", "danger")


def create_item(item: Item) -> None:
    backend_uri = get_config().BACKEND_URI
    endpoint = f"{backend_uri}/item"
    try:
        response = requests.put(endpoint, json=item.model_dump(mode="json"))
        response.raise_for_status()
        flash("Item created successfully!", "success")
        app.logger.debug("Item created successfully!", "success")
    except requests.RequestException as e:
        flash(f"Failed to create item: {e}", "danger")
        app.logger.debug(f"Failed to create item: {e}", "danger")


@app.route("/item/<rfid>", methods=["GET", "POST"])
def item(rfid) -> str | tuple[str, int]:
    reader_id = request.args.get("reader")
    app.logger.debug(f"{reader_id=}, {rfid}")
    if not reader_id or not rfid:
        return redirect(url_for("index"))
    # Assuming you have a function to get item by RFID
    item_res = get_item_by_rfid(rfid)
    item_data = item_res if item_res else Item(container_tag_id=rfid)
    if item_res:
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
        item_form = ItemForm(container_tag_id=str(item_data.container_tag_id))
    message = "Hello"
    if item_form.validate_on_submit():
        # Implement the logic to handle the item form submission
        message = f"Item '{item_data.short_name}' has been submitted."
        item = Item(
            container_tag_id=item_form.container_tag_id.data,
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
        if item_res:
            update_item(item)
        else:
            create_item(item)
        return redirect(url_for("item", reader=reader_id, rfid=rfid))
    return render_template("item.html", reader=reader_id, rfid=rfid, item_form=item_form, message=message)


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
