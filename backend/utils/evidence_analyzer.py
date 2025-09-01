#utils/evidence_analyzer.py
import os
import logging
import datetime
from PIL import Image, ExifTags
import hashlib
import mimetypes

# Configure logging first to ensure logger is available
logger = logging.getLogger(__name__)



# Define constants
EVIDENCE_TYPES = ['image', 'document', 'video', 'audio', 'other']
CATEGORIES = ['Physical Evidence', 'Digital Evidence', 'Documentary Evidence', 'Testimonial Evidence', 'Other Evidence']

def get_file_type(file_path):
    """
    Determine the type of file based on its MIME type

    Args:
        file_path: Path to the file

    Returns:
        str: One of the EVIDENCE_TYPES
    """
    try:
        # Try to use python-magic if available
        try:
            import magic
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(file_path)
            logger.debug(f"Using python-magic to determine file type: {mime_type}")
        except (ImportError, AttributeError, TypeError) as e:
            logger.debug(f"python-magic not available or error: {str(e)}")
            # Use mimetypes as fallback
            mime_type, _ = mimetypes.guess_type(file_path)
            logger.debug(f"Using mimetypes to determine file type: {mime_type}")

            if mime_type is None:
                # If mimetypes can't determine the type, use file extension
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
                    mime_type = 'image/jpeg'  # Default to image/jpeg for image files
                elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv']:
                    mime_type = 'video/mp4'  # Default to video/mp4 for video files
                elif ext in ['.mp3', '.wav', '.ogg', '.flac', '.aac']:
                    mime_type = 'audio/mp3'  # Default to audio/mp3 for audio files
                elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf']:
                    mime_type = 'application/pdf'  # Default to application/pdf for document files
                else:
                    mime_type = 'application/octet-stream'  # Default to binary for unknown types
                logger.debug(f"Using file extension to determine file type: {mime_type}")

        if mime_type and mime_type.startswith('image/'):
            return 'image'
        elif mime_type and mime_type.startswith('video/'):
            return 'video'
        elif mime_type and mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type and (mime_type in ['application/pdf', 'application/msword',
                          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                          'text/plain', 'application/rtf']):
            return 'document'
        else:
            return 'other'
    except Exception as e:
        logger.error(f"Error determining file type: {str(e)}")
        return 'other'

def extract_metadata(file_path):
    """
    Extract metadata from a file

    Args:
        file_path: Path to the file

    Returns:
        dict: Metadata information
    """
    try:
        # Basic file info
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        file_extension = os.path.splitext(file_name)[1].lower()
        last_modified = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

        # Calculate file hash
        file_hash = calculate_file_hash(file_path)

        metadata = {
            'file_name': file_name,
            'file_size': file_size,
            'file_extension': file_extension,
            'last_modified': last_modified,
            'hash': file_hash
        }

        # Extract specific metadata based on file type
        file_type = get_file_type(file_path)

        if file_type == 'image':
            try:
                image_metadata = extract_image_metadata(file_path)
                metadata.update(image_metadata)
            except Exception as e:
                logger.error(f"Error extracting image metadata: {str(e)}")

        return metadata
    except Exception as e:
        logger.error(f"Error extracting metadata: {str(e)}")
        return {}

def extract_image_metadata(file_path):
    """
    Extract metadata from an image file

    Args:
        file_path: Path to the image file

    Returns:
        dict: Image metadata
    """
    try:
        with Image.open(file_path) as img:
            # Get dimensions
            width, height = img.size

            metadata = {
                'dimensions': {
                    'width': width,
                    'height': height
                },
                'format': img.format,
                'mode': img.mode
            }

            # Extract EXIF data if available
            exif = {}

            # Try to get EXIF data using modern methods
            try:
                # For newer Pillow versions
                exif_info = None
                try:
                    # First try the modern getexif() method
                    exif_info = img.getexif()
                except (AttributeError, TypeError):
                    # If that fails, we'll just use an empty dict
                    pass

                if exif_info:
                    # Convert to a more usable dictionary with tag names
                    for tag_id, value in exif_info.items():
                        if tag_id in ExifTags.TAGS:
                            exif[ExifTags.TAGS[tag_id]] = value
            except Exception as exif_err:
                logger.warning(f"Error extracting EXIF data: {str(exif_err)}")

                # Convert binary data to string representation
                for key, value in exif.items():
                    if isinstance(value, bytes):
                        try:
                            exif[key] = value.decode('utf-8', errors='replace')
                        except:
                            exif[key] = str(value)

                metadata['exif'] = exif

                # Extract GPS data if available
                if 'GPSInfo' in exif:
                    gps_info = exif['GPSInfo']
                    try:
                        gps_data = extract_gps_data(gps_info)
                        if gps_data:
                            metadata['gps'] = gps_data
                    except Exception as e:
                        logger.error(f"Error extracting GPS data: {str(e)}")

            return metadata
    except Exception as e:
        logger.error(f"Error extracting image metadata: {str(e)}")
        return {}

