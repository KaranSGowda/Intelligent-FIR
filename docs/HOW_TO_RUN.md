# How to Run the Intelligent FIR System

This guide explains how to run the Intelligent FIR System with voice transcription support.

## Prerequisites

- Python 3.8 or higher
- FFmpeg (installed automatically by the setup script)

## Setup and Installation

1. **Clone the repository** (if you haven't already)

2. **Install Python dependencies**:
   ```
   pip install -r requirements.txt
   ```

3. **Download NLTK data**:
   ```
   python download_nltk_data.py
   ```

4. **Set up FFmpeg** (required for voice transcription):
   ```
   python fix_pydub_ffmpeg.py
   ```
   This script will:
   - Download and install FFmpeg in the project directory
   - Configure the application to use the local FFmpeg installation

## Running the Application

After completing the setup, you can run the application using:

```
python main.py
```

The application will be available at:
- http://127.0.0.1:5000

## Troubleshooting

### Voice Transcription Issues

If you encounter issues with voice transcription:

1. Make sure FFmpeg is properly installed:
   ```
   python fix_pydub_ffmpeg.py
   ```

2. Restart the application after installing FFmpeg

3. Try using a different browser (Chrome or Firefox recommended)

4. Ensure your microphone is working properly

### Other Issues

- If you see database errors, make sure the database file exists and has the correct permissions
- If you see module import errors, make sure all dependencies are installed
- If the application fails to start, check the console output for specific error messages

## Features

- File and manage First Information Reports (FIRs)
- AI-powered complaint analysis
- Evidence management
- Voice transcription
- Chatbot interface
- PDF generation
- Multi-language support

## Login Information

Default login credentials:
- Username: admin
- Password: admin123

## Additional Information

For more details about the project, refer to the main README.md file.
