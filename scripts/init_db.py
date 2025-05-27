from app import create_app, db
from models import User, Role

def init_database():
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
                {
                    'username': 'user',
                    'password': 'password',
                    'email': 'user@example.com',
                    'full_name': 'Demo User',
                    'role': Role.PUBLIC
                },
                {
                    'username': 'police',
                    'password': 'password',
                    'email': 'police@example.com',
                    'full_name': 'Police Officer',
                    'role': Role.POLICE
                },
                {
                    'username': 'admin',
                    'password': 'password',
                    'email': 'admin@example.com',
                    'full_name': 'System Admin',
                    'role': Role.ADMIN
                }
            ]

            for user_data in demo_users:
                user = User(
                    username=user_data['username'],
                    email=user_data['email'],
                    full_name=user_data['full_name'],
                    role=user_data['role']
                )
                user.set_password(user_data['password'])
                db.session.add(user)

            db.session.commit()
            print("Demo users created successfully!")
        else:
            print("Demo users already exist, skipping creation.")

if __name__ == "__main__":
    init_database()