def extract_gps_data(gps_info):
    """
    Extract GPS data from EXIF GPS info

    Args:
        gps_info: EXIF GPS info

    Returns:
        dict: GPS data
    """
    try:
        # Convert GPS coordinates to decimal degrees
        if 1 in gps_info and 2 in gps_info and 3 in gps_info and 4 in gps_info:
            lat_ref = gps_info.get(1, 'N')
            lat = gps_info.get(2, (0, 0, 0))
            lon_ref = gps_info.get(3, 'E')
            lon = gps_info.get(4, (0, 0, 0))

            # Convert degrees, minutes, seconds to decimal degrees
            lat_value = lat[0] + lat[1]/60 + lat[2]/3600
            if lat_ref == 'S':
                lat_value = -lat_value

            lon_value = lon[0] + lon[1]/60 + lon[2]/3600
            if lon_ref == 'W':
                lon_value = -lon_value

            return {
                'latitude': lat_value,
                'longitude': lon_value
            }
        return None
    except Exception as e:
        logger.error(f"Error extracting GPS data: {str(e)}")
        return None

def calculate_file_hash(file_path):
    """
    Calculate SHA-256 hash of a file

    Args:
        file_path: Path to the file

    Returns:
        str: SHA-256 hash
    """
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            # Read and update hash in chunks of 4K
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        logger.error(f"Error calculating file hash: {str(e)}")
        return ""

def analyze_evidence(file_path, file_type):
    """
    Analyze evidence file and return analysis results

    Args:
        file_path: Path to the evidence file
        file_type: Type of the evidence file

    Returns:
        dict: Analysis results
    """
    try:
        # Basic analysis
        analysis = {
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis_text': f"Automatic analysis of {file_type} evidence.",
            'tags': []
        }

        # Specific analysis based on file type
        if file_type == 'image':
            image_analysis = analyze_image(file_path)
            analysis.update(image_analysis)
        elif file_type == 'document':
            document_analysis = analyze_document(file_path)
            analysis.update(document_analysis)
        elif file_type == 'video':
            video_analysis = analyze_video(file_path)
            analysis.update(video_analysis)
        elif file_type == 'audio':
            audio_analysis = analyze_audio(file_path)
            analysis.update(audio_analysis)

        return analysis
    except Exception as e:
        logger.error(f"Error analyzing evidence: {str(e)}")
        return {
            'timestamp': datetime.datetime.now().isoformat(),
            'analysis_text': f"Error analyzing evidence: {str(e)}",
            'tags': []
        }

def analyze_image(_):
    """
    Analyze an image file

    Args:
        _: Path to the image file (not used in this implementation)

    Returns:
        dict: Analysis results
    """
    try:
        # In a real system, this would use computer vision APIs
        # For now, we'll return a simple analysis
        # Note: file_path is not used in this simplified implementation
        # but would be used in a real implementation to analyze the image
        return {
            'analysis_text': "This is an image file. In a production system, this would be analyzed using computer vision to identify objects, people, text, etc.",
            'tags': ['image', 'visual evidence']
        }
    except Exception as e:
        logger.error(f"Error analyzing image: {str(e)}")
        return {
            'analysis_text': f"Error analyzing image: {str(e)}",
            'tags': ['image']
        }

def analyze_document(_):
    """
    Analyze a document file

    Args:
        _: Path to the document file (not used in this implementation)

    Returns:
        dict: Analysis results
    """
    try:
        # In a real system, this would use text extraction and NLP
        # For now, we'll return a simple analysis
        # Note: file_path is not used in this simplified implementation
        # but would be used in a real implementation to analyze the document
        return {
            'analysis_text': "This is a document file. In a production system, this would be analyzed using text extraction and NLP to identify key information.",
            'tags': ['document', 'textual evidence']
        }
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return {
            'analysis_text': f"Error analyzing document: {str(e)}",
            'tags': ['document']
        }

def analyze_video(_):
    """
    Analyze a video file

    Args:
        _: Path to the video file (not used in this implementation)

    Returns:
        dict: Analysis results
    """
    try:
        # In a real system, this would use video analysis APIs
        # For now, we'll return a simple analysis
        # Note: file_path is not used in this simplified implementation
        # but would be used in a real implementation to analyze the video
        return {
            'analysis_text': "This is a video file. In a production system, this would be analyzed using video analysis to identify scenes, objects, people, etc.",
            'tags': ['video', 'visual evidence', 'temporal evidence']
        }
    except Exception as e:
        logger.error(f"Error analyzing video: {str(e)}")
        return {
            'analysis_text': f"Error analyzing video: {str(e)}",
            'tags': ['video']
        }

def analyze_audio(_):
    """
    Analyze an audio file

    Args:
        _: Path to the audio file (not used in this implementation)

    Returns:
        dict: Analysis results
    """
    try:
        # In a real system, this would use audio analysis
        # For now, we'll return a simple analysis
        # Note: file_path is not used in this simplified implementation
        # but would be used in a real implementation to analyze the audio
        return {
            'analysis_text': "This is an audio file. In a production system, this would be analyzed using audio analysis to transcribe and identify speakers.",
            'tags': ['audio', 'auditory evidence']
        }
    except Exception as e:
        logger.error(f"Error analyzing audio: {str(e)}")
        return {
            'analysis_text': f"Error analyzing audio: {str(e)}",
            'tags': ['audio']
        }

def suggest_evidence_category(file_type):
    """
    Suggest a category for evidence based on file type

    Args:
        file_type: Type of the evidence file

    Returns:
        str: Suggested category
    """
    if file_type in ['image', 'video', 'audio']:
        return 'Digital Evidence'
    elif file_type == 'document':
        return 'Documentary Evidence'
    else:
        return 'Other Evidence'