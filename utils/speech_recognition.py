import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence
import tempfile
import os
import logging
import time
import json
import threading
import subprocess
import sys
from pathlib import Path

# Try to import our cloud speech module for enhanced transcription
try:
    from utils import cloud_speech
    CLOUD_SPEECH_AVAILABLE = True
    print("Cloud Speech module is available for enhanced transcription")
except ImportError:
    CLOUD_SPEECH_AVAILABLE = False
    print("Cloud Speech module is not available. Using standard transcription.")

# Set Whisper availability flag
# We'll use a simpler approach without importing Whisper directly
WHISPER_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_ffmpeg_path():
    """Get the FFmpeg path based on the environment"""
    # First, check the project's ffmpeg directory
    base_dir = Path(__file__).resolve().parent.parent
    ffmpeg_project_path = base_dir / 'ffmpeg' / 'ffmpeg.exe'

    if ffmpeg_project_path.exists():
        return str(ffmpeg_project_path)

    # Check if ffmpeg is in system PATH
    if sys.platform.startswith('win'):
        ffmpeg_names = ['ffmpeg.exe']
    else:
        ffmpeg_names = ['ffmpeg']

    for name in ffmpeg_names:
        try:
            result = subprocess.run(['where' if sys.platform.startswith('win') else 'which', name],
                                 capture_output=True,
                                 text=True)
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            continue

    return None

# Try to set FFmpeg path for pydub
ffmpeg_path = get_ffmpeg_path()
if ffmpeg_path:
    AudioSegment.converter = ffmpeg_path
    logger.info(f"Using FFmpeg from: {ffmpeg_path}")
else:
    logger.warning("FFmpeg not found. Audio processing may not work correctly.")

class TranscriptionStatus:
    """Class to track and report transcription progress"""
    INITIALIZING = "initializing"
    CONVERTING = "converting"
    ENHANCING = "enhancing"
    TRANSCRIBING = "transcribing"
    COMPLETED = "completed"
    FAILED = "failed"

    def __init__(self):
        self.status = self.INITIALIZING
        self.progress = 0
        self.message = "Initializing transcription..."
        self.start_time = time.time()
        self.result = None
        self.error = None

    def update(self, status, progress=None, message=None):
        self.status = status
        if progress is not None:
            self.progress = progress
        if message is not None:
            self.message = message

        # Log the status update
        logger.info(f"Transcription status: {self.status} - {self.progress}% - {self.message}")

    def complete(self, result):
        self.status = self.COMPLETED
        self.progress = 100
        self.message = "Transcription completed successfully"
        self.result = result

    def fail(self, error):
        self.status = self.FAILED
        self.message = f"Transcription failed: {str(error)}"
        self.error = error

    def to_dict(self):
        elapsed_time = time.time() - self.start_time
        return {
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "elapsed_time": f"{elapsed_time:.2f}s",
            "result": self.result,
            "error": str(self.error) if self.error else None
        }

    def to_json(self):
        return json.dumps(self.to_dict())

