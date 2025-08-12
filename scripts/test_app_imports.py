from app import app

with app.app_context():
    try:
        from models import User, FIR, Evidence, Role
        print("✅ Successfully imported models")
    except ImportError as e:
        print(f"❌ Error importing models: {e}")

    try:
        from routes.fir import fir_bp
        print("✅ Successfully imported routes.fir")
    except ImportError as e:
        print(f"❌ Error importing routes.fir: {e}")

    try:
        print("✅ Successfully imported utils.speech_recognition")
    except ImportError as e:
        print(f"❌ Error importing utils.speech_recognition: {e}")
