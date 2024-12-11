from flask import Blueprint

marketAddOns = Blueprint('marketAddOns', __name__)

def get_addon_items():
    return [
        {'id': 7, 'name': 'Bridal Bouquet', 'price': 59.99, 'image': 'images/bridal_banquet.jpg'},
        {'id': 8, 'name': 'Floral Centerpiece', 'price': 45.99, 'image': 'images/floral_centerpiece.jpg'},
        {'id': 9, 'name': 'Corsage', 'price': 15.99, 'image': 'images/corsage_two.jpg'},
        {'id': 10, 'name': 'Hanging Floral Installation', 'price': 89.99, 'image': 'images/hanging_floral_installation_two.jpg'},
        {'id': 11, 'name': 'Aisle Runner Flowers', 'price': 29.99, 'image': 'images/aisle_runner_flowers.jpg'},
        {'id': 12, 'name': 'Flower Petal Confetti', 'price': 9.99, 'image': 'images/flower_petal_confetti.jpg'}


    ]