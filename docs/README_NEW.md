# 🚔 Intelligent FIR Filing System

A comprehensive web-based First Information Report (FIR) filing system with AI-powered features, voice transcription, evidence management, and automated legal section mapping.

## 🌟 Features

### 🔐 Core Functionality
- **User Authentication** - Secure login/registration with role-based access
- **FIR Management** - Create, view, edit, and track FIR cases
- **Evidence Management** - Upload, analyze, and manage digital evidence
- **PDF Generation** - Automated PDF generation with dynamic content sizing
- **Multi-language Support** - Support for multiple Indian languages

### 🤖 AI-Powered Features
- **Voice Transcription** - Convert speech to text for FIR filing
- **Legal Section Mapping** - Automatic IPC section suggestion using ML
- **Evidence Analysis** - AI-powered evidence categorization
- **Chatbot Assistant** - Interactive help and guidance
- **Document Verification** - QR code-based document authenticity

### 👥 User Roles
- **Public Users** - File and track FIRs
- **Police Officers** - Process and investigate cases
- **Administrators** - System management and oversight

## 🏗️ Project Structure

```
📁 Intelligent-FIR/
├── 🚀 app.py                    # Main Flask application
├── 🔧 extensions.py             # Flask extensions
├── 📊 models.py                 # Database models
├── ⚙️ requirements.txt          # Dependencies
├── 📋 PROJECT_STRUCTURE.md      # Detailed structure guide
│
├── 📁 routes/                   # Application routes
│   ├── 🔐 auth.py              # Authentication
│   ├── 📄 fir.py               # FIR management
│   ├── 🔍 evidence.py          # Evidence handling
│   └── ...
│
├── 📁 utils/                    # Utility functions
│   ├── 🧠 ml_analyzer.py       # Machine learning
│   ├── 📄 pdf_generator.py     # PDF generation
│   ├── 🎤 speech_recognition.py # Voice processing
│   └── ...
│
├── 📁 templates/                # HTML templates
├── 📁 static/                   # Static assets & uploads
├── 📁 scripts/                  # Setup & utility scripts
├── 📁 docs/                     # Documentation
└── 📁 instance/                 # Database files
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- FFmpeg (for audio processing)
- SQLite (included with Python)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent-FIR
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python scripts/setup_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open http://localhost:5000 in your browser
   - Register a new account or use demo credentials

## 📖 Documentation

- **[Project Structure](PROJECT_STRUCTURE.md)** - Detailed project organization
- **[API Documentation](docs/API.md)** - API endpoints and usage
- **[Deployment Guide](docs/DEPLOYMENT.md)** - Production deployment
- **[Development Setup](docs/DEVELOPMENT.md)** - Development environment
- **[Feature Guide](docs/FEATURES.md)** - Detailed feature documentation

## 🔧 Configuration

### Environment Variables
```bash
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DEBUG=True

# Database
DATABASE_URL=sqlite:///fir_system.db

# Optional: AI Features
OPENAI_API_KEY=your-openai-api-key
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

### Database Setup
The system uses SQLite by default. For production, consider PostgreSQL:
```bash
DATABASE_URL=postgresql://user:password@localhost/fir_system
```

## 🧪 Testing

Run the test suite:
```bash
python -m pytest tests/
```

Run specific tests:
```bash
python scripts/test_app.py
python scripts/test_models.py
```

## 📊 Recent Updates

### ✅ Fixed Issues
- **PDF Generation** - Dynamic description sizing and proper formatting
- **Static File Serving** - Fixed 404 errors for uploaded evidence files
- **Routing Errors** - Resolved Flask routing endpoint mismatches
- **File Path Handling** - Cross-platform compatibility improvements

### 🆕 New Features
- **Enhanced PDF Generation** - Professional formatting with tables
- **Evidence Management** - Improved file upload and display
- **Error Handling** - Better error messages and logging
- **Project Organization** - Cleaner folder structure

## 🛠️ Development

### Adding New Features
1. Create feature branch: `git checkout -b feature/new-feature`
2. Add routes in `routes/` directory
3. Add utilities in `utils/` directory
4. Add templates in `templates/` directory
5. Update documentation
6. Test thoroughly
7. Submit pull request

### Database Migrations
```bash
python scripts/backup_db.py          # Backup before changes
python scripts/setup_db.py           # Apply schema changes
python scripts/verify_db.py          # Verify changes
```

## 🚀 Deployment

### Development
```bash
python app.py
```

### Production
```bash
# Using Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app

# Using Waitress
python deployment/waitress_server.py
```

### Docker
```bash
docker build -t intelligent-fir .
docker run -p 5000:5000 intelligent-fir
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Update documentation
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check the `docs/` directory for detailed guides
- **Development**: See `docs/DEVELOPMENT.md` for setup instructions

## 🙏 Acknowledgments

- Flask framework and community
- OpenAI for AI capabilities
- Google Cloud for speech recognition
- ReportLab for PDF generation
- All contributors and testers

---

**Made with ❤️ for efficient law enforcement and citizen services**
