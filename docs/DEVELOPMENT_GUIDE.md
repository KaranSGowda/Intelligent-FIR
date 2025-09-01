# 🛠️ Development Guide - Intelligent FIR System

## 📋 Table of Contents
1. [Development Setup](#development-setup)
2. [Project Architecture](#project-architecture)
3. [Code Organization](#code-organization)
4. [Development Workflow](#development-workflow)
5. [Testing Guidelines](#testing-guidelines)
6. [Debugging Tips](#debugging-tips)
7. [Performance Optimization](#performance-optimization)

## 🚀 Development Setup

### Prerequisites
```bash
# Required
Python 3.8+
SQLite 3
FFmpeg

# Optional (for enhanced features)
OpenAI API Key
Google Cloud Speech API credentials
```

### Environment Setup
```bash
# 1. Clone and navigate
git clone <repository-url>
cd Intelligent-FIR

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# 5. Initialize database
python scripts/setup_db.py

# 6. Run development server
python app.py
```

## 🏗️ Project Architecture

### MVC Pattern
```
📁 Models (models.py, models/)
├── User, FIR, Evidence, LegalSection
└── Database relationships and validations

📁 Views (templates/)
├── HTML templates with Jinja2
└── Responsive Bootstrap UI

📁 Controllers (routes/)
├── Request handling and business logic
└── API endpoints and form processing
```

### Key Components

#### 🔐 Authentication System
- **File**: `routes/auth.py`
- **Features**: Login, registration, role-based access
- **Models**: User with roles (public, police, admin)

#### 📄 FIR Management
- **File**: `routes/fir.py`
- **Features**: CRUD operations, status tracking, PDF generation
- **Models**: FIR with complainant and officer relationships

#### 🔍 Evidence System
- **File**: `routes/evidence.py`
- **Features**: File upload, analysis, chain of custody
- **Models**: Evidence with metadata and analysis results

#### 🧠 AI/ML Features
- **Files**: `utils/ml_analyzer.py`, `utils/openai_helper.py`
- **Features**: Legal section mapping, text analysis
- **Models**: Trained classifiers and vectorizers

## 📁 Code Organization

### Directory Structure
```
📁 routes/           # Flask blueprints
├── auth.py         # Authentication routes
├── fir.py          # FIR management
├── evidence.py     # Evidence handling
├── admin.py        # Admin panel
└── ...

📁 utils/           # Business logic
├── ml_analyzer.py  # Machine learning
├── pdf_generator.py # PDF creation
├── speech_recognition.py # Voice processing
└── ...

📁 templates/       # Jinja2 templates
├── layout.html     # Base template
├── fir/           # FIR templates
├── evidence/      # Evidence templates
└── ...

📁 static/         # Static assets
├── css/           # Stylesheets
├── js/            # JavaScript
├── uploads/       # User uploads
└── pdfs/          # Generated PDFs
```

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions**: `snake_case()`
- **Variables**: `snake_case`
- **Constants**: `UPPER_CASE`
- **Templates**: `snake_case.html`

## 🔄 Development Workflow

### 1. Feature Development
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes
# - Add routes in routes/
# - Add utilities in utils/
# - Add templates in templates/
# - Update models if needed

# Test changes
python scripts/test_app.py
python app.py  # Manual testing

# Commit and push
git add .
git commit -m "Add new feature: description"
git push origin feature/new-feature
```

### 2. Database Changes
```bash
# Backup current database
python scripts/backup_db.py

# Make model changes in models.py
# Update setup_db.py if needed

# Apply changes
python scripts/setup_db.py

# Verify changes
python scripts/verify_db.py
```

### 3. Adding New Routes
```python
# In routes/new_module.py
from flask import Blueprint, render_template, request
from flask_login import login_required

new_bp = Blueprint('new_module', __name__, url_prefix='/new')

@new_bp.route('/')
@login_required
def index():
    return render_template('new_module/index.html')

# In app.py
from routes.new_module import new_bp
app.register_blueprint(new_bp)
```

### 4. Adding Utilities
```python
# In utils/new_utility.py
import logging

logger = logging.getLogger(__name__)

def new_function(param):
    """
    Description of function
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    try:
        # Implementation
        return result
    except Exception as e:
        logger.error(f"Error in new_function: {str(e)}")
        raise
```

## 🧪 Testing Guidelines

### Unit Tests
```python
# In tests/test_new_feature.py
import unittest
from app import create_app
from models import db

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
    
    def test_new_feature(self):
        response = self.client.get('/new-endpoint')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
```

### Integration Tests
```python
# Test complete workflows
def test_fir_creation_workflow(self):
    # 1. Login
    # 2. Create FIR
    # 3. Add evidence
    # 4. Generate PDF
    # 5. Verify all steps
    pass
```

### Manual Testing Checklist
- [ ] User registration and login
- [ ] FIR creation and editing
- [ ] Evidence upload and viewing
- [ ] PDF generation
- [ ] Voice transcription
- [ ] Admin panel access
- [ ] Error handling
- [ ] Mobile responsiveness

## 🐛 Debugging Tips

### Logging
```python
import logging
logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical error")
```

### Common Issues

#### Database Errors
```python
# Check database connection
python scripts/check_db.py

# Verify schema
python scripts/verify_db.py

# Reset database
python scripts/setup_db.py
```

#### File Upload Issues
```python
# Check file permissions
# Verify upload directory exists
# Check file size limits
# Validate file types
```

#### PDF Generation Problems
```python
# Check reportlab installation
pip install reportlab

# Verify template rendering
# Check file paths
# Test with simple content first
```

### Debug Mode
```python
# In app.py
app.run(debug=True)

# Or set environment variable
export FLASK_ENV=development
export FLASK_DEBUG=1
```

## ⚡ Performance Optimization

### Database Optimization
```python
# Use database indexes
# Optimize queries
# Implement pagination
# Use connection pooling
```

### File Handling
```python
# Implement file compression
# Use appropriate file formats
# Implement file cleanup
# Cache frequently accessed files
```

### Frontend Optimization
```html
<!-- Minify CSS/JS -->
<!-- Optimize images -->
<!-- Use CDN for libraries -->
<!-- Implement lazy loading -->
```

### Caching
```python
# Implement Redis caching
# Cache ML model predictions
# Cache PDF generation
# Cache database queries
```

## 📝 Code Style Guidelines

### Python (PEP 8)
```python
# Line length: 88 characters
# Use type hints
# Document functions
# Handle exceptions properly
# Use meaningful variable names
```

### HTML/CSS
```html
<!-- Use semantic HTML -->
<!-- Follow Bootstrap conventions -->
<!-- Maintain consistent indentation -->
<!-- Use meaningful class names -->
```

### JavaScript
```javascript
// Use modern ES6+ syntax
// Follow consistent naming
// Add comments for complex logic
// Handle errors gracefully
```

## 🔧 Development Tools

### Recommended IDE Extensions
- Python extension
- Flask snippets
- Jinja2 syntax highlighting
- SQLite viewer
- Git integration

### Useful Commands
```bash
# Format code
black *.py

# Check code quality
flake8 *.py

# Type checking
mypy *.py

# Security check
bandit -r .
```

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [Python Best Practices](https://docs.python-guide.org/)

---

**Happy coding! 🚀**
