"""
Fix PyDub FFmpeg Path

This script modifies the PyDub library to use our local FFmpeg installation.
"""

import os
import sys
import importlib.util
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_pydub_utils():
    """Find the pydub.utils module path"""
    try:
        spec = importlib.util.find_spec("pydub.utils")
        if spec is None:
            logger.error("Could not find pydub.utils module")
            return None
        return spec.origin
    except ImportError:
        logger.error("pydub is not installed")
        return None

def fix_pydub_ffmpeg_path():
    """Fix the FFmpeg path in pydub.utils"""
    pydub_utils_path = find_pydub_utils()
    if not pydub_utils_path:
        return False

    logger.info(f"Found pydub.utils at: {pydub_utils_path}")

    # Get the absolute path to our local FFmpeg
    ffmpeg_dir = os.path.abspath("ffmpeg")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")
    ffprobe_path = os.path.join(ffmpeg_dir, "ffprobe.exe")

    if not os.path.exists(ffmpeg_path):
        logger.error(f"FFmpeg not found at: {ffmpeg_path}")
        return False

    logger.info(f"Using FFmpeg at: {ffmpeg_path}")

    # Read the pydub.utils file
    with open(pydub_utils_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if we've already modified the file
    if "# Modified by fix_pydub_ffmpeg.py" in content:
        logger.info("pydub.utils has already been modified")
        return True

    # Find the get_encoder_name and get_player_name functions
    if "def get_encoder_name():" not in content or "def get_player_name():" not in content:
        logger.error("Could not find the functions to modify in pydub.utils")
        return False

    # Replace the get_encoder_name function
    new_get_encoder_name = f'''
def get_encoder_name():
    """
    # Modified by fix_pydub_ffmpeg.py
    Return the name of the default encoder.
    """
    return r"{ffmpeg_path}"
'''

    # Replace the get_player_name function
    new_get_player_name = f'''
def get_player_name():
    """
    # Modified by fix_pydub_ffmpeg.py
    Return the name of the default player.
    """
    return r"{ffmpeg_path}"
'''

    # Replace the get_prober_name function
    new_get_prober_name = f'''
def get_prober_name():
    """
    # Modified by fix_pydub_ffmpeg.py
    Return the name of the default prober.
    """
    return r"{ffprobe_path}"
'''

    # Replace the functions in the content
    content = content.replace("def get_encoder_name():", new_get_encoder_name)
    content = content.replace("def get_player_name():", new_get_player_name)
    content = content.replace("def get_prober_name():", new_get_prober_name)

    # Write the modified content back to the file
    with open(pydub_utils_path, 'w', encoding='utf-8') as f:
        f.write(content)

    logger.info("Successfully modified pydub.utils to use local FFmpeg")
    return True

if __name__ == "__main__":
    if fix_pydub_ffmpeg_path():
        logger.info("Successfully fixed pydub FFmpeg path")
        sys.exit(0)
    else:
        logger.error("Failed to fix pydub FFmpeg path")
        sys.exit(1)
