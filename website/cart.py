from flask import Blueprint, session, redirect, url_for, request, jsonify, make_response
from .marketAddOns import get_addon_items
from .models import db, Cart
from .market import get_items
import json

cart = Blueprint('cart', __name__)

def get_cart_from_cookies():
    cart_cookie = request.cookies.get('cart')
    if cart_cookie:
        cart_items = json.loads(cart_cookie)
        print(f"Retrieved cart from cookies: {cart_items}")  # Debugging line to print retrieved data
        return cart_items
    return []


def save_cart_to_cookies(cart_items):
    response = make_response(jsonify({"message": "Item added to cart"}))  # Change to return a JSON response
    response.set_cookie('cart', json.dumps(cart_items), max_age=30*24*60*60)  # 30 days
    return response


@cart.route('/add-to-cart/<int:item_id>', methods=['POST'])
def add_to_cart(item_id):
    quantity = int(request.form.get('quantity', 1))
    items = get_items() + get_addon_items()
    item = next((item for item in items if item['id'] == item_id), None)
    if item:
        if 'user_id' in session:
            user_id = session['user_id']
            existing_item = Cart.query.filter_by(user_id=user_id, item_id=item_id).first()
            if existing_item:
                existing_item.quantity += quantity
            else:
                new_cart_item = Cart(
                    item_id=item_id,
                    user_id=user_id,
                    item_name=item['name'],
                    item_price=item['price'],
                    quantity=quantity
                )
                db.session.add(new_cart_item)
            try:
                db.session.commit()
                print(f"Item {item['name']} added to user {user_id}'s cart.")
                return jsonify({"message": "Item added to cart"})
            except Exception as e:
                db.session.rollback()
                print(f"Error adding item to cart: {e}")
                return jsonify({"message": "Error adding item to cart"}), 500
        else:
            cart_items = get_cart_from_cookies()
            existing_item = next((i for i in cart_items if i['id'] == item_id), None)
            if existing_item:
                existing_item['quantity'] += quantity
            else:
                item['quantity'] = quantity
                cart_items.append(item)
            response = save_cart_to_cookies(cart_items)
            print(f"Cookies after adding item: {cart_items}")  # Debugging line to print cookie data
            return response
    return jsonify({"message": "Item not found"}), 404


@cart.route('/remove-from-cart/<int:item_id>', methods=['POST'])
def remove_from_cart(item_id):
    if 'user_id' in session:
        user_id = session['user_id']
        Cart.query.filter_by(item_id=item_id, user_id=user_id).delete()
        db.session.commit()
    elif request.cookies.get('cart'):
        cart_items = get_cart_from_cookies()
        cart_items = [item for item in cart_items if item['id'] != item_id]
        response = save_cart_to_cookies(cart_items)
        return response

    return jsonify({"message": "Item removed from cart"})


@cart.route('/update-cart', methods=['POST'])
def update_cart():
    quantities = request.form.to_dict(flat=False)

    if 'user_id' in session:
        user_id = session['user_id']
        for key, quantity_list in quantities.items():
            item_id = key.split('[')[1].split(']')[0]  # Extract item ID from the key
            cart_item = Cart.query.filter_by(user_id=user_id, item_id=item_id).first()
            if cart_item:
                cart_item.quantity = int(quantity_list[0])
                db.session.add(cart_item)
        try:
            db.session.commit()
            return jsonify({"message": "Cart updated"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Error updating cart"}), 500
    else:
        cart_items = get_cart_from_cookies()
        for key, quantity_list in quantities.items():
            item_id = key.split('[')[1].split(']')[0]  # Extract item ID from the key
            for item in cart_items:
                if item['id'] == int(item_id):
                    item['quantity'] = int(quantity_list[0])
        response = save_cart_to_cookies(cart_items)
        return jsonify({"message": "Cart updated"})

    return jsonify({"message": "Error updating cart"}), 500


