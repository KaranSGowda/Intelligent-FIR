import sys
print(f"Python version: {sys.version}")

# Test Flask
try:
    import flask
    print(f"✅ Flask version: {flask.__version__}")
except ImportError as e:
    print(f"❌ Error importing Flask: {e}")

# Test Flask-Login
try:
    import flask_login
    print(f"✅ Flask-Login version: {flask_login.__version__}")
except ImportError as e:
    print(f"❌ Error importing Flask-Login: {e}")

# Test Werkzeug
try:
    import werkzeug
    from werkzeug.utils import secure_filename
    import importlib.metadata
    werkzeug_version = importlib.metadata.version("werkzeug")
    print(f"✅ Werkzeug version: {werkzeug_version}")
    test_filename = "my file with spaces & special chars.txt"
    secure_name = secure_filename(test_filename)
    print(f"  Secure filename test: {test_filename} -> {secure_name}")
except ImportError as e:
    print(f"❌ Error importing Werkzeug: {e}")
except Exception as e:
    print(f"❌ Error with Werkzeug: {e}")

# Test SQLAlchemy
try:
    import sqlalchemy
    print(f"✅ SQLAlchemy version: {sqlalchemy.__version__}")
except ImportError as e:
    print(f"❌ Error importing SQLAlchemy: {e}")

# Test NLTK
try:
    import nltk
    print(f"✅ NLTK version: {nltk.__version__}")
    # Test NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
        print("  NLTK punkt data is available")
    except LookupError:
        print("  ❌ NLTK punkt data is not available")
except ImportError as e:
    print(f"❌ Error importing NLTK: {e}")

# Test SpeechRecognition
try:
    import speech_recognition as sr
    print(f"✅ SpeechRecognition version: {sr.__version__}")
except ImportError as e:
    print(f"❌ Error importing SpeechRecognition: {e}")

# Test scikit-learn
try:
    import sklearn
    print(f"✅ scikit-learn version: {sklearn.__version__}")
except ImportError as e:
    print(f"❌ Error importing scikit-learn: {e}")

# Test pandas
try:
    import pandas
    print(f"✅ pandas version: {pandas.__version__}")
except ImportError as e:
    print(f"❌ Error importing pandas: {e}")

# Test OpenAI
try:
    import openai
    print(f"✅ OpenAI version: {openai.__version__}")
except ImportError as e:
    print(f"❌ Error importing OpenAI: {e}")

print("\nAll import tests completed.")
