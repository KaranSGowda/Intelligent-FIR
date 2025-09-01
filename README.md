# Intelligent FIR System

A comprehensive First Information Report (FIR) management system with AI-powered analysis and modern web interface.

## 🏗️ Project Structure

This project follows a clean separation of concerns with the following structure:

```
Intelligent-FIR/
├── backend/                 # Python Flask Backend
│   ├── app.py              # Main Flask application
│   ├── extensions.py       # Flask extensions configuration
│   ├── models.py           # Database models
│   ├── routes/             # API routes and endpoints
│   ├── models/             # Database models
│   ├── utils/              # Utility functions
│   ├── config/             # Configuration files
│   ├── controllers/        # Business logic controllers
│   ├── middlewares/        # Custom middleware
│   ├── services/           # Business services
│   ├── uploads/            # File upload directory
│   └── requirements.txt    # Python dependencies
├── frontend/               # Frontend Assets
│   ├── static/             # Static files (CSS, JS, images)
│   ├── src/                # Source files
│   │   ├── templates/      # HTML templates
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   ├── styles/         # CSS stylesheets
│   │   └── utils/          # Frontend utilities
│   └── public/             # Public assets
├── docs/                   # Documentation
├── scripts/                # Utility scripts
├── tests/                  # Test files
├── deployment/             # Deployment configurations
├── main.py                 # Application entry point
└── README.md               # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- SQLite (or PostgreSQL for production)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Intelligent-FIR
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your configuration
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`

## 🔧 Development

### Backend Development
- All Python code is in the `backend/` directory
- Use `python main.py` to run the development server
- The Flask app is configured in `backend/app.py`

### Frontend Development
- HTML templates are in `frontend/src/templates/`
- CSS files are in `frontend/src/styles/`
- JavaScript files are in `frontend/static/js/`
- Static assets are in `frontend/static/`

### Database
- SQLite database: `backend/fir_system.db`
- Database models: `backend/models/`
- Database backups: `backend/backups/`

## 📚 Features

- **User Management**: Registration, login, role-based access
- **FIR Management**: Create, view, and manage FIR reports
- **AI Analysis**: Machine learning-powered case analysis
- **Document Generation**: PDF report generation
- **File Uploads**: Support for images and documents
- **Admin Dashboard**: Comprehensive admin interface
- **Police Dashboard**: Specialized police interface
- **Chatbot Integration**: AI-powered assistance

## 🧪 Testing

Run tests from the project root:
```bash
python -m pytest tests/
```

## 🚀 Deployment

Deployment configurations are in the `deployment/` directory:
- `waitress_server.py` - Production server configuration
- `setup_ffmpeg.bat` - FFmpeg setup for Windows
- `run_with_ffmpeg.bat` - Run application with FFmpeg

## 📖 Documentation

- `docs/README.md` - Main documentation
- `docs/HOW_TO_RUN.md` - Detailed setup instructions
- `docs/DEVELOPMENT_GUIDE.md` - Development guidelines
- `docs/SQLITE_DB_GUIDE.md` - Database management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions, please refer to the documentation in the `docs/` directory or create an issue in the repository.
