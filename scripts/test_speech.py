"""
Test script for speech recognition functionality.
"""

import os
import sys
import logging
import tempfile

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_speech_recognition():
    """Test if speech recognition is working properly"""
    try:
        import speech_recognition as sr
        logger.info(f"SpeechRecognition version: {sr.__version__}")
        
        # Create a recognizer
        r = sr.Recognizer()
        logger.info("Recognizer created successfully")
        
        # Test with a sample audio file if provided
        if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
            audio_path = sys.argv[1]
            logger.info(f"Testing with audio file: {audio_path}")
            
            try:
                with sr.AudioFile(audio_path) as source:
                    audio = r.record(source)
                    logger.info("Audio recorded from file successfully")
                    
                    # Try to recognize
                    text = r.recognize_google(audio)
                    logger.info(f"Transcription result: {text}")
                    return True
            except Exception as e:
                logger.error(f"Error processing audio file: {str(e)}")
                return False
        else:
            logger.info("No audio file provided, testing with microphone")
            
            # Test microphone
            try:
                with sr.Microphone() as source:
                    logger.info("Say something...")
                    audio = r.listen(source, timeout=5)
                    logger.info("Audio recorded from microphone successfully")
                    
                    # Try to recognize
                    text = r.recognize_google(audio)
                    logger.info(f"Transcription result: {text}")
                    return True
            except Exception as e:
                logger.error(f"Error processing microphone input: {str(e)}")
                return False
    except ImportError as e:
        logger.error(f"SpeechRecognition not installed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

def test_audio_conversion():
    """Test if audio conversion is working properly"""
    try:
        from pydub import AudioSegment
        logger.info(f"Pydub installed successfully")
        
        # Create a simple audio segment
        audio = AudioSegment.silent(duration=1000)  # 1 second of silence
        
        # Try to export it
        temp_path = os.path.join(tempfile.gettempdir(), "test_audio.wav")
        audio.export(temp_path, format="wav")
        
        if os.path.exists(temp_path):
            logger.info(f"Audio export successful: {temp_path}")
            os.remove(temp_path)
            return True
        else:
            logger.error("Failed to export audio file")
            return False
    except ImportError as e:
        logger.error(f"Pydub not installed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error testing audio conversion: {str(e)}")
        return False

if __name__ == "__main__":
    print("Testing speech recognition functionality...")
    
    # Test audio conversion
    conversion_result = test_audio_conversion()
    print(f"Audio conversion test: {'PASSED' if conversion_result else 'FAILED'}")
    
    # Test speech recognition
    recognition_result = test_speech_recognition()
    print(f"Speech recognition test: {'PASSED' if recognition_result else 'FAILED'}")
    
    # Overall result
    if conversion_result and recognition_result:
        print("All tests PASSED!")
        sys.exit(0)
    else:
        print("Some tests FAILED!")
        sys.exit(1)
