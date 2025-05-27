# Intelligent FIR System - Project Structure

## 📁 Current Project Organization

### 🏗️ Core Application Files
```
📁 Intelligent-FIR/
├── 🚀 app.py                    # Main Flask application entry point
├── 🔧 extensions.py             # Flask extensions configuration
├── 📊 models.py                 # Database models (simple version)
├── ⚙️ requirements.txt          # Python dependencies
├── 📋 pyproject.toml            # Project configuration
└── 🔒 .env                      # Environment variables (create from .env.example)
```

### 🗂️ Application Modules
```
📁 routes/                       # Flask route handlers
├── 🔐 auth.py                   # Authentication routes
├── 📄 fir.py                    # FIR management routes
├── 🔍 evidence.py               # Evidence management routes
├── ⚖️ legal_sections.py         # Legal sections routes
├── 👤 admin.py                  # Admin panel routes
├── 🤖 chatbot.py                # AI chatbot routes
├── 🎤 speech_recognition.py     # Voice transcription routes
├── ✅ verification.py           # Document verification routes
├── 🛠️ debug.py                  # Debug utilities
└── ⚙️ user_settings.py          # User preferences routes

📁 models/                       # Enhanced database models
├── 📊 __init__.py               # Extended models with full features
└── 📄 fir.py                    # FIR model definitions

📁 utils/                        # Utility functions
├── 🤖 chatbot.py                # AI chatbot logic
├── ☁️ cloud_speech.py           # Google Cloud Speech API
├── 🔍 evidence_analyzer.py      # Evidence analysis tools
├── 🌐 language_utils.py         # Multi-language support
├── ⚖️ legal_mapper.py           # Legal section mapping
├── 🧠 ml_analyzer.py            # Machine learning classifier
├── 🤖 openai_helper.py          # OpenAI API integration
├── 📄 pdf_generator.py          # PDF document generation
├── 📱 qr_generator.py           # QR code generation
├── 🎤 speech_recognition.py     # Speech processing
└── 📚 training_data.py          # ML training data
```

### 🎨 Frontend & Templates
```
📁 templates/                    # Jinja2 HTML templates
├── 📄 layout.html               # Base template
├── 🏠 index.html                # Homepage
├── 🔐 login.html                # Login page
├── 📝 register.html             # Registration page
├── 📁 fir/                      # FIR-related templates
│   ├── 📊 dashboard.html        # FIR dashboard
│   ├── ➕ new.html              # Create new FIR
│   └── 👁️ view.html             # View FIR details
├── 📁 evidence/                 # Evidence templates
│   ├── 📋 manage.html           # Evidence management
│   ├── 👁️ view.html             # View evidence
│   └── ✏️ edit.html             # Edit evidence
├── 📁 admin/                    # Admin templates
├── 📁 legal_sections/           # Legal section templates
└── 📁 verification/             # Verification templates

📁 static/                       # Static assets
├── 📁 css/                      # Stylesheets
├── 📁 js/                       # JavaScript files
├── 📁 images/                   # Static images
├── 📁 uploads/                  # User uploaded files
│   ├── 📁 evidence/             # Evidence files
│   ├── 📁 audio/                # Audio recordings
│   └── 📁 images/               # Image uploads
└── 📁 pdfs/                     # Generated PDF documents
```

### 🗄️ Database & Storage
```
📁 instance/                     # Flask instance folder
└── 🗄️ fir_system.db            # SQLite database

📁 utils/ml_models/              # Machine learning models
├── 🧠 ipc_classifier.pkl       # Trained classifier
├── 📊 tfidf_vectorizer.pkl     # Text vectorizer
└── 🏷️ multilabel_binarizer.pkl # Label encoder
```

### 🛠️ Development & Deployment
```
📁 scripts/                      # Utility scripts (to be created)
├── 🔧 setup_db.py              # Database initialization
├── 🎯 train_model.py           # ML model training
├── 🧹 cleanup.py               # Cleanup utilities
└── 📊 backup_db.py             # Database backup

📁 docs/                         # Documentation (to be created)
├── 📖 API.md                   # API documentation
├── 🚀 DEPLOYMENT.md            # Deployment guide
├── 🔧 DEVELOPMENT.md           # Development setup
└── 🎯 FEATURES.md              # Feature documentation

📁 tests/                        # Test files (to be organized)
├── 🧪 test_app.py              # Application tests
├── 🧪 test_models.py           # Model tests
└── 🧪 test_routes.py           # Route tests
```

### 🔧 Configuration & Setup
```
📁 config/                       # Configuration files (to be created)
├── ⚙️ development.py           # Development settings
├── 🚀 production.py            # Production settings
└── 🧪 testing.py               # Testing settings

📁 deployment/                   # Deployment files (to be created)
├── 🐳 Dockerfile              # Docker configuration
├── 🔧 docker-compose.yml      # Docker Compose
├── 🌐 nginx.conf              # Nginx configuration
└── 🚀 gunicorn.conf.py        # Gunicorn configuration
```

## 📋 File Categories

### ✅ Core Files (Keep as is)
- `app.py` - Main application
- `extensions.py` - Flask extensions
- `models.py` - Database models
- `requirements.txt` - Dependencies

### 📁 To Organize into `scripts/`
- `setup_db.py`, `init_db.py`, `setup_sqlite_db.py`
- `train_*.py`, `update_*.py`
- `backup_*.py`, `maintain_*.py`
- `check_*.py`, `verify_*.py`
- `fix_*.py`, `debug_*.py`

### 📁 To Organize into `docs/`
- `README.md`, `HOW_TO_RUN.md`
- `SQLITE_DB_GUIDE.md`, `SUPABASE_SETUP.md`
- `FFMPEG_INSTALLATION_INSTRUCTIONS.md`

### 🗑️ To Clean Up
- `__pycache__/` directories
- Temporary test files
- Old training case files
- Duplicate FFmpeg installations

## 🎯 Recommended Actions

1. **Create organized folder structure**
2. **Move files to appropriate directories**
3. **Create comprehensive documentation**
4. **Set up proper development workflow**
5. **Implement automated testing**
6. **Add deployment configurations**

This structure will make the project much more maintainable and easier to navigate for development and updates.
