from app import create_app, db
from models import User, Role
import os

def create_demo_users():
    print("Creating application...")
    app = create_app()

    print("Initializing database...")
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created successfully!")

        # Check if users already exist
        if User.query.filter_by(username='user').first() is None:
            print("Creating demo users...")

            # Create demo users
            demo_users = [
                User(
                    username='user',
                    email='user@example.com',
                    full_name='Demo User',
                    role=Role.PUBLIC,
                    phone='1234567890',
                    address='123 Main St'
                ),
                User(
                    username='police',
                    email='police@example.com',
                    full_name='Police Officer',
                    role=Role.POLICE,
                    phone='9876543210',
                    address='Police Station'
                ),
                User(
                    username='admin',
                    email='admin@example.com',
                    full_name='System Admin',
                    role=Role.ADMIN,
                    phone='5555555555',
                    address='Admin Office'
                )
            ]

            # Set passwords and add to session
            for user in demo_users:
                user.set_password('password')
                db.session.add(user)

            db.session.commit()
            print("Demo users created successfully!")
        else:
            print("Demo users already exist, skipping creation.")

if __name__ == "__main__":
    create_demo_users()
