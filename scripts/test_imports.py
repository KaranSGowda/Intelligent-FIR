try:
    import flask
    print("Flask is installed")
except ImportError:
    print("Flask is not installed")

try:
    import flask_cors
    print("Flask-CORS is installed")
except ImportError:
    print("Flask-CORS is not installed")

try:
    import flask_sqlalchemy
    print("Flask-SQLAlchemy is installed")
except ImportError:
    print("Flask-SQLAlchemy is not installed")

try:
    import flask_login
    print("Flask-Login is installed")
except ImportError:
    print("Flask-Login is not installed")

print("Python path:")
import sys
print(sys.path)
