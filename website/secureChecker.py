import re
from .models import User

def sanitize(myInput):
    # Sanitize the input to prevent SQL injection
    # Whitelist approach: Allow only alphanumeric characters, underscore, space, @, and .
    sanitized_input = re.sub(r'[^a-zA-Z0-9_ @.]', '', myInput)

    # Check if any harmful keywords were removed
    removed_keywords = re.findall(r'\b(?:SELECT|DROP|DELETE)\b', myInput)
    if removed_keywords:
        removed_keywords_str = ', '.join(removed_keywords)
        print(f"Removed harmful keywords: {removed_keywords_str}")

    return sanitized_input

def validate_name(name):
    # Allow alphanumeric characters, 3-15 characters long
    pattern = r'^[a-zA-Z0-9_]{3,15}$'
    return re.match(pattern, name)

def validate_username(username):
    # Allowing alphanumeric characters and underscore, 4-20 characters long
    pattern = r'^[a-zA-Z0-9_]{4,20}$'
    return re.match(pattern, username)

def validate_password(password):
    # Requiring at least 8 characters with one lowercase, one uppercase, one digit
    pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,20}$'
    return re.match(pattern, password)

def validate_email(email):
    # Standard email pattern for validation
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

def email_exists(email):
    """Check if the email already exists in the database."""
    user = User.query.filter_by(email=email).first()
    return user is not None

def username_exists(username):
    """Check if the username already exists in the database."""
    user = User.query.filter_by(username=username).first()
    return user is not None
