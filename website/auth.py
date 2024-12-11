from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, CustomWeddingRequest
from . import db
from .secureChecker import sanitize, validate_name, validate_username, validate_password, validate_email, email_exists, username_exists

auth = Blueprint('auth', __name__)

@auth.route('/account')
def account():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to log in if not logged in
    user = User.query.get(session['user_id'])
    has_custom_wedding_request = CustomWeddingRequest.query.filter_by(user_id=user.id).first() is not None
    return render_template('account.html', user=user, has_custom_wedding_request=has_custom_wedding_request)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = sanitize(request.form.get('username'))
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['cart'] = session.get('cart', [])  # Initialize cart in session
            session['logged_in'] = True
            flash('Login successful!', category='success')
            return redirect(url_for('views.home'))
        else:
            error = 'User does not exist or incorrect password.'

    return render_template("login.html", error=error)

@auth.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('cart', None)  # Clear the cart on logout
    session.pop('logged_in', None)
    flash('Logged out successfully.', category='success')
    return redirect(url_for('views.home'))

@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        first_name = sanitize(request.form.get('first_name'))
        last_name = sanitize(request.form.get('last_name'))
        username = sanitize(request.form.get('username'))
        email = sanitize(request.form.get('email'))
        password = request.form.get('password')

        try:
            # Check for harmful keywords
            if any(keyword in first_name for keyword in ['SELECT', 'DROP', 'DELETE']) or \
                    any(keyword in last_name for keyword in ['SELECT', 'DROP', 'DELETE']) or \
                    any(keyword in username for keyword in ['SELECT', 'DROP', 'DELETE']) or \
                    any(keyword in password for keyword in ['SELECT', 'DROP', 'DELETE']) or \
                    any(keyword in email for keyword in ['SELECT', 'DROP', 'DELETE']):
                raise ValueError("Input contained harmful keywords!")

            # Validate other inputs
            if not validate_name(first_name):
                raise ValueError("Invalid First Name!")
            if not validate_name(last_name):
                raise ValueError("Invalid Last Name!")
            if not validate_username(username):
                raise ValueError("Invalid Username!")
            if not validate_password(password):
                raise ValueError("Invalid Password!")
            if not validate_email(email):
                raise ValueError("Invalid email format!")

            # Check if the credential already exist
            if email_exists(email):
                raise ValueError("Email address already exists!")
            if username_exists(username):
                raise ValueError("Username already exists!")

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=generate_password_hash(password, method='pbkdf2:sha256')
            )
            db.session.add(new_user)
            db.session.commit()

            # Log in the user immediately after registration
            session['user_id'] = new_user.id
            session['cart'] = session.get('cart', [])
            session['logged_in'] = True

            flash('Registration successful! You are now logged in.', category='success')
            return redirect(url_for('views.home'))

        except ValueError as e:
            flash(str(e), category='error')

    return render_template('sign_up.html')
