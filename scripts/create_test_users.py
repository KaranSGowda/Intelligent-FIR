
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app, db
from models import User, Role

with app.app_context():
    # Test users to add
    test_users = [
        dict(username='admin_test', email='admin@test.com', full_name='Admin Test', password='admin123', role=Role.ADMIN),
        dict(username='police_test', email='police@test.com', full_name='Police Test', password='police123', role=Role.POLICE),
        dict(username='public_test', email='public@test.com', full_name='Public Test', password='public123', role=Role.PUBLIC),
    ]

    for user_data in test_users:
        user = User.query.filter_by(username=user_data['username']).first()
        if not user:
            user = User()
            user.username = user_data['username']
            user.email = user_data['email']
            user.full_name = user_data['full_name']
            user.role = user_data['role']
            user.set_password(user_data['password'])
            db.session.add(user)
            print(f"[DEBUG] Added test user: {user.username} ({user.role})")
        else:
            print(f"[DEBUG] Test user already exists: {user.username}")
    db.session.commit()
    print("[DEBUG] Test users created/verified.")
