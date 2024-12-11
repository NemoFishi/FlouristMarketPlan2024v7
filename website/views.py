from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from .models import User, Cart, Order, OrderItem, CustomWeddingRequest
from .market import get_items
from .marketAddOns import get_addon_items
from .cart import get_cart_from_cookies, save_cart_to_cookies
from . import db, mail, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_ID_FULL
from datetime import datetime
import pytz
from flask_mail import Message
from .helpers import get_admin_emails
from .secureChecker import sanitize

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return render_template('home.html', show_toast=session.pop('logged_in', False))

@views.route('/market')
def market_page():
    items = get_items()
    return render_template('market.html', items=items)

@views.route('/marketAddOns')
def market_addons_page():
    addon_items = get_addon_items()
    return render_template('marketAddOns.html', addon_items=addon_items)


@views.route('/cart')
def cart_page():
    if 'user_id' in session:
        user_id = session['user_id']
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_price = sum(item.item_price * item.quantity for item in cart_items)
    else:
        cart_items = get_cart_from_cookies()
        total_price = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)

    if not cart_items:
        total_price = 0

    print(f"Cart items: {cart_items}")  # Debugging line
    print(f"Total price: {total_price}")  # Debugging line
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@views.route('/checkout', methods=['GET'])
def checkout_page():
    if 'user_id' in session:
        user_id = session['user_id']
        cart_items = Cart.query.filter_by(user_id=user_id).all()
        total_price = sum(item.item_price * item.quantity for item in cart_items)
    else:
        cart_items = get_cart_from_cookies()
        total_price = sum(item.get('price', 0) * item.get('quantity', 0) for item in cart_items)

    return render_template('checkout.html', cart_items=cart_items, total_price=total_price, paypal_client_id=PAYPAL_CLIENT_ID_FULL)

@views.route('/process-checkout', methods=['POST'])
def process_checkout():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    total_amount = request.form.get('total_amount')
    time_zone = request.form.get('time_zone')

    # Spy on persons time zone
    user_time_zone = pytz.timezone(time_zone)
    date_ordered = datetime.now(user_time_zone)

    cart_items = Cart.query.filter_by(user_id=user_id).all()
    order = Order(user_id=user_id, total_amount=total_amount, date_ordered=date_ordered)
    db.session.add(order)
    db.session.flush()  # Get the order ID for order items

    for item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            product_name=item.item_name,
            product_price=item.item_price,
            quantity=item.quantity,
            total_price=item.item_price * item.quantity
        )
        db.session.add(order_item)

    # cart go away after buy
    Cart.query.filter_by(user_id=user_id).delete()
    db.session.commit()

    # Confirm whatever I bought
    return redirect(url_for('views.order_confirmation'))

@views.route('/order-confirmation', methods=['GET'])
def order_confirmation():
    return render_template('order_confirmation.html')

@views.route('/order-history', methods=['GET'])
def order_history():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.date_ordered.desc()).all()

    return render_template('order_history.html', orders=orders)

@views.route('/wedding-form')
def wedding_form():
    return render_template('customWeddings.html')

