from . import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    carts = db.relationship('Cart', backref='user', lazy=True)


class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, nullable=False)
    item_name = db.Column(db.String(150), nullable=False)
    item_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date_ordered = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_name = db.Column(db.String(120), nullable=False)
    product_price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)

class CustomWeddingRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    bride_name = db.Column(db.String(150), nullable=False)
    groom_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    bride_address = db.Column(db.String(255), nullable=False)
    groom_address = db.Column(db.String(255), nullable=False)
    bride_phone = db.Column(db.String(20), nullable=False)
    groom_phone = db.Column(db.String(20), nullable=False)
    ceremony_location = db.Column(db.String(255), nullable=False)
    ceremony_date = db.Column(db.Date, nullable=False)
    ceremony_time = db.Column(db.Time, nullable=False)
    reception_location = db.Column(db.String(255), nullable=False)
    reception_date = db.Column(db.Date, nullable=False)
    reception_time = db.Column(db.Time, nullable=False)
    dress_color_style = db.Column(db.String(255), nullable=False)
    bouquets = db.Column(db.Text, nullable=True)
    boutonnieres = db.Column(db.Text, nullable=True)
    parents = db.Column(db.Text, nullable=True)
    corsages = db.Column(db.Text, nullable=True)
    ceremony_decor = db.Column(db.Text, nullable=True)
    reception_decor = db.Column(db.Text, nullable=True)
    date_submitted = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    user = db.relationship('User', backref=db.backref('wedding_requests', lazy=True))
