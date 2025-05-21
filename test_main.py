import time
import sys

print("Starting import...")
start_time = time.time()

try:
    from app import app
    import_time = time.time() - start_time
    print(f"Import completed in {import_time:.2f} seconds")
    
    # Test routes
    print("\nApp routes:")
    print(app.url_map)
    
    # Test database connection
    print("\nTesting database connection...")
    from models import User
    with app.app_context():
        users = User.query.limit(1).all()
        print(f"Database connection successful. Found {len(users)} user(s).")
    
    print("\nAll tests passed!")
    
except Exception as e:
    import_time = time.time() - start_time
    print(f"Import failed after {import_time:.2f} seconds")
    print(f"Error: {str(e)}")
    import traceback
    traceback.print_exc()
    sys.exit(1)