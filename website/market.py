from flask import Blueprint

market = Blueprint('market', __name__)

items = [
    {'id': 1, 'name': 'Rustic Romance Collection', 'price': 399.99, 'image': 'images/rustic_romance_collection.jpg'},
    {'id': 2, 'name': 'Elegant Enchantment Collection', 'price': 459.99, 'image': 'images/elegant_enhanced_collection.jpg'},
    {'id': 3, 'name': 'Bohemian Bliss Collection', 'price': 429.99, 'image': 'images/bohemeian_bliss_collection.jpg'},
    {'id': 4, 'name': 'Vintage Charm Collection', 'price': 449.99, 'image': 'images/vintage_charm_collection.jpg'},
    {'id': 5, 'name': 'Modern Chic Collection', 'price': 479.99, 'image': 'images/modern_chic_collection.jpg'},
    {'id': 6, 'name': 'Garden Party Collection', 'price': 419.99, 'image': 'images/garden_party_collection.jpg'}
]

def get_items():
    return items
