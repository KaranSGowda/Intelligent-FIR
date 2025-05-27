from app import app, db
from models import User

with app.app_context():
    print(f'Database connected: {db is not None}')
    print(f'User count: {User.query.count()}')
    
    # List all users
    users = User.query.all()
    print(f'Users: {[user.username for user in users]}')
    
    # Check if tables exist
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print(f'Tables in database: {tables}')
