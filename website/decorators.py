from functools import wraps
from flask import session, redirect, url_for
from .models import User

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            return redirect(url_for('views.home'))
        return f(*args, **kwargs)
    return decorated_function