@views.route('/submit-wedding-form', methods=['POST'])
def submit_wedding_form():
    bride_name = sanitize(request.form['brideName'])
    groom_name = sanitize(request.form['groomName'])
    email = sanitize(request.form['email'])
    bride_address = sanitize(request.form['brideAddress'])
    groom_address = sanitize(request.form['groomAddress'])
    bride_phone = sanitize(request.form['bridePhone'])
    groom_phone = sanitize(request.form['groomPhone'])
    ceremony_location = sanitize(request.form['ceremonyLocation'])
    ceremony_date = datetime.strptime((request.form['ceremonyDate']), '%Y-%m-%d').date()
    ceremony_time = datetime.strptime((request.form['ceremonyTime']), '%H:%M').time()
    reception_location = sanitize(request.form['receptionLocation'])
    reception_date = datetime.strptime((request.form['receptionDate']), '%Y-%m-%d').date()
    reception_time = datetime.strptime((request.form['receptionTime']), '%H:%M').time()
    dress_color_style = sanitize(request.form['dressColorStyle'])
    bouquets = sanitize(request.form.get('bouquets'))
    boutonnieres = sanitize(request.form.get('boutonnieres'))
    parents = sanitize(request.form.get('parents'))
    corsages = sanitize(request.form.get('corsages'))
    ceremony_decor = sanitize(request.form.get('ceremonyDecor'))
    reception_decor = sanitize(request.form.get('receptionDecor'))

    if 'user_id' in session:
        user_id = session['user_id']
    else:
        user_id = None

    new_request = CustomWeddingRequest(
        bride_name=bride_name, groom_name=groom_name, email=email, bride_address=bride_address, groom_address=groom_address,
        bride_phone=bride_phone, groom_phone=groom_phone, ceremony_location=ceremony_location,
        ceremony_date=ceremony_date, ceremony_time=ceremony_time, reception_location=reception_location,
        reception_date=reception_date, reception_time=reception_time, dress_color_style=dress_color_style,
        bouquets=bouquets, boutonnieres=boutonnieres, parents=parents, corsages=corsages,
        ceremony_decor=ceremony_decor, reception_decor=reception_decor, user_id=user_id
    )
    db.session.add(new_request)
    db.session.commit()

    try:
        msg = Message('New Wedding Request', sender='nikolisr@icloud.com', recipients=[email])
        msg.body = f'''Dear {bride_name} {groom_name},

Thank you for your custom wedding request. Here are the details you provided:

Bride: {bride_name}
Groom: {groom_name}
Bride Address: {bride_address}
Groom Address: {groom_address}
Bride Phone: {bride_phone}
Groom Phone: {groom_phone}
Ceremony Location: {ceremony_location}
Ceremony Date: {ceremony_date}
Ceremony Time: {ceremony_time}
Reception Location: {reception_location}
Reception Date: {reception_date}
Reception Time: {reception_time}
Dress Color and Style: {dress_color_style}

Wedding Party:
Bouquets: {bouquets}
Boutonnieres: {boutonnieres}
Parents: {parents}
Corsages: {corsages}

Ceremony Decorations:
{ceremony_decor}

Reception Decorations:
{reception_decor}

We will get back to you soon to discuss further details.

Best regards,
Your Company Name
'''
        mail.send(msg)
        print("Email sent successfully to the user")
    except Exception as e:
        print(f"Failed to send email to the user: {e}")
        flash('Failed to send confirmation email. Please try again later.', 'danger')

    # Get all admin emails
    admin_emails = get_admin_emails()

    try:
        admin_msg = Message('New Custom Wedding Request', sender='nikolisr@icloud.com', recipients=admin_emails)
        admin_msg.html = f'''<h1>New Custom Wedding Request</h1>
        <p><strong>Bride:</strong> {bride_name}</p>
        <p><strong>Groom:</strong> {groom_name}</p>
        <p><strong>Ceremony Date:</strong> {ceremony_date}</p>
        <p><strong>Reception Date:</strong> {reception_date}</p>
        <p><strong>Email:</strong> {email}</p>
        <a href="{url_for('views.admin_dashboard', _external=True)}" style="display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-align: center; text-decoration: none; border-radius: 5px;">Open Admin Dashboard</a>'''
        mail.send(admin_msg)
        print("Notification email sent successfully to the admin")
    except Exception as e:
        print(f"Failed to send notification email to the admin: {e}")

    flash('Wedding request submitted successfully!', 'success')
    return render_template('form_submitted.html', first_name=bride_name, last_name=groom_name)


@views.route('/custom-wedding')
def custom_wedding():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to log in if not logged in
    user = User.query.get(session['user_id'])
    custom_wedding_request = CustomWeddingRequest.query.filter_by(user_id=user.id).first()
    if not custom_wedding_request:
        flash('No custom wedding details found!', category='error')
        return redirect(url_for('auth.account'))

    return render_template('my_custom_wedding.html',
                           brideName=custom_wedding_request.bride_name,
                           groomName=custom_wedding_request.groom_name,
                           email=custom_wedding_request.email,
                           brideAddress=custom_wedding_request.bride_address,
                           groomAddress=custom_wedding_request.groom_address,
                           bridePhone=custom_wedding_request.bride_phone,
                           groomPhone=custom_wedding_request.groom_phone,
                           ceremonyLocation=custom_wedding_request.ceremony_location,
                           ceremonyDate=custom_wedding_request.ceremony_date,
                           ceremonyTime=custom_wedding_request.ceremony_time,
                           receptionLocation=custom_wedding_request.reception_location,
                           receptionDate=custom_wedding_request.reception_date,
                           receptionTime=custom_wedding_request.reception_time,
                           dressColorStyle=custom_wedding_request.dress_color_style,
                           bouquets=custom_wedding_request.bouquets,
                           boutonnieres=custom_wedding_request.boutonnieres,
                           parents=custom_wedding_request.parents,
                           corsages=custom_wedding_request.corsages,
                           ceremonyDecor=custom_wedding_request.ceremony_decor,
                           receptionDecor=custom_wedding_request.reception_decor)



# Admin Dashboard Route
@views.route('/admin')
def admin_dashboard():
    all_orders = Order.query.order_by(Order.date_ordered.desc()).all()
    all_order_details = []

    for all_order in all_orders:
        user = User.query.get(all_order.user_id)
        all_order_items = OrderItem.query.filter_by(order_id=all_order.id).all()
        item_list = [{'product_name': item.product_name, 'product_price': item.product_price, 'quantity': item.quantity, 'total_price': item.total_price} for item in all_order_items]
        all_order_details.append({
            'id': all_order.id,
            'customer_name': f"{user.first_name} {user.last_name}",
            'date_ordered': all_order.date_ordered,
            'total_amount': all_order.total_amount,
            'order_items': item_list
        })

    wedding_requests = CustomWeddingRequest.query.order_by(CustomWeddingRequest.date_submitted.desc()).all()

    return render_template('admin.html', all_orders=all_order_details, wedding_requests=wedding_requests)


