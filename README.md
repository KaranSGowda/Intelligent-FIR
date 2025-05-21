# Intelligent FIR System

An AI-powered First Information Report (FIR) management system that uses machine learning to analyze complaints and determine applicable Indian Penal Code (IPC) sections.

## Overview

The Intelligent FIR System is designed to modernize and streamline the process of filing and managing First Information Reports in the Indian legal system. It leverages natural language processing and machine learning to analyze complaint texts and automatically suggest relevant IPC sections, making the legal classification process more efficient and consistent.

## Key Features

- **AI-Powered Complaint Analysis**: Automatically analyzes complaint text to determine applicable IPC sections
- **User Role Management**: Supports different user roles (Public, Police, Admin) with appropriate access controls
- **Chatbot Interface**: Interactive chatbot for retrieving case information and legal guidance
- **Evidence Management**: Upload and manage different types of evidence (images, audio, etc.)
- **PDF Generation**: Generate official FIR documents in PDF format
- **Speech Recognition**: Convert spoken complaints to text for easier filing

## Technology Stack

- **Backend**: Flask (Python web framework)
- **Database**: SQLAlchemy with SQLite (configurable for other databases)
- **Machine Learning**: scikit-learn, NLTK for text processing and classification
- **Authentication**: Flask-Login for user authentication and session management
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **AI Integration**: OpenAI API (optional fallback for complaint analysis)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- NLTK data files (for text processing)

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/intelligent-fir-system.git
   cd intelligent-fir-system
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Download required NLTK data:
   ```
   python download_nltk_data.py
   ```

5. Set up environment variables (create a `.env` file in the project root):
   ```
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=1
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///fir_system.db
   # Optional: Add OpenAI API key if using OpenAI integration
   # OPENAI_API_KEY=your-openai-api-key
   ```

6. Initialize the database:
   ```
   python -c "from app import create_app; app = create_app(); from extensions import db; with app.app_context(): db.create_all()"
   ```

## Running the Application

Start the development server:
```
python main.py
```

The application will be available at http://127.0.0.1:5000/

For production deployment, use a production WSGI server like Gunicorn:
```
gunicorn --bind 0.0.0.0:5000 main:app
```

## Project Structure

- `app.py`: Main application factory and configuration
- `main.py`: Entry point for running the application
- `extensions.py`: Flask extensions (SQLAlchemy, LoginManager)
- `models/`: Database models
  - `__init__.py`: Model definitions (User, FIR, Evidence, LegalSection)
- `routes/`: Flask blueprints for different sections of the application
  - `auth.py`: Authentication routes (login, register, logout)
  - `fir.py`: FIR management routes
  - `admin.py`: Admin panel routes
  - `chatbot.py`: Chatbot API routes
- `utils/`: Utility modules
  - `ml_analyzer.py`: Machine learning model for complaint analysis
  - `chatbot.py`: Chatbot logic for answering queries
  - `legal_mapper.py`: Maps complaints to legal sections
  - `speech_recognition.py`: Speech-to-text functionality
  - `pdf_generator.py`: Generates PDF documents
- `templates/`: HTML templates
- `static/`: Static assets (CSS, JavaScript, images)

## Machine Learning Components

The system uses two approaches for analyzing complaints:

1. **ML-based Classification**: Uses TF-IDF vectorization and a multi-label classifier to predict applicable IPC sections based on complaint text.

2. **Keyword-based Matching**: A fallback method that uses predefined keywords associated with each IPC section.

The ML model is trained automatically when the application starts, using a combination of predefined training data and historical FIR data from the database.

## Troubleshooting

### NLTK Data Issues

If you encounter errors related to NLTK data (like WordNet), run:
```
python download_nltk_data.py
```

This will download all required NLTK data packages.

### Database Initialization

If you encounter database-related errors, ensure the database is properly initialized:
```
python -c "from app import create_app; app = create_app(); from extensions import db; with app.app_context(): db.create_all()"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
