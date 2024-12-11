from .models import User

def get_admin_emails():
    admin_emails = [user.email for user in User.query.filter_by(is_admin=True).all()]
    return admin_emails