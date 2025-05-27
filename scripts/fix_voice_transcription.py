"""
Script to fix voice transcription issues.
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ffmpeg():
    """Check if ffmpeg is installed and accessible"""
    try:
        subprocess.check_output(['ffmpeg', '-version'], stderr=subprocess.STDOUT)
        logger.info("✅ ffmpeg is installed and accessible")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        logger.error("❌ ffmpeg is not installed or not in PATH")
        return False

def check_dependencies():
    """Check if required Python packages are installed"""
    missing_packages = []

    # Check SpeechRecognition
    try:
        import speech_recognition
        logger.info(f"✅ SpeechRecognition is installed (version {speech_recognition.__version__})")
    except ImportError:
        logger.error("❌ SpeechRecognition is not installed")
        missing_packages.append("SpeechRecognition")

    # Check pydub
    try:
        import pydub
        logger.info(f"✅ pydub is installed")
    except ImportError:
        logger.error("❌ pydub is not installed")
        missing_packages.append("pydub")

    # Check pyaudio (optional but recommended)
    try:
        import pyaudio
        logger.info(f"✅ PyAudio is installed")
    except ImportError:
        logger.warning("⚠️ PyAudio is not installed (optional for microphone support)")
        missing_packages.append("pyaudio")

    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies"""
    if not packages:
        logger.info("No packages to install")
        return True

    logger.info(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
        logger.info("✅ All packages installed successfully")
        return True
    except subprocess.SubprocessError as e:
        logger.error(f"❌ Failed to install packages: {str(e)}")
        return False

def check_directories():
    """Check if required directories exist and are writable"""
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))

    # Check uploads directory
    uploads_dir = os.path.join(project_root, 'uploads', 'audio')
    if not os.path.exists(uploads_dir):
        logger.warning(f"⚠️ Uploads directory does not exist: {uploads_dir}")
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            logger.info(f"✅ Created uploads directory: {uploads_dir}")
        except Exception as e:
            logger.error(f"❌ Failed to create uploads directory: {str(e)}")
            return False

    # Check if directory is writable
    if not os.access(uploads_dir, os.W_OK):
        logger.error(f"❌ Uploads directory is not writable: {uploads_dir}")
        return False

    logger.info(f"✅ Uploads directory exists and is writable: {uploads_dir}")
    return True

def fix_voice_transcription():
    """Fix voice transcription issues"""
    logger.info("Starting voice transcription fix...")

    # Check ffmpeg
    ffmpeg_ok = check_ffmpeg()

    # Check dependencies
    missing_packages = check_dependencies()

    # Install missing packages
    if missing_packages:
        install_ok = install_dependencies(missing_packages)
        if not install_ok:
            logger.error("❌ Failed to install required packages")
            return False

    # Check directories
    dirs_ok = check_directories()

    # Overall status
    if ffmpeg_ok and dirs_ok:
        logger.info("✅ All checks passed! Voice transcription should work now.")
        return True
    else:
        logger.error("❌ Some issues were found. Please fix them manually.")
        return False

if __name__ == "__main__":
    print("=== Voice Transcription Fix Tool ===")
    success = fix_voice_transcription()

    if success:
        print("\n✅ Voice transcription should work now. Please restart your application.")
        sys.exit(0)
    else:
        print("\n❌ Some issues could not be fixed automatically.")

        if not check_ffmpeg():
            print("\nTo install ffmpeg:")
            print("- Windows: Download from https://ffmpeg.org/download.html or use Chocolatey: choco install ffmpeg")
            print("- macOS: Use Homebrew: brew install ffmpeg")
            print("- Linux: Use your package manager, e.g., apt install ffmpeg")

        sys.exit(1)
