from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from .secrets import *

db = SQLAlchemy()
mail = Mail()


def create_app():

    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

    # Email configuration
    app.config['MAIL_SERVER'] = 'smtp.mail.me.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = MAIL_USERNAME
    app.config['MAIL_PASSWORD'] = MAIL_PASSWORD


    db.init_app(app)
    mail.init_app(app)

    from .views import views
    from .auth import auth
    from .models import User
    from .market import market
    from .marketAddOns import marketAddOns
    from .cart import cart

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(market, url_prefix="/")
    app.register_blueprint(cart, url_prefix="/")
    app.register_blueprint(marketAddOns, url_prefix="/")

    @app.context_processor
    def inject_user():
        user = None
        if 'user_id' in session:
            user = User.query.get(session['user_id'])
        return dict(user=user)

    with app.app_context():
        db.create_all()

    return app
