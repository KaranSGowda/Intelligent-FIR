try:
    from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
    print("✅ Successfully imported Flask modules")
except ImportError as e:
    print(f"❌ Error importing Flask: {e}")

try:
    from flask_login import login_required, current_user
    print("✅ Successfully imported Flask-Login modules")
except ImportError as e:
    print(f"❌ Error importing Flask-Login: {e}")

try:
    from werkzeug.utils import secure_filename
    print("✅ Successfully imported Werkzeug modules")
except ImportError as e:
    print(f"❌ Error importing Werkzeug: {e}")

try:
    from models import FIR, Evidence, User, Role
    print("✅ Successfully imported models")
except ImportError as e:
    print(f"❌ Error importing models: {e}")

try:
    from routes.fir import fir_bp
    print("✅ Successfully imported routes.fir")
except ImportError as e:
    print(f"❌ Error importing routes.fir: {e}")

try:
    from utils.speech_recognition import SpeechToText
    print("✅ Successfully imported utils.speech_recognition")
except ImportError as e:
    print(f"❌ Error importing utils.speech_recognition: {e}")
