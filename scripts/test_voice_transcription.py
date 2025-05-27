"""
Test script for voice transcription functionality.
"""

import os
import sys
import logging
import tempfile
import requests
import json
import time
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
API_BASE_URL = "http://localhost:5000/api"
SPEECH_ENDPOINT = f"{API_BASE_URL}/speech"
TEST_ENDPOINT = f"{SPEECH_ENDPOINT}/test"
UPLOAD_ENDPOINT = f"{SPEECH_ENDPOINT}/upload"
STATUS_ENDPOINT = f"{SPEECH_ENDPOINT}/status"
LANGUAGES_ENDPOINT = f"{SPEECH_ENDPOINT}/languages"

def test_speech_recognition_endpoint():
    """Test the speech recognition test endpoint"""
    try:
        logger.info(f"Testing speech recognition endpoint: {TEST_ENDPOINT}")
        response = requests.get(TEST_ENDPOINT)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Speech recognition test successful: {json.dumps(data, indent=2)}")
            return True
        else:
            logger.error(f"Speech recognition test failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing speech recognition endpoint: {str(e)}")
        return False

def test_languages_endpoint():
    """Test the languages endpoint"""
    try:
        logger.info(f"Testing languages endpoint: {LANGUAGES_ENDPOINT}")
        response = requests.get(LANGUAGES_ENDPOINT)
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Languages endpoint successful: {len(data)} languages available")
            return True
        else:
            logger.error(f"Languages endpoint failed with status code {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error testing languages endpoint: {str(e)}")
        return False

def create_test_audio_file():
    """Create a test audio file using ffmpeg"""
    try:
        # Create a temporary WAV file with 3 seconds of silence
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        
        logger.info(f"Creating test audio file: {temp_file.name}")
        
        # Use ffmpeg to create a silent audio file
        import subprocess
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',           # Use libavfilter
            '-i', 'anullsrc=r=44100:cl=mono',  # Generate silence at 44.1kHz mono
            '-t', '3',               # 3 seconds duration
            '-q:a', '0',             # Highest quality
            '-y',                    # Overwrite output file
            temp_file.name           # Output file
        ], check=True, capture_output=True)
        
        logger.info(f"Test audio file created successfully: {temp_file.name}")
        return temp_file.name
    except Exception as e:
        logger.error(f"Error creating test audio file: {str(e)}")
        return None

def test_upload_endpoint(audio_file_path):
    """Test the upload endpoint with a test audio file"""
    try:
        logger.info(f"Testing upload endpoint: {UPLOAD_ENDPOINT}")
        
        # Check if file exists
        if not os.path.exists(audio_file_path):
            logger.error(f"Audio file does not exist: {audio_file_path}")
            return False
        
        # Create multipart form data with audio file
        with open(audio_file_path, 'rb') as f:
            files = {'audio': (os.path.basename(audio_file_path), f, 'audio/wav')}
            
            # Send request
            response = requests.post(UPLOAD_ENDPOINT, files=files)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Upload successful: {json.dumps(data, indent=2)}")
                
                # Return task ID for status polling
                return data.get('task_id')
            else:
                logger.error(f"Upload failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return None
    except Exception as e:
        logger.error(f"Error testing upload endpoint: {str(e)}")
        return None

def test_status_endpoint(task_id):
    """Test the status endpoint with a task ID"""
    try:
        logger.info(f"Testing status endpoint: {STATUS_ENDPOINT}/{task_id}")
        
        # Poll status endpoint until transcription is complete or failed
        max_attempts = 10
        for attempt in range(max_attempts):
            response = requests.get(f"{STATUS_ENDPOINT}/{task_id}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Status check {attempt+1}/{max_attempts}: {data.get('status')} - {data.get('message')}")
                
                # Check if transcription is complete or failed
                if data.get('status') in ['completed', 'failed']:
                    logger.info(f"Transcription {data.get('status')}: {json.dumps(data, indent=2)}")
                    return data.get('status') == 'completed'
                
                # Wait before next attempt
                time.sleep(2)
            else:
                logger.error(f"Status check failed with status code {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
        
        logger.error(f"Transcription did not complete after {max_attempts} attempts")
        return False
    except Exception as e:
        logger.error(f"Error testing status endpoint: {str(e)}")
        return False

def run_all_tests():
    """Run all tests for voice transcription"""
    logger.info("Starting voice transcription tests...")
    
    # Test speech recognition endpoint
    test_result = test_speech_recognition_endpoint()
    logger.info(f"Speech recognition test: {'PASSED' if test_result else 'FAILED'}")
    
    # Test languages endpoint
    languages_result = test_languages_endpoint()
    logger.info(f"Languages endpoint test: {'PASSED' if languages_result else 'FAILED'}")
    
    # Create test audio file
    audio_file_path = create_test_audio_file()
    if not audio_file_path:
        logger.error("Failed to create test audio file, skipping upload test")
        return False
    
    # Test upload endpoint
    task_id = test_upload_endpoint(audio_file_path)
    if not task_id:
        logger.error("Failed to upload audio file, skipping status test")
        return False
    
    # Test status endpoint
    status_result = test_status_endpoint(task_id)
    logger.info(f"Status endpoint test: {'PASSED' if status_result else 'FAILED'}")
    
    # Clean up test audio file
    try:
        os.remove(audio_file_path)
        logger.info(f"Removed test audio file: {audio_file_path}")
    except Exception as e:
        logger.warning(f"Failed to remove test audio file: {str(e)}")
    
    # Overall result
    overall_result = test_result and languages_result and status_result
    logger.info(f"Overall test result: {'PASSED' if overall_result else 'FAILED'}")
    
    return overall_result

if __name__ == "__main__":
    print("=== Voice Transcription Test Tool ===")
    success = run_all_tests()
    
    if success:
        print("\n✅ All tests passed! Voice transcription is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the logs for details.")
        sys.exit(1)
