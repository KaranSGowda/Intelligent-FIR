"""
Basic tests for the Intelligent FIR System
"""
import pytest
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_import_app():
    """Test that the main app can be imported"""
    try:
        from app import create_app
        assert create_app is not None
    except ImportError as e:
        pytest.fail(f"Failed to import create_app: {e}")

def test_import_extensions():
    """Test that extensions can be imported"""
    try:
        from extensions import db, login_manager
        assert db is not None
        assert login_manager is not None
    except ImportError as e:
        pytest.fail(f"Failed to import extensions: {e}")

def test_import_models():
    """Test that models can be imported"""
    try:
        import models
        assert models is not None
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")

def test_import_routes():
    """Test that routes can be imported"""
    try:
        from routes import auth, fir, admin, chatbot
        assert auth is not None
        assert fir is not None
        assert admin is not None
        assert chatbot is not None
    except ImportError as e:
        pytest.fail(f"Failed to import routes: {e}")

def test_import_utils():
    """Test that utility modules can be imported"""
    try:
        from utils import ml_analyzer, pdf_generator, speech_recognition
        assert ml_analyzer is not None
        assert pdf_generator is not None
        assert speech_recognition is not None
    except ImportError as e:
        pytest.fail(f"Failed to import utils: {e}")

def test_app_creation():
    """Test that the Flask app can be created"""
    try:
        from app import create_app
        app = create_app()
        assert app is not None
        assert hasattr(app, 'config')
    except Exception as e:
        pytest.fail(f"Failed to create app: {e}")

def test_requirements_file():
    """Test that requirements.txt exists and is readable"""
    requirements_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'requirements.txt')
    assert os.path.exists(requirements_path), "requirements.txt file not found"
    
    with open(requirements_path, 'r') as f:
        content = f.read()
        assert len(content) > 0, "requirements.txt is empty"

def test_pyproject_toml():
    """Test that pyproject.toml exists and has correct project name"""
    pyproject_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyproject.toml')
    assert os.path.exists(pyproject_path), "pyproject.toml file not found"
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
        assert 'intelligent-fir-system' in content, "Project name not found in pyproject.toml"

if __name__ == '__main__':
    pytest.main([__file__]) 