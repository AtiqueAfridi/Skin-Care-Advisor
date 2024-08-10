from app import app
from models import db, User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create a new user
    new_user = User(username="testuser", password=generate_password_hash("testpassword"))
    
    # Add and commit to the database
    db.session.add(new_user)
    db.session.commit()

    print("User added successfully.")
