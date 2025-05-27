import os
import sys
import subprocess
import platform
import tempfile
import shutil
import zipfile
import urllib.request
import logging

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

def install_ffmpeg_linux():
    """Install FFmpeg on Linux"""
    try:
        # Detect distribution
        if os.path.exists('/etc/debian_version'):
            # Debian/Ubuntu
            logger.info("Detected Debian/Ubuntu system")
            subprocess.run(['sudo', 'apt', 'update'], check=True)
            subprocess.run(['sudo', 'apt', 'install', '-y', 'ffmpeg'], check=True)
        elif os.path.exists('/etc/fedora-release'):
            # Fedora
            logger.info("Detected Fedora system")
            subprocess.run(['sudo', 'dnf', 'install', '-y', 'ffmpeg'], check=True)
        elif os.path.exists('/etc/arch-release'):
            # Arch Linux
            logger.info("Detected Arch Linux system")
            subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'ffmpeg'], check=True)
        else:
            logger.warning("Unknown Linux distribution, trying apt-get...")
            subprocess.run(['sudo', 'apt-get', 'update'], check=True)
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'ffmpeg'], check=True)
        
        logger.info("FFmpeg installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {str(e)}")
        return False

def install_ffmpeg_mac():
    """Install FFmpeg on macOS using Homebrew"""
    try:
        # Check if Homebrew is installed
        try:
            subprocess.run(['brew', '--version'], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE,
                          check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            logger.info("Homebrew not found, installing...")
            homebrew_install_cmd = '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'
            subprocess.run(homebrew_install_cmd, shell=True, check=True)
        
        # Install FFmpeg
        logger.info("Installing FFmpeg with Homebrew...")
        subprocess.run(['brew', 'install', 'ffmpeg'], check=True)
        
        logger.info("FFmpeg installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing FFmpeg: {str(e)}")
        return False

def main():
    """Main function to check and install FFmpeg"""
    logger.info("Checking if FFmpeg is installed...")
    
    if is_ffmpeg_installed():
        logger.info("FFmpeg is already installed and working correctly!")
        return True
    
    logger.info("FFmpeg not found. Installing...")
    
    system = platform.system()
    if system == "Windows":
        success = install_ffmpeg_windows()
    elif system == "Linux":
        success = install_ffmpeg_linux()
    elif system == "Darwin":  # macOS
        success = install_ffmpeg_mac()
    else:
        logger.error(f"Unsupported operating system: {system}")
        return False
    
    if success:
        logger.info("FFmpeg installation completed successfully!")
        logger.info("Please restart your application for the changes to take effect.")
    else:
        logger.error("Failed to install FFmpeg. Please install it manually.")
    
    return success

if __name__ == "__main__":
    main()