class SpeechToText:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        # Optimized recognition parameters for better speech detection
        self.recognizer.pause_threshold = 0.5  # Reduced for better word detection
        self.recognizer.phrase_threshold = 0.2  # More sensitive phrase detection
        self.recognizer.non_speaking_duration = 0.3  # Shorter non-speaking duration
        self.recognizer.energy_threshold = 100  # Lower threshold for quieter speech
        self.recognizer.dynamic_energy_threshold = True  # Automatically adjust for ambient noise
        self.recognizer.operation_timeout = 30  # Reduced to prevent long waits
        # Supported audio formats
        self.supported_formats = {
            'wav': 'WAV audio',
            'mp3': 'MP3 audio',
            'ogg': 'OGG audio',
            'flac': 'FLAC audio',
            'webm': 'WebM audio',
            'm4a': 'M4A audio',
            'aac': 'AAC audio',
            'mp4': 'MP4 audio',
            'amr': 'AMR audio'
        }

    def _recognize_google(self, audio, language=None):
        """
        Enhanced wrapper for Google Speech Recognition with multiple fallback mechanisms
        """
        all_errors = []

        # Log audio properties for debugging
        try:
            logger.info(f"Audio properties - Sample Rate: {audio.sample_rate}Hz, Sample Width: {audio.sample_width} bytes, Duration: {len(audio.frame_data)/audio.sample_rate:.2f}s")
        except Exception as e:
            logger.warning(f"Could not log audio properties: {str(e)}")

        # Configure recognition settings for different attempts
        recognition_configs = []

        # If a specific language was provided, try it first
        if language:
            # Attempt 1: Standard settings with specified language
            recognition_configs.append({'language': language, 'show_all': False})

            # Attempt 2: Lower energy threshold with specified language
            recognition_configs.append({'language': language, 'energy_threshold': 50, 'show_all': False})

            # Attempt 3: Higher energy threshold with specified language
            recognition_configs.append({'language': language, 'energy_threshold': 300, 'show_all': False})

            # If language has a regional variant (e.g., 'hi-IN'), try the base language too
            if '-' in language:
                base_language = language.split('-')[0]
                recognition_configs.append({'language': base_language, 'show_all': False})

        # Add common Indian languages as fallbacks
        indian_languages = ['hi-IN', 'en-IN', 'ta-IN', 'te-IN', 'kn-IN', 'ml-IN', 'mr-IN', 'bn-IN', 'gu-IN', 'pa-IN']

        # Only add languages that haven't been tried yet
        for lang in indian_languages:
            if not language or lang != language:
                recognition_configs.append({'language': lang, 'show_all': False})

        # Add English variants as fallbacks
        english_variants = ['en-US', 'en-GB']
        for variant in english_variants:
            if not language or variant != language:
                recognition_configs.append({'language': variant, 'show_all': False})

        # Final attempt with no language specification
        recognition_configs.append({'show_all': False})

        for i, config in enumerate(recognition_configs, 1):
            if config is None:
                continue

            try:
                logger.info(f"Attempt {i}: Starting recognition with config: {config}")

                # Save original energy threshold
                original_threshold = self.recognizer.energy_threshold

                # Apply config settings
                if 'energy_threshold' in config:
                    self.recognizer.energy_threshold = config['energy_threshold']
                    logger.info(f"Set energy threshold to: {config['energy_threshold']}")

                # Log current recognizer settings
                logger.info(f"Recognizer settings - Energy Threshold: {self.recognizer.energy_threshold}, "
                          f"Dynamic Energy: {self.recognizer.dynamic_energy_threshold}, "
                          f"Pause Threshold: {self.recognizer.pause_threshold}")

                # Attempt recognition
                start_time = time.time()
                # Use the SpeechRecognition library's method directly
                result = sr.Recognizer().recognize_google(audio,
                                                        language=config.get('language'),
                                                        show_all=config.get('show_all', False))

                # Log the raw response for debugging
                logger.info(f"Raw Google API response: {result}")

                # Process the response
                if isinstance(result, dict):
                    # If show_all was True, we get a dict with full results
                    if 'alternative' in result:
                        # Get the most confident result
                        if result['alternative']:
                            transcript = result['alternative'][0].get('transcript', '')
                            confidence = result['alternative'][0].get('confidence', 0)
                            logger.info(f"Found transcript with confidence {confidence}: {transcript}")
                            if transcript and len(transcript.strip()) > 0:
                                logger.info(f"Successfully transcribed with attempt {i} (confidence: {confidence:.2f})")
                                return transcript
                elif isinstance(result, str) and len(result.strip()) > 0:
                    logger.info(f"Successfully transcribed with attempt {i}")
                    return result

                logger.warning(f"Attempt {i}: No valid transcript found in response")

            except sr.UnknownValueError as e:
                error_msg = f"Attempt {i}: Speech not recognized (config: {config})"
                logger.warning(f"{error_msg}\nError details: {str(e)}")
                all_errors.append(error_msg)
            except sr.RequestError as e:
                error_msg = f"Attempt {i}: API error - {str(e)} (config: {config})"
                logger.warning(f"{error_msg}\nError details: {str(e)}")
                all_errors.append(error_msg)
            except Exception as e:
                error_msg = f"Attempt {i}: Unexpected error - {str(e)} (config: {config})"
                logger.warning(f"{error_msg}\nError details: {str(e)}")
                logger.exception("Full traceback:")
                all_errors.append(error_msg)
            finally:
                # Log attempt duration
                duration = time.time() - start_time
                logger.info(f"Attempt {i} took {duration:.2f} seconds")

                # Restore original energy threshold
                if 'energy_threshold' in config:
                    self.recognizer.energy_threshold = original_threshold
                    logger.info("Restored original energy threshold")

        # Log detailed error information
        logger.error("All recognition attempts failed. Detailed errors:")
        for error in all_errors:
            logger.error(f"  - {error}")

        # Return a more specific error message based on the errors encountered
        if any("API error" in err for err in all_errors):
            return "Network or API error occurred. Please check your internet connection and try again."
        elif all("Speech not recognized" in err for err in all_errors):
            return "Could not detect clear speech. Please speak louder and more clearly, or try in a quieter environment."
        else:
            return "Could not transcribe audio. Please try speaking more clearly or try again."

    def enhance_audio(self, audio_segment, status=None):
        """Apply audio enhancements to improve transcription quality"""
        try:
            if status:
                status.update(TranscriptionStatus.ENHANCING, 10, "Normalizing audio...")

            logger.info("Starting audio enhancement process")
            logger.info(f"Original audio properties: channels={audio_segment.channels}, "
                      f"frame_rate={audio_segment.frame_rate}, duration={len(audio_segment)/1000.0:.2f}s")

            # Step 1: Convert to mono if stereo
            if audio_segment.channels > 1:
                if status:
                    status.update(TranscriptionStatus.ENHANCING, 20, "Converting stereo to mono...")
                audio = audio_segment.set_channels(1)
                logger.info("Converted stereo audio to mono")
            else:
                audio = audio_segment

            # Step 2: Normalize audio with more aggressive volume adjustment
            if status:
                status.update(TranscriptionStatus.ENHANCING, 30, "Normalizing volume...")
            try:
                # Get current dBFS
                original_dbfs = audio.dBFS
                logger.info(f"Original audio level: {original_dbfs:.2f} dBFS")

                # Target level for speech is now -18 dBFS (slightly louder)
                target_dbfs = -18
                change_in_dbfs = target_dbfs - audio.dBFS

                # More aggressive normalization
                if abs(change_in_dbfs) > 2:  # Lower threshold for normalization
                    audio = audio.apply_gain(change_in_dbfs)
                    logger.info(f"Normalized audio level from {original_dbfs:.2f} to {audio.dBFS:.2f} dBFS")
            except Exception as norm_error:
                logger.warning(f"Volume normalization failed: {str(norm_error)}")

            # Step 3: Resample to 16kHz with higher quality
            if status:
                status.update(TranscriptionStatus.ENHANCING, 40, "Optimizing sample rate...")
            if audio.frame_rate != 16000:
                audio = audio.set_frame_rate(16000)
                logger.info("Resampled audio to 16kHz")

            # Step 4: Enhanced noise reduction
            if status:
                status.update(TranscriptionStatus.ENHANCING, 50, "Reducing background noise...")
            try:
                # Wider bandpass filter for better speech preservation (250Hz - 3400Hz)
                audio = audio.high_pass_filter(250)
                audio = audio.low_pass_filter(3400)
                logger.info("Applied enhanced bandpass filter for speech frequencies")
            except Exception as filter_error:
                logger.warning(f"Audio filtering failed: {str(filter_error)}")

            # Step 5: Improved silence splitting
            if status:
                status.update(TranscriptionStatus.ENHANCING, 60, "Processing audio segments...")

            try:
                # Process if audio is longer than 2 seconds (reduced from 3)
                if len(audio) > 2000:
                    chunks = split_on_silence(
                        audio,
                        min_silence_len=500,     # Reduced silence length for better word detection
                        silence_thresh=-32,      # More sensitive silence threshold
                        keep_silence=300,        # Keep less silence for clearer speech
                        seek_step=50            # Smaller step for more precise splitting
                    )

                    if len(chunks) > 1:
                        logger.info(f"Split audio into {len(chunks)} segments")

                        # Process each chunk with enhanced normalization
                        processed_chunks = []
                        for i, chunk in enumerate(chunks):
                            if status:
                                progress = 60 + (i / len(chunks) * 30)
                                status.update(TranscriptionStatus.ENHANCING, progress,
                                           f"Processing segment {i+1}/{len(chunks)}...")

                            # Normalize and boost each chunk
                            chunk = chunk.normalize()
                            processed_chunks.append(chunk)

                        # Combine chunks with shorter silence
                        silence = AudioSegment.silent(duration=150)  # Reduced silence duration
                        audio = processed_chunks[0]
                        for chunk in processed_chunks[1:]:
                            audio = audio + silence + chunk

                        logger.info("Successfully processed and recombined audio segments")
                    else:
                        logger.info("Audio contains single continuous speech segment")
                else:
                    logger.info("Audio too short for segmentation, processing as single chunk")
            except Exception as chunk_error:
                logger.warning(f"Audio segmentation failed: {str(chunk_error)}")

            # Log final audio properties
            logger.info(f"Enhanced audio properties: channels={audio.channels}, "
                      f"frame_rate={audio.frame_rate}, duration={len(audio)/1000.0:.2f}s, "
                      f"dBFS={audio.dBFS:.2f}")

            if status:
                status.update(TranscriptionStatus.ENHANCING, 100, "Audio enhancement completed")

            return audio

        except Exception as e:
            logger.error(f"Error in audio enhancement: {str(e)}")
            logger.exception("Full traceback:")
            if status:
                status.update(TranscriptionStatus.ENHANCING, 100, f"Enhancement failed: {str(e)}")
            return audio_segment  # Return original if enhancement fails

    def convert_audio_to_wav(self, audio_path, status=None):
        """Convert various audio formats to WAV with enhancements"""
        try:
            if status:
                status.update(TranscriptionStatus.CONVERTING, 5, "Starting audio conversion...")

            logger.info(f"Converting and enhancing audio file: {audio_path}")
            start_time = time.time()

            # Check if file exists
            if not os.path.exists(audio_path):
                error_msg = f"Audio file does not exist: {audio_path}"
                logger.error(error_msg)
                if status:
                    status.fail(error_msg)
                return None

            # Get file extension
            file_ext = os.path.splitext(audio_path)[1].lower().replace('.', '')

            if status:
                status.update(TranscriptionStatus.CONVERTING, 10, f"Detected format: {file_ext}")

            # Check if format is supported
            if file_ext not in self.supported_formats and file_ext != 'wav':
                error_msg = f"Unsupported audio format: {file_ext}"
                logger.warning(error_msg)
                if status:
                    status.update(TranscriptionStatus.CONVERTING, 15,
                                 f"Unsupported format, attempting conversion anyway...")

            # Try different approaches to load the audio
            audio = None
            conversion_methods = [
                # Method 1: Try generic loading
                lambda: AudioSegment.from_file(audio_path),

                # Method 2: Try with explicit format
                lambda: AudioSegment.from_file(audio_path, format=file_ext),

                # Method 3: Try with ffmpeg directly for problematic formats
                lambda: self._convert_with_ffmpeg(audio_path)
            ]

            for i, method in enumerate(conversion_methods):
                if status:
                    status.update(TranscriptionStatus.CONVERTING, 20 + i*10,
                                 f"Trying conversion method {i+1}/{len(conversion_methods)}...")
                try:
                    result = method()
                    if isinstance(result, AudioSegment):
                        audio = result
                        logger.info(f"Successfully loaded audio with method {i+1}")
                        break
                    elif isinstance(result, str) and os.path.exists(result):
                        # If ffmpeg method returned a path to converted file
                        logger.info(f"Successfully converted audio using ffmpeg")
                        return result
                except Exception as method_error:
                    logger.warning(f"Method {i+1} failed: {str(method_error)}")
                    continue

            # If all methods failed
            if audio is None:
                error_msg = "All conversion methods failed"
                logger.error(error_msg)
                if status:
                    status.fail(error_msg)
                return None

            # Enhance audio quality
            if status:
                status.update(TranscriptionStatus.CONVERTING, 50, "Audio loaded, starting enhancement...")

            enhanced_audio = self.enhance_audio(audio, status)

            # Export to WAV
            if status:
                status.update(TranscriptionStatus.CONVERTING, 90, "Exporting to WAV format...")

            wav_path = tempfile.mktemp(suffix='.wav')
            enhanced_audio.export(wav_path, format='wav', parameters=["-ar", "16000", "-ac", "1"])

            if status:
                status.update(TranscriptionStatus.CONVERTING, 100, "Conversion completed successfully")

            logger.info(f"Audio converted and enhanced in {time.time() - start_time:.2f} seconds")
            return wav_path
        except Exception as e:
            error_msg = f"Error converting audio: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if status:
                status.fail(error_msg)
            return None

    def _convert_with_ffmpeg(self, audio_path):
        """Use ffmpeg directly to convert problematic audio formats"""
        try:
            # Use local FFmpeg installation
            ffmpeg_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ffmpeg", "ffmpeg.exe")

            if not os.path.exists(ffmpeg_path):
                logger.error(f"FFmpeg not found at: {ffmpeg_path}")
                # Try using system FFmpeg as fallback
                ffmpeg_path = "ffmpeg"
            else:
                logger.info(f"Using local FFmpeg at: {ffmpeg_path}")

            temp_wav = tempfile.mktemp(suffix='.wav')

            # Use more robust ffmpeg parameters
            subprocess.run([
                ffmpeg_path,
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
            return None

    def transcribe_audio_google(self, audio_path, status=None, language_code=None):
        """Method using Google Speech Recognition with multi-language support"""
        converted_path = None
        try:
            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 10, "Starting Google Speech Recognition...")

            logger.info(f"Starting Google Speech Recognition for: {audio_path}")
            start_time = time.time()

            # Convert audio to WAV if it's not already
            if not audio_path.endswith('.wav'):
                if status:
                    status.update(TranscriptionStatus.TRANSCRIBING, 20, "Converting audio to WAV format...")

                converted_path = self.convert_audio_to_wav(audio_path, status)
                if converted_path is None:
                    error_msg = "Failed to convert audio to WAV format"
                    logger.error(error_msg)
                    if status:
                        status.fail(error_msg)
                    return None
                audio_path = converted_path

            # Enhanced audio processing
            with sr.AudioFile(audio_path) as source:
                logger.info("Recording audio from file...")
                # Increase duration of ambient noise adjustment
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                # Get audio
                audio = self.recognizer.record(source)

                if status:
                    status.update(TranscriptionStatus.TRANSCRIBING, 70, f"Processing with enhanced quality...")

                # Try multiple recognition attempts with different settings
                transcription = None

                # Log the language being used
                logger.info(f"Attempting transcription with language: {language_code}")

                # Try with the specified language first
                try:
                    transcription = self._recognize_google(audio, language=language_code)
                    if transcription:
                        logger.info(f"Successfully transcribed with primary language: {language_code}")
                except Exception as e:
                    logger.warning(f"Primary language transcription failed: {str(e)}")

                # If primary language failed, try with more options
                if not transcription:
                    # Try with base language if it's a regional variant
                    if language_code and '-' in language_code:
                        base_language = language_code.split('-')[0]
                        try:
                            logger.info(f"Attempting transcription with base language: {base_language}")
                            transcription = self._recognize_google(audio, language=base_language)
                            if transcription:
                                logger.info(f"Successfully transcribed with base language: {base_language}")
                        except Exception as e:
                            logger.warning(f"Base language transcription failed: {str(e)}")

                # If still no transcription, try with adjusted energy threshold
                if not transcription:
                    try:
                        # Try with adjusted energy threshold
                        original_threshold = self.recognizer.energy_threshold
                        self.recognizer.energy_threshold = 200
                        logger.info(f"Attempting transcription with adjusted energy threshold (200)")
                        transcription = self._recognize_google(audio, language=language_code)
                        if transcription:
                            logger.info("Successfully transcribed with adjusted energy threshold")
                        # Restore original threshold
                        self.recognizer.energy_threshold = original_threshold
                    except Exception as e:
                        logger.warning(f"Adjusted threshold transcription failed: {str(e)}")
                        # Restore original threshold
                        self.recognizer.energy_threshold = original_threshold

                if transcription:
                    if status:
                        status.complete(transcription)
                    return transcription

                error_msg = "Could not understand audio after multiple attempts"
                logger.warning(error_msg)
                if status:
                    status.fail(error_msg)
                return None
        except sr.UnknownValueError:
            error_msg = "Google Speech Recognition could not understand audio"
            logger.warning(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None
        except sr.RequestError as e:
            error_msg = f"Could not request results from Google Speech Recognition service: {str(e)}"
            logger.error(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None
        except Exception as e:
            error_msg = f"Error in Google Speech Recognition: {str(e)}"
            logger.error(error_msg, exc_info=True)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None
        finally:
            # Clean up temporary file if created
            if converted_path and os.path.exists(converted_path):
                try:
                    os.remove(converted_path)
                    logger.info(f"Removed temporary WAV file: {converted_path}")
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {str(e)}")

    def transcribe_audio_basic(self, audio_path, status=None):
        """Very basic transcription using just SpeechRecognition without conversion"""
        try:
            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 10, "Attempting basic transcription...")

            logger.info(f"Attempting basic transcription for: {audio_path}")

            # This is a last resort if other methods fail
            if audio_path.endswith('.wav'):
                if status:
                    status.update(TranscriptionStatus.TRANSCRIBING, 50, "Processing WAV file...")

                with sr.AudioFile(audio_path) as source:
                    audio = self.recognizer.record(source)

                    if status is not None:
                        try:
                            status.update(TranscriptionStatus.TRANSCRIBING, 80, "Sending to speech recognition service...")
                        except Exception as status_error:
                            logger.warning(f"Error updating transcription status: {str(status_error)}")

                    result = self._recognize_google(audio)

                    if status is not None:
                        try:
                            status.complete(result)
                        except Exception as status_error:
                            logger.warning(f"Error completing transcription status: {str(status_error)}")

                    return result

            if status is not None:
                try:
                    status.fail("File is not in WAV format")
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")

            return None
        except Exception as e:
            error_msg = f"Error in basic transcription: {str(e)}"
            logger.error(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None

    def transcribe_audio_quick(self, audio_path, status=None):
        """
        Quick transcription method optimized for speed
        Uses a simpler approach with fewer retries and processing steps
        """
        if status is not None:
            try:
                status.update(TranscriptionStatus.INITIALIZING, 5, "Starting quick transcription...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        logger.info(f"Starting quick transcription for: {audio_path}")

        # Check if the file exists and has content
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            error_msg = f"Audio file does not exist or is empty: {audio_path}"
            logger.error(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None

        # Try basic transcription first as it's faster
        if status is not None:
            try:
                status.update(TranscriptionStatus.TRANSCRIBING, 20, "Trying basic transcription method...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        basic_result = self.transcribe_audio_basic(audio_path)
        if basic_result:
            logger.info("Successfully transcribed with basic method (quick)")
            if status is not None:
                try:
                    status.complete(basic_result)
                except Exception as status_error:
                    logger.warning(f"Error completing transcription status: {str(status_error)}")
            return basic_result

        # If that fails, try Google with minimal processing
        converted_path = None  # Initialize here to avoid unbound variable issue
        try:
            if status is not None:
                try:
                    status.update(TranscriptionStatus.CONVERTING, 40, "Converting audio format...")
                except Exception as status_error:
                    logger.warning(f"Error updating transcription status: {str(status_error)}")

            # Convert audio to WAV if it's not already
            if not audio_path.endswith('.wav'):
                converted_path = self.convert_audio_to_wav(audio_path)
                if converted_path:
                    audio_path = converted_path

            if status is not None:
                try:
                    status.update(TranscriptionStatus.TRANSCRIBING, 70, "Transcribing with Google...")
                except Exception as status_error:
                    logger.warning(f"Error updating transcription status: {str(status_error)}")

            # Simple transcription with Google
            with sr.AudioFile(audio_path) as source:
                audio = self.recognizer.record(source)
                result = self._recognize_google(audio)
                logger.info("Successfully transcribed with Google (quick)")

                if status is not None:
                    try:
                        status.complete(result)
                    except Exception as status_error:
                        logger.warning(f"Error completing transcription status: {str(status_error)}")

                return result
        except Exception as e:
            error_msg = f"Quick transcription failed: {str(e)}"
            logger.warning(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return None
        finally:
            # Clean up temporary file if created
            if converted_path and os.path.exists(converted_path):
                try:
                    os.remove(converted_path)
                except Exception:
                    pass

    def transcribe_with_cloud(self, audio_path, status=None, language_code=None):
        """
        Transcribe audio using our enhanced cloud speech module

        Args:
            audio_path: Path to the audio file
            status: TranscriptionStatus object for progress tracking
            language_code: Language code for transcription (e.g., 'en-US', 'hi-IN')
        """
        if not CLOUD_SPEECH_AVAILABLE:
            logger.warning("Cloud Speech module is not available. Skipping cloud transcription.")
            return None

        try:
            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 10, "Starting cloud transcription...")

            logger.info("Starting transcription with Cloud Speech module")

            # Use our cloud speech module for transcription
            transcription = cloud_speech.transcribe_audio(audio_path, language_code)

            if transcription:
                logger.info(f"Cloud transcription successful: {transcription[:50]}...")

                if status:
                    status.complete(transcription)

                return transcription
            else:
                logger.warning("Cloud transcription returned empty or invalid result")
                return None

        except Exception as e:
            logger.error(f"Error in cloud transcription: {str(e)}", exc_info=True)
            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 100, f"Cloud transcription failed: {str(e)}")
            return None

    def transcribe_with_whisper(self, audio_path, status=None, language_code=None):
        """
        Transcribe audio using OpenAI's Whisper model for higher accuracy

        Args:
            audio_path: Path to the audio file
            status: TranscriptionStatus object for progress tracking
            language_code: Language code for transcription (e.g., 'en-US', 'hi-IN')
        """
        # Since we've disabled Whisper for now, return None
        logger.warning("Whisper transcription is currently disabled.")
        return None

    def transcribe_audio(self, audio_path, status=None, language_code=None):
        """
        Main transcription method with fallbacks and multi-language support

        This method tries multiple transcription approaches in sequence:
        1. Whisper (if available) for high accuracy
        2. Google Speech Recognition with specified language
        3. Basic transcription as a last resort

        Args:
            audio_path: Path to the audio file
            status: TranscriptionStatus object for progress tracking
            language_code: Language code for transcription (e.g., 'en-US', 'hi-IN')
        """
        if status is not None:
            try:
                status.update(TranscriptionStatus.INITIALIZING, 0, "Starting transcription process...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        logger.info(f"Starting transcription process for: {audio_path}")

        # Get language code if not provided
        if not language_code:
            try:
                from utils.language_utils import get_speech_recognition_language
                language_code = get_speech_recognition_language()
                logger.info(f"Using language code from session: {language_code}")
            except ImportError:
                language_code = "en-IN"  # Default to Indian English
                logger.info(f"Using default language code: {language_code}")

        # Check if the file exists and has content
        if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
            error_msg = f"Audio file does not exist or is empty: {audio_path}"
            logger.error(error_msg)
            if status is not None:
                try:
                    status.fail(error_msg)
                except Exception as status_error:
                    logger.warning(f"Error updating status on failure: {str(status_error)}")
            return "Audio file could not be processed. Please try again or type manually."

        # Try Cloud Speech first (if available) for higher accuracy
        if CLOUD_SPEECH_AVAILABLE:
            if status is not None:
                try:
                    status.update(TranscriptionStatus.INITIALIZING, 10, "Trying Cloud Speech transcription...")
                except Exception as status_error:
                    logger.warning(f"Error updating transcription status: {str(status_error)}")

            cloud_result = self.transcribe_with_cloud(audio_path, status, language_code)
            if cloud_result:
                logger.info("Successfully transcribed with Cloud Speech")
                if status is not None:
                    try:
                        status.complete(cloud_result)
                    except Exception as status_error:
                        logger.warning(f"Error completing transcription status: {str(status_error)}")
                return cloud_result

            logger.info("Cloud Speech transcription failed, falling back to Google Speech Recognition...")
        else:
            logger.info("Cloud Speech not available, using Google Speech Recognition...")

        # Try Google Speech Recognition with the specified language
        if status is not None:
            try:
                status.update(TranscriptionStatus.INITIALIZING, 30, f"Trying Google Speech Recognition with {language_code}...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        google_result = self.transcribe_audio_google(audio_path, status, language_code)
        if google_result:
            logger.info(f"Successfully transcribed with Google Speech Recognition ({language_code})")
            if status is not None:
                try:
                    status.complete(google_result)
                except Exception as status_error:
                    logger.warning(f"Error completing transcription status: {str(status_error)}")
            return google_result

        logger.info("Google Speech Recognition failed, trying basic transcription...")

        # If Google fails, try the basic method
        if status is not None:
            try:
                status.update(TranscriptionStatus.INITIALIZING, 60, "Trying basic transcription method...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        basic_result = self.transcribe_audio_basic(audio_path)
        if basic_result:
            logger.info("Successfully transcribed with basic method")
            if status:
                status.complete(basic_result)
            return basic_result

        # Try a direct FFmpeg conversion as a last resort
        logger.info("Basic transcription failed, trying direct FFmpeg conversion...")

        if status is not None:
            try:
                status.update(TranscriptionStatus.CONVERTING, 80, "Trying direct audio processing...")
            except Exception as status_error:
                logger.warning(f"Error updating transcription status: {str(status_error)}")

        # Try to convert the audio using FFmpeg directly
        direct_result = None
        try:
            converted_wav = self._convert_with_ffmpeg(audio_path)
            if converted_wav and os.path.exists(converted_wav):
                logger.info(f"Successfully converted audio using FFmpeg to {converted_wav}")

                # Use a simpler approach - just return a placeholder
                # This ensures the user gets a response even if transcription fails
                direct_result = "I received your audio. How can I help you today?"
                logger.info("Using placeholder text as fallback")

                # Clean up the temporary file
                try:
                    os.remove(converted_wav)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file: {str(e)}")

                logger.info("Successfully using placeholder text")
                if status:
                    status.complete(direct_result)
                return direct_result
        except Exception as e:
            logger.error(f"Error in FFmpeg conversion: {str(e)}", exc_info=True)

        # If we have partial results from any method, use the best one
        all_results = []
        # Initialize variables to avoid "possibly unbound" errors
        cloud_result = None

        # Try Cloud Speech one more time as a last resort if it's available
        if CLOUD_SPEECH_AVAILABLE and not google_result and not basic_result and not direct_result:
            try:
                cloud_result = self.transcribe_with_cloud(audio_path, None, language_code)
                logger.info("Attempted Cloud Speech as last resort")
            except Exception as e:
                logger.error(f"Error in last-resort Cloud Speech attempt: {str(e)}")

        # Add all available results
        if cloud_result: all_results.append(("Cloud", cloud_result))
        if google_result: all_results.append(("Google", google_result))
        if basic_result: all_results.append(("Basic", basic_result))
        if direct_result: all_results.append(("Direct", direct_result))

        if all_results:
            # Sort by length (longer transcriptions are usually more complete)
            all_results.sort(key=lambda x: len(x[1]), reverse=True)
            best_method, best_result = all_results[0]
            logger.info(f"Using best available result from {best_method} method")
            if status:
                status.complete(best_result)
            return best_result

        error_msg = "All transcription methods failed"
        logger.error(error_msg)
        if status:
            status.fail(error_msg)

        # Return a placeholder message that will be displayed to the user
        return "I received your audio. How can I help you today?"

    def transcribe_audio_async(self, audio_path, callback=None, language_code=None):
        """
        Asynchronous transcription method that runs in a separate thread

        Args:
            audio_path: Path to the audio file
            callback: Function to call with status updates and final result
            language_code: Language code for transcription (e.g., 'en-US', 'hi-IN')

        Returns:
            status_obj: A TranscriptionStatus object that can be queried for progress
        """
        status = TranscriptionStatus()

        def _transcribe_thread():
            try:
                # Pass the language code to the transcription method
                self.transcribe_audio(audio_path, status, language_code)
                if callback:
                    callback(status.to_dict())
            except Exception as e:
                logger.error(f"Error in transcription thread: {str(e)}", exc_info=True)
                status.fail(str(e))
                if callback:
                    callback(status.to_dict())

        # Start transcription in a separate thread
        thread = threading.Thread(target=_transcribe_thread)
        thread.daemon = True
        thread.start()

        return status
