from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, ReadOnly


class ItemForm(FlaskForm):
    save = SubmitField("Save")
    container_tag_id = StringField(
        "Container TAG ID",
        validators=[
            DataRequired(),
            ReadOnly(),
            Length(min=10, max=57),
            # Regexp(r"^[0-9A-Fa-f]{2,10}(-[0-9A-Fa-f]{2,10}){4,7}$", message="Invalid RFID format"),
        ],
    )
    short_name = StringField("Short Name", validators=[DataRequired(), Length(1, 100)])
    description = StringField("Description")
    amount = StringField("Amount", validators=[DataRequired()])
    category_tags = StringField("Category/Tags", validators=[DataRequired()])
    images = StringField("Image URLs (comma separated)")
    storage_location = StringField("Storage Location")
    storage_location_tag_id = StringField("Storage Location Tag ID")
    current_location = StringField("Current Location")
    borrowed_by = StringField("Borrowed By")
    cost_per_item = StringField("Cost per Item")
    manufacturer = StringField("Manufacturer")
    model_number = StringField("Model Number")
    upc = StringField("UPC")
    asin = StringField("ASIN")
    serial_number = StringField("Serial Number")
    vendor = StringField("Vendor")
    shop_url = StringField("Shop URL")
    container_size = StringField("Container Size")
    consumable = StringField("Consumable (True/False)", validators=[DataRequired()])
    documentation = StringField("Documentation")


class LoginForm(FlaskForm):
    name = StringField("Insert Reader ID", validators=[DataRequired(), Length(16)])
    submit = SubmitField("Submit")
