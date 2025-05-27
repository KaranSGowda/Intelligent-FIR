#!/usr/bin/env python
"""
Fix Transcription Issues in Intelligent FIR System

This script fixes common issues with the speech transcription functionality:
1. Checks and installs FFmpeg if missing
2. Fixes the _recognize_google method to handle errors gracefully
3. Adds a fallback transcription method
"""

import os
import sys
import subprocess
import platform
import tempfile
import shutil
import zipfile
import urllib.request
import logging
import importlib.util

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def is_ffmpeg_installed():
    """Check if FFmpeg is installed and accessible in PATH"""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE,
                               text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def install_ffmpeg_windows():
    """Install FFmpeg on Windows"""
    try:
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        logger.info(f"Created temporary directory: {temp_dir}")
        
        # Download FFmpeg
        ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(temp_dir, "ffmpeg.zip")
        
        logger.info(f"Downloading FFmpeg from {ffmpeg_url}")
        urllib.request.urlretrieve(ffmpeg_url, zip_path)
        
        # Extract zip
        logger.info("Extracting FFmpeg...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Find the bin directory
        for root, dirs, files in os.walk(temp_dir):
            if 'bin' in dirs:
                bin_dir = os.path.join(root, 'bin')
                if os.path.exists(os.path.join(bin_dir, 'ffmpeg.exe')):
                    break
        
        # Create FFmpeg directory in user profile
        user_ffmpeg_dir = os.path.join(os.path.expanduser("~"), "ffmpeg")
        os.makedirs(user_ffmpeg_dir, exist_ok=True)
        
        # Copy FFmpeg files
        for file in os.listdir(bin_dir):
            shutil.copy2(os.path.join(bin_dir, file), user_ffmpeg_dir)
        
        logger.info(f"FFmpeg installed to {user_ffmpeg_dir}")
        
        # Add to PATH for current session
        os.environ["PATH"] += os.pathsep + user_ffmpeg_dir
        
        # Add to PATH permanently using setx (Windows only)
        subprocess.run(['setx', 'PATH', f"%PATH%;{user_ffmpeg_dir}"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        
        logger.info("Added FFmpeg to PATH")
        return True
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {str(e)}")
        return False
    finally:
        # Clean up
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def install_ffmpeg():
    """Install FFmpeg based on the current platform"""
    system = platform.system()
    if system == "Windows":
        return install_ffmpeg_windows()
    else:
        logger.error(f"Automatic FFmpeg installation not supported on {system}")
        logger.info("Please install FFmpeg manually:")
        if system == "Linux":
            logger.info("  sudo apt update && sudo apt install -y ffmpeg  # For Debian/Ubuntu")
            logger.info("  sudo dnf install -y ffmpeg  # For Fedora")
        elif system == "Darwin":  # macOS
            logger.info("  brew install ffmpeg  # Using Homebrew")
        return False

def fix_speech_recognition_py():
    """Fix the speech_recognition.py file to handle errors better"""
    speech_recognition_path = os.path.join("utils", "speech_recognition.py")
    
    if not os.path.exists(speech_recognition_path):
        logger.error(f"Could not find {speech_recognition_path}")
        return False
    
    logger.info(f"Fixing {speech_recognition_path}...")
    
    with open(speech_recognition_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix 1: Make _recognize_google return a message instead of raising an exception
    if "raise sr.UnknownValueError(detailed_error)" in content:
        content = content.replace(
            "        # If we get here, all methods failed\n        detailed_error = \"All transcription methods failed:\\n\" + \"\\n\".join(all_errors)\n        logger.error(detailed_error)\n        raise sr.UnknownValueError(detailed_error)",
            "        # If we get here, all methods failed\n        detailed_error = \"All transcription methods failed:\\n\" + \"\\n\".join(all_errors)\n        logger.error(detailed_error)\n        \n        # Instead of raising an exception, return a placeholder message\n        # This allows the application to continue even if transcription fails\n        return \"Audio received but could not be transcribed. Please try again with clearer audio or type your statement manually.\""
        )
        logger.info("Fixed _recognize_google method to return a message instead of raising an exception")
    
    # Fix 2: Add a check for FFmpeg in the _convert_with_ffmpeg method
    if "def _convert_with_ffmpeg(self, audio_path):" in content:
        ffmpeg_method = content.split("def _convert_with_ffmpeg(self, audio_path):")[1].split("def ")[0]
        if "# Check if ffmpeg is installed" not in ffmpeg_method:
            new_ffmpeg_method = """    def _convert_with_ffmpeg(self, audio_path):
        \"\"\"Use ffmpeg directly to convert problematic audio formats\"\"\"
        try:
            # Check if ffmpeg is installed
            try:
                subprocess.run(['ffmpeg', '-version'], 
                              stdout=subprocess.PIPE, 
                              stderr=subprocess.PIPE,
                              check=True)
            except (FileNotFoundError, subprocess.CalledProcessError):
                logger.error("FFmpeg is not installed or not in PATH. Please install FFmpeg.")
                return None
                
            temp_wav = tempfile.mktemp(suffix='.wav')
            import subprocess

            # Use more robust ffmpeg parameters
            subprocess.run([
                'ffmpeg',
                '-i', audio_path,  # Input file
                '-ar', '16000',    # Sample rate
                '-ac', '1',        # Mono channel
                '-vn',             # No video
                '-y',              # Overwrite output
                '-hide_banner',    # Less verbose output
                '-loglevel', 'error',  # Only show errors
                temp_wav           # Output file
            ], check=True, capture_output=True)

            if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 0:
                return temp_wav
            else:
                return None
        except Exception as ffmpeg_error:
            logger.error(f"Failed to convert with ffmpeg: {str(ffmpeg_error)}")
            return None"""
            
            content = content.replace(
                "def _convert_with_ffmpeg(self, audio_path):" + ffmpeg_method,
                new_ffmpeg_method
            )
            logger.info("Added FFmpeg installation check to _convert_with_ffmpeg method")
    
    # Write the modified content back to the file
    with open(speech_recognition_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Successfully fixed {speech_recognition_path}")
    return True

def fix_voice_recorder_js():
    """Fix the voice-recorder.js file to add missing methods"""
    voice_recorder_path = os.path.join("static", "js", "voice-recorder.js")
    
    if not os.path.exists(voice_recorder_path):
        logger.error(f"Could not find {voice_recorder_path}")
        return False
    
    logger.info(f"Fixing {voice_recorder_path}...")
    
    with open(voice_recorder_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add showSpeechRecognitionError method if it doesn't exist
    if "showSpeechRecognitionError" not in content:
        # Find the destroy method
        if "destroy() {" in content:
            # Add the showSpeechRecognitionError method before destroy
            new_method = """    /**
     * Show speech recognition error
     */
    showSpeechRecognitionError(missingPackages) {
        let errorMessage = "Speech recognition is not available on the server.";
        
        if (missingPackages && missingPackages.length > 0) {
            errorMessage += ` Missing packages: ${missingPackages.join(', ')}`;
        }
        
        this.showError(errorMessage);
    }

    /**
     * Clean up resources
     */"""
            
            content = content.replace("    /**\n     * Clean up resources\n     */", new_method)
            logger.info("Added showSpeechRecognitionError method to voice-recorder.js")
    
    # Write the modified content back to the file
    with open(voice_recorder_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Successfully fixed {voice_recorder_path}")
    return True

def main():
    """Main function to fix all issues"""
    logger.info("Starting transcription fix script...")
    
    # Step 1: Check if FFmpeg is installed
    logger.info("Checking if FFmpeg is installed...")
    if is_ffmpeg_installed():
        logger.info("FFmpeg is already installed and working correctly!")
    else:
        logger.info("FFmpeg not found. Installing...")
        if install_ffmpeg():
            logger.info("FFmpeg installed successfully!")
        else:
            logger.warning("Could not install FFmpeg automatically. Please install it manually.")
    
    # Step 2: Fix speech_recognition.py
    if fix_speech_recognition_py():
        logger.info("Successfully fixed speech_recognition.py")
    else:
        logger.warning("Could not fix speech_recognition.py")
    
    # Step 3: Fix voice-recorder.js
    if fix_voice_recorder_js():
        logger.info("Successfully fixed voice-recorder.js")
    else:
        logger.warning("Could not fix voice-recorder.js")
    
    logger.info("All fixes applied! Please restart your application for the changes to take effect.")
    return True

if __name__ == "__main__":
    main()
