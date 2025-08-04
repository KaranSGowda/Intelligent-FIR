import os
from app import app
from extensions import db
from models import User, Role

def create_admin():
    with app.app_context():
        username = 'admin'
        password = 'admin123'
        email = 'admin@example.com'
        full_name = 'Test Admin'
        # Check if user already exists
        user = User.query.filter_by(username=username).first()
        if user:
            print(f"User '{username}' already exists.")
            return
        user = User()
        user.username = username
        user.email = email
        user.full_name = full_name
        user.role = Role.ADMIN
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        print(f"Admin user '{username}' created with password '{password}'")

if __name__ == '__main__':
    create_admin()
