from website import create_app, db
from website.models import User
from werkzeug.security import generate_password_hash
from .secrets import *

app = create_app()

with app.app_context():
    # Update an existing user to be an admin
    admin_user = User.query.filter_by(email='nlr11@pct.edu').first()
    if admin_user:
        admin_user.is_admin = True
        db.session.commit()
        print("Existing user updated to admin.")
    else:


        # Example usage in your script
        admin_user = User(
            first_name=ADMIN_FIRST_NAME,
            last_name=ADMIN_LAST_NAME,
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=generate_password_hash(ADMIN_PASSWORD, method='pbkdf2:sha256'),  # Hash the password
            is_admin=ADMIN_IS_ADMIN
        )

        db.session.add(admin_user)
        db.session.commit()
        print("New admin user created successfully.")
