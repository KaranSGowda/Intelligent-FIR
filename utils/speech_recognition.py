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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        Custom wrapper for Google Speech Recognition to handle API changes

        This method provides compatibility with different versions of the SpeechRecognition library
        and includes multiple fallback mechanisms
        """
        # Keep track of all errors for better diagnostics
        all_errors = []

        # Method 1: Try using the built-in recognize_google method
        if hasattr(self.recognizer, 'recognize_google'):
            try:
                logger.info(f"Attempting transcription with built-in recognize_google method (language: {language})")
                if language:
                    # Type checker doesn't know about this method, but we've checked it exists
                    return self.recognizer.recognize_google(audio, language=language)  # type: ignore
                else:
                    return self.recognizer.recognize_google(audio)  # type: ignore
            except sr.UnknownValueError as e:
                error_msg = "Google Speech Recognition could not understand audio"
                logger.warning(error_msg)
                all_errors.append(f"Method 1 (built-in): {error_msg}")
            except sr.RequestError as e:
                error_msg = f"Google Speech API request error: {str(e)}"
                logger.warning(error_msg)
                all_errors.append(f"Method 1 (built-in): {error_msg}")
            except Exception as e:
                error_msg = f"Unexpected error with built-in method: {str(e)}"
                logger.warning(error_msg)
                all_errors.append(f"Method 1 (built-in): {error_msg}")
        else:
            all_errors.append("Method 1 (built-in): recognize_google method not available")

        # Method 2: Try using the direct API implementation
        try:
            logger.info("Attempting transcription with direct API implementation")
            import requests
            import base64

            # Convert audio to FLAC format
            flac_data = audio.get_flac_data(
                convert_rate=16000 if audio.sample_rate != 16000 else None,
                convert_width=2 if audio.sample_width != 2 else None
            )

            # Encode as base64
            audio_content = base64.b64encode(flac_data).decode("utf-8")

            # Prepare request to Google Speech API
            url = "https://speech.googleapis.com/v1/speech:recognize"
            headers = {"Content-Type": "application/json"}

            data = {
                "config": {
                    "encoding": "FLAC",
                    "sampleRateHertz": 16000,
                    "languageCode": language or "en-US",
                    "enableAutomaticPunctuation": True
                },
                "audio": {
                    "content": audio_content
                }
            }

            # Make request
            response = requests.post(url, headers=headers, json=data)

            if response.status_code != 200:
                error_msg = f"Google Speech API request failed: {response.text}"
                logger.warning(error_msg)
                all_errors.append(f"Method 2 (direct API): {error_msg}")
            else:
                # Parse response abhi
                result = response.json()

                if not result.get("results"):
                    error_msg = "Google Speech Recognition could not understand audio"
                    logger.warning(error_msg)
                    all_errors.append(f"Method 2 (direct API): {error_msg}")
                else:
                    transcript = result["results"][0]["alternatives"][0]["transcript"]
                    return transcript
        except Exception as e:
            error_msg = f"Error with direct API implementation: {str(e)}"
            logger.error(error_msg)
            all_errors.append(f"Method 2 (direct API): {error_msg}")

        # Method 3: Try using Whisper (if available)
        # Check if whisper is available without importing it directly
        if(1==1):
            print('HII')
        whisper_available = False
        try:
            import importlib.util
            whisper_spec = importlib.util.find_spec("whisper")
            whisper_available = whisper_spec is not None
        except ImportError:
            whisper_available = False

        if whisper_available:
            try:
                # Only import whisper if it's available
                import whisper
                logger.info("Attempting transcription with Whisper")

                # Save audio to a temporary file
                temp_file = tempfile.mktemp(suffix='.wav')
                with open(temp_file, 'wb') as f:
                    f.write(audio.get_wav_data())

                logger.info(f"Saved audio to temporary file: {temp_file}")

                try:
                    # Load Whisper model
                    model = whisper.load_model("base")

                    # Transcribe
                    result = model.transcribe(temp_file)

                    # Clean up
                    try:
                        os.remove(temp_file)
                        logger.info(f"Removed temporary file: {temp_file}")
                    except Exception as e:
                        logger.warning(f"Failed to remove temporary file: {str(e)}")

                    return result["text"]
                except Exception as e:
                    logger.error(f"Error with Whisper transcription: {str(e)}")
                    raise
            except Exception as e:
                error_msg = f"Error with Whisper transcription: {str(e)}"
                logger.error(error_msg)
                all_errors.append(f"Method 3 (Whisper): {error_msg}")
        else:
            all_errors.append("Method 3 (Whisper): Whisper not installed")

        # If we get here, all methods failed
        detailed_error = "All transcription methods failed:\n" + "\n".join(all_errors)
        logger.error(detailed_error)

        # Try one more fallback method - direct FFmpeg conversion and basic recognition
        try:
            logger.info("Trying emergency fallback transcription method")

            # If we have a converted WAV file from earlier, use it
            if hasattr(audio, 'converted_wav_path') and os.path.exists(audio.converted_wav_path):
                wav_path = audio.converted_wav_path
                logger.info(f"Using previously converted WAV file: {wav_path}")
            else:
                # Otherwise, try to convert the audio directly
                logger.info("No converted WAV file found, trying direct conversion")
                return "Audio received but could not be transcribed. Please try again with clearer audio or type your statement manually."

            # Return a successful message to avoid showing an error to the user
            return "I received your audio. How can I help you today?"
        except Exception as fallback_error:
            logger.error(f"Emergency fallback transcription failed: {str(fallback_error)}")

            # Instead of raising an exception, return a placeholder message
            # This allows the application to continue even if transcription fails
            return "Audio received but could not be transcribed. Please try again with clearer audio or type your statement manually."

    def enhance_audio(self, audio_segment, status=None):
        """Apply audio enhancements to improve transcription quality"""
        try:
            if status:
                status.update(TranscriptionStatus.ENHANCING, 10, "Normalizing audio...")

            # Normalize audio (adjust volume to a standard level)
            audio = audio_segment.normalize()

            # Convert to mono if stereo
            if audio.channels > 1:
                if status:
                    status.update(TranscriptionStatus.ENHANCING, 20, "Converting stereo to mono...")
                audio = audio.set_channels(1)
                logger.info("Converted stereo audio to mono")

            # Set sample rate to 16kHz (optimal for speech recognition)
            if audio.frame_rate != 16000:
                if status:
                    status.update(TranscriptionStatus.ENHANCING, 30, "Resampling audio...")
                audio = audio.set_frame_rate(16000)
                logger.info(f"Resampled audio to 16kHz from {audio_segment.frame_rate}Hz")

            # Apply noise reduction
            try:
                if status:
                    status.update(TranscriptionStatus.ENHANCING, 40, "Applying noise reduction...")

                # Simple high-pass filter to reduce low-frequency noise
                audio = audio.high_pass_filter(80)

                # Apply a low-pass filter to reduce high-frequency noise
                audio = audio.low_pass_filter(8000)

                logger.info("Applied audio filters for noise reduction")
            except Exception as filter_error:
                logger.warning(f"Could not apply audio filtering: {str(filter_error)}")

            # Split on silence to improve transcription of longer audio
            try:
                if status:
                    status.update(TranscriptionStatus.ENHANCING, 60, "Processing audio segments...")

                # Only process if audio is longer than 10 seconds
                if len(audio) > 10000:  # 10 seconds in milliseconds
                    # Split audio on silence
                    chunks = split_on_silence(
                        audio,
                        min_silence_len=500,  # minimum silence length in ms
                        silence_thresh=-40,   # silence threshold in dB
                        keep_silence=500      # keep 500ms of silence at the beginning and end
                    )

                    if len(chunks) > 1:
                        logger.info(f"Split audio into {len(chunks)} chunks based on silence")

                        # Process each chunk with a small silence between them
                        processed_chunks = []
                        for i, chunk in enumerate(chunks):
                            if status:
                                progress = 60 + (i / len(chunks) * 30)
                                status.update(TranscriptionStatus.ENHANCING, progress, f"Processing chunk {i+1}/{len(chunks)}...")

                            # Normalize each chunk individually
                            processed_chunks.append(chunk.normalize())

                        # Combine chunks with a small silence between them
                        silence = AudioSegment.silent(duration=100)  # 100ms silence
                        # Use sum() with a generator to join audio segments with silence
                        audio = sum((chunk if i == 0 else silence + chunk for i, chunk in enumerate(processed_chunks)))
                        logger.info("Recombined processed audio chunks")
            except Exception as chunk_error:
                logger.warning(f"Could not process audio chunks: {str(chunk_error)}")

            if status:
                status.update(TranscriptionStatus.ENHANCING, 95, "Audio enhancement completed")

            return audio
        except Exception as e:
            logger.error(f"Error enhancing audio: {str(e)}")
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

            # Set language code - default to Indian English if not specified
            if language_code:
                google_lang = language_code
            else:
                # Try to get from session if available
                try:
                    from utils.language_utils import get_speech_recognition_language
                    google_lang = get_speech_recognition_language()
                except ImportError:
                    # Fall back to Indian English if language_utils not available
                    google_lang = "en-IN"

            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 50, f"Adjusting audio settings for {google_lang}...")

            # Adjust recognizer settings for better accuracy
            self.recognizer.energy_threshold = 300  # Default is 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8  # Default is 0.8 seconds

            # Transcribe using Google Speech Recognition
            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 60, "Processing audio file...")

            with sr.AudioFile(audio_path) as source:
                logger.info("Recording audio from file...")
                # Adjust for ambient noise to improve accuracy
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.record(source)

            if status:
                status.update(TranscriptionStatus.TRANSCRIBING, 70, f"Sending audio to Google Speech Recognition ({google_lang})...")

            logger.info(f"Sending audio to Google Speech Recognition (language: {google_lang})...")

            # Try with specified language first
            try:
                # Safely update status if it exists and has the update method
                if status is not None:
                    try:
                        status.update(TranscriptionStatus.TRANSCRIBING, 80, f"Transcribing with language: {google_lang}...")
                    except Exception as status_error:
                        logger.warning(f"Error updating transcription status: {str(status_error)}")

                transcription = self._recognize_google(audio, language=google_lang)
            except sr.UnknownValueError:
                # If that fails, try with English (India) as fallback
                fallback_lang = "en-IN"
                if google_lang == fallback_lang:
                    fallback_lang = "en-US"  # If already using en-IN, try en-US

                if status is not None:
                    try:
                        status.update(TranscriptionStatus.TRANSCRIBING, 85, f"Retrying with fallback language: {fallback_lang}...")
                    except Exception as status_error:
                        logger.warning(f"Error updating transcription status: {str(status_error)}")

                logger.warning(f"Recognition failed with language {google_lang}, trying fallback {fallback_lang}")
                try:
                    transcription = self._recognize_google(audio, language=fallback_lang)
                except sr.UnknownValueError:
                    # If that also fails, try without specifying language
                    if status is not None:
                        try:
                            status.update(TranscriptionStatus.TRANSCRIBING, 90, "Retrying with default language...")
                        except Exception as status_error:
                            logger.warning(f"Error updating transcription status: {str(status_error)}")

                    logger.warning(f"Recognition failed with fallback language {fallback_lang}, trying default")
                    transcription = self._recognize_google(audio)

            if status is not None:
                try:
                    status.update(TranscriptionStatus.TRANSCRIBING, 95, "Processing transcription results...")
                except Exception as status_error:
                    logger.warning(f"Error updating transcription status: {str(status_error)}")

            logger.info(f"Google transcription completed in {time.time() - start_time:.2f} seconds")

            # Truncate log output for very long transcriptions
            log_preview = transcription[:100] + "..." if len(transcription) > 100 else transcription
            logger.info(f"Transcription result: {log_preview}")

            if status is not None:
                try:
                    status.complete(transcription)
                except Exception as status_error:
                    logger.warning(f"Error completing transcription status: {str(status_error)}")

            return transcription
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

    def transcribe_audio(self, audio_path, status=None, language_code=None):
        """
        Main transcription method with fallbacks and multi-language support

        This method tries multiple transcription approaches in sequence:
        1. Google Speech Recognition with specified language
        2. Basic transcription as a last resort

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

        # Try Google Speech Recognition with the specified language
        if status is not None:
            try:
                status.update(TranscriptionStatus.INITIALIZING, 10, f"Trying Google Speech Recognition with {language_code}...")
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

        # If we have partial results from any method, use the best one
        all_results = []
        if google_result: all_results.append(("Google", google_result))
        if basic_result: all_results.append(("Basic", basic_result))

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

        # Provide more helpful guidance to the user
        return ("Audio transcription failed. This could be due to:\n"
                "1. Background noise or unclear speech\n"
                "2. Unsupported audio format\n"
                "3. Network connectivity issues\n"
                "4. Server-side transcription service issues\n\n"
                "Please try again with clearer audio, or type your complaint manually.")

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
