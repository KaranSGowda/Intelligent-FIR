
import json
import os
import base64
import time
import logging
from openai import OpenAI



# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai_client = None

def get_openai_client():
    """Return a lazily-initialized OpenAI client or None if unavailable."""
    global openai_client, OPENAI_API_KEY
    if openai_client is not None:
        return openai_client
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY is not set. AI features are disabled.")
        return None
    try:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        return openai_client
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        return None

# Settings for retry logic
MAX_RETRIES = 3
INITIAL_BACKOFF = 2  # seconds

def transcribe_audio(audio_file_path):
    """
    Transcribe audio file using OpenAI Whisper API
    """
    retry_count = 0

    client = get_openai_client()
    if client is None:
        return "Error: OpenAI API key not configured. Audio transcription unavailable."

    while retry_count < MAX_RETRIES:
        try:
            with open(audio_file_path, "rb") as audio_file:
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return response.text
        except Exception as e:
            error_msg = str(e)
            retry_count += 1

            # Check if it's a rate limit error
            if "429" in error_msg or "rate limit" in error_msg.lower():
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                time.sleep(wait_time)
            # If it's some other API error that might be transient
            elif "5" in error_msg[:3] or "timeout" in error_msg.lower():  # 5xx errors or timeouts
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    raise Exception(f"OpenAI API error: {error_msg}")

                time.sleep(wait_time)
            else:
                # If it's a different kind of error that won't be fixed by retrying
                logger.error(f"Error transcribing audio: {error_msg}")
                raise Exception(f"Failed to transcribe audio: {error_msg}")

def analyze_complaint(complaint_text):
    """
    Analyze complaint text to extract key details and determine urgency
    """
    retry_count = 0

    client = get_openai_client()
    if client is None:
        return {
            "incident_summary": "AI analysis unavailable. API key not configured.",
            "urgency_level": "normal",
            "incident_type": "unclassified",
            "key_entities": [],
            "recommended_action": "Manually review the complaint"
        }

    while retry_count < MAX_RETRIES:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a specialized legal assistant for police departments. Analyze the given complaint text and extract key details. Return a JSON object with the following fields:\n"
                                "- incident_summary: A concise summary of the incident\n"
                                "- urgency_level: Determine level of urgency (low, normal, high, critical)\n"
                                "- incident_type: The general category of the incident\n"
                                "- key_entities: Extract names of people, locations, and other entities mentioned\n"
                                "- recommended_action: Brief recommendation on immediate actions needed"
                    },
                    {"role": "user", "content": complaint_text}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            error_msg = str(e)
            retry_count += 1

            # Check if it's a rate limit error
            if "429" in error_msg or "rate limit" in error_msg.lower():
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    if "insufficient_quota" in error_msg:
                        # Special case for quota issues
                        logger.error("OpenAI API quota exceeded. Please check your billing details.")
                        return {
                            "incident_summary": "Unable to analyze due to API quota limits",
                            "urgency_level": "normal",  # Default to normal as a fallback
                            "incident_type": "unclassified",
                            "key_entities": [],
                            "recommended_action": "Manually review the complaint"
                        }
                    else:
                        raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                time.sleep(wait_time)
            # If it's some other API error that might be transient
            elif "5" in error_msg[:3] or "timeout" in error_msg.lower():  # 5xx errors or timeouts
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    # If we've exhausted our retries, return a basic response
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {error_msg}")
                    return {
                        "incident_summary": "Unable to analyze due to service unavailability",
                        "urgency_level": "normal",  # Default to normal as a fallback
                        "incident_type": "unclassified",
                        "key_entities": [],
                        "recommended_action": "Manually review the complaint"
                    }

                time.sleep(wait_time)
            else:
                # If it's a different kind of error that won't be fixed by retrying
                logger.error(f"Error analyzing complaint: {error_msg}")
                raise Exception(f"Failed to analyze complaint: {error_msg}")

def map_legal_sections(complaint_text):
    """
    Map complaint text to relevant Indian legal sections using ML and AI

    This function uses a hybrid approach:
    1. First tries the ML-based analyzer for faster and more reliable results
    2. Falls back to OpenAI GPT-4 if the ML analyzer fails or returns no results

    Returns a JSON object with sections and their relevance to the complaint
    """
    # Import here to avoid circular imports
    from utils.ml_analyzer import analyze_complaint as ml_analyze_complaint

    try:
        # First try the ML-based analyzer
        logger.info("Analyzing complaint using ML-based analyzer")
        ml_results = ml_analyze_complaint(complaint_text)

        # If ML analyzer returned results, use them
        if ml_results and ml_results.get("sections") and len(ml_results["sections"]) > 0:
            logger.info(f"ML analyzer found {len(ml_results['sections'])} relevant sections")
            return ml_results

        # If ML analyzer didn't return results, fall back to OpenAI
        logger.info("ML analyzer didn't find relevant sections, falling back to OpenAI")
    except Exception as ml_error:
        # If ML analyzer failed, log the error and fall back to OpenAI
        logger.error(f"ML analyzer error: {str(ml_error)}")
        logger.info("Falling back to OpenAI for legal section mapping")

    # OpenAI-based analysis as fallback
    retry_count = 0

    client = get_openai_client()
    if client is None:
        return {
            "sections": [
                {
                    "section_code": "N/A",
                    "section_name": "AI mapping unavailable - API key not configured",
                    "section_description": "The system could not analyze the complaint because the OpenAI API key is missing.",
                    "relevance": "Please manually review the complaint to identify applicable sections",
                    "confidence": 0
                }
            ]
        }

    while retry_count < MAX_RETRIES:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": """You are a legal expert specializing in Indian criminal law. Based on the complaint text, identify the relevant sections of the Indian Penal Code (IPC) that may apply.

Be very specific and accurate with the IPC section numbers. Focus on the most relevant sections (maximum 5) that directly apply to the complaint.

Return a JSON array with objects containing the following fields:
- section_code: The IPC section number (e.g., '302', '376', '420')
- section_name: The official name of the section
- section_description: Brief description of the section
- relevance: Brief explanation of how this section applies to the complaint
- confidence: A number between 0 and 1 indicating your confidence in this section's applicability

Example response format:
{
  "sections": [
    {
      "section_code": "302",
      "section_name": "Murder",
      "section_description": "Punishment for murder",
      "relevance": "The complaint describes an intentional killing with premeditation",
      "confidence": 0.95
    },
    {
      "section_code": "120B",
      "section_name": "Criminal Conspiracy",
      "section_description": "Punishment of criminal conspiracy",
      "relevance": "Multiple persons planned the crime together as evidenced by...",
      "confidence": 0.85
    }
  ]
}"""
                    },
                    {"role": "user", "content": complaint_text}
                ],
                response_format={"type": "json_object"}
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            error_msg = str(e)
            retry_count += 1

            # Check if it's a rate limit error
            if "429" in error_msg or "rate limit" in error_msg.lower():
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    if "insufficient_quota" in error_msg:
                        # Special case for quota issues
                        logger.error("OpenAI API quota exceeded. Please check your billing details.")
                        return {
                            "sections": [
                                {
                                    "section_code": "N/A",
                                    "section_name": "Unable to determine - API quota exceeded",
                                    "section_description": "The system could not analyze the complaint due to API quota limitations",
                                    "relevance": "Please manually review the complaint to identify applicable sections",
                                    "confidence": 0
                                }
                            ]
                        }
                    else:
                        raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                time.sleep(wait_time)
            # If it's some other API error that might be transient
            elif "5" in error_msg[:3] or "timeout" in error_msg.lower():  # 5xx errors or timeouts
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    # If we've exhausted our retries, return a fallback response
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {error_msg}")
                    return {
                        "sections": [
                            {
                                "section_code": "N/A",
                                "section_name": "Unable to determine - Service unavailable",
                                "section_description": "The system could not analyze the complaint due to service unavailability",
                                "relevance": "Please manually review the complaint to identify applicable sections",
                                "confidence": 0
                            }
                        ]
                    }

                time.sleep(wait_time)
            else:
                # If it's a different kind of error that won't be fixed by retrying
                logger.error(f"Error mapping legal sections: {error_msg}")
                raise Exception(f"Failed to map legal sections: {error_msg}")

def analyze_image(image_path):
    """
    Analyze image content using OpenAI Vision API

    Args:
        image_path: Path to the image file

    Returns:
        str: Analysis of the image content
    """
    # Encode image to base64
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Error reading image file: {str(e)}")
        return "Error: Unable to read the uploaded image file."

    retry_count = 0

    client = get_openai_client()
    if client is None:
        return "Error: OpenAI API key not configured. Image analysis unavailable."

    while retry_count < MAX_RETRIES:
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Analyze this image for evidence related to a criminal complaint. Describe key elements that may be relevant for a police investigation. Focus on people, objects, locations, and any details that might indicate a crime. Be specific and detailed in your analysis."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                            }
                        ]
                    }
                ],
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            retry_count += 1

            # Check if it's a rate limit error
            if "429" in error_msg or "rate limit" in error_msg.lower():
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))  # Exponential backoff
                logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    if "insufficient_quota" in error_msg:
                        # Special case for quota issues
                        logger.error("OpenAI API quota exceeded. Please check your billing details.")
                        return "Unable to analyze the image due to API quota limitations. Please manually review the image or try again later when quota is available."
                    else:
                        raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                time.sleep(wait_time)
            # If it's some other API error that might be transient
            elif "5" in error_msg[:3] or "timeout" in error_msg.lower():  # 5xx errors or timeouts
                wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                if retry_count >= MAX_RETRIES:
                    # If we've exhausted our retries, return a fallback response
                    logger.error(f"Failed after {MAX_RETRIES} attempts: {error_msg}")
                    return "Unable to analyze the image due to service unavailability. Please manually review the image or try again later."

                time.sleep(wait_time)
            else:
                # If it's a different kind of error that won't be fixed by retrying
                logger.error(f"Error analyzing image: {error_msg}")
                raise Exception(f"Failed to analyze image: {error_msg}")

def analyze_document(document_path):
    """
    Analyze document content using OpenAI API

    Args:
        document_path: Path to the document file

    Returns:
        str: Analysis of the document content
    """
    # For now, we'll just extract text from the document and analyze it
    # In a future version, we could use a document processing library to extract text
    # from PDFs, Word documents, etc.

    try:
        # Read the document as text (this is a simplified approach)
        with open(document_path, 'rb') as f:
            # Try to decode as UTF-8, but fall back to latin-1 if that fails
            try:
                document_text = f.read().decode('utf-8')
            except UnicodeDecodeError:
                # Reopen the file and try with latin-1 encoding
                f.seek(0)
                document_text = f.read().decode('latin-1')

        # Truncate if too long
        if len(document_text) > 10000:
            document_text = document_text[:10000] + "... [truncated]"

        retry_count = 0

        client = get_openai_client()
        if client is None:
            return "Error: OpenAI API key not configured. Document analysis unavailable."

        while retry_count < MAX_RETRIES:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a forensic document analyst. Analyze the provided document for evidence related to a criminal complaint. Focus on key information, dates, names, locations, and any details that might be relevant for a police investigation."
                        },
                        {"role": "user", "content": document_text}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                retry_count += 1

                # Handle errors (similar to analyze_image)
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                    if retry_count >= MAX_RETRIES:
                        if "insufficient_quota" in error_msg:
                            logger.error("OpenAI API quota exceeded. Please check your billing details.")
                            return "Unable to analyze the document due to API quota limitations. Please manually review the document or try again later when quota is available."
                        else:
                            raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                    time.sleep(wait_time)
                elif "5" in error_msg[:3] or "timeout" in error_msg.lower():
                    wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                    logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                    if retry_count >= MAX_RETRIES:
                        logger.error(f"Failed after {MAX_RETRIES} attempts: {error_msg}")
                        return "Unable to analyze the document due to service unavailability. Please manually review the document or try again later."

                    time.sleep(wait_time)
                else:
                    logger.error(f"Error analyzing document: {error_msg}")
                    raise Exception(f"Failed to analyze document: {error_msg}")
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        return f"Error: Unable to process the document. {str(e)}"



def analyze_audio(audio_path):
    """
    Analyze audio content using OpenAI API

    Args:
        audio_path: Path to the audio file

    Returns:
        str: Analysis of the audio content
    """
    try:
        # First try to transcribe the audio using OpenAI Whisper
        transcription = transcribe_audio(audio_path)



        if not transcription:
            return "Error: Unable to transcribe the audio file."

        # Then analyze the transcription
        retry_count = 0

        client = get_openai_client()
        if client is None:
            return "Error: OpenAI API key not configured. Audio analysis unavailable."

        while retry_count < MAX_RETRIES:
            try:
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a forensic audio analyst. Analyze the provided audio transcription for evidence related to a criminal complaint. Focus on key information, statements, names, locations, and any details that might be relevant for a police investigation."
                        },
                        {"role": "user", "content": f"Audio Transcription: {transcription}"}
                    ],
                    max_tokens=500
                )
                return response.choices[0].message.content
            except Exception as e:
                error_msg = str(e)
                retry_count += 1

                # Handle errors (similar to analyze_image)
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                    logger.warning(f"Rate limit exceeded. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                    if retry_count >= MAX_RETRIES:
                        if "insufficient_quota" in error_msg:
                            logger.error("OpenAI API quota exceeded. Please check your billing details.")
                            return "Unable to analyze the audio due to API quota limitations. Please manually review the transcription or try again later when quota is available."
                        else:
                            raise Exception("OpenAI API rate limit exceeded. Please try again later.")

                    time.sleep(wait_time)
                elif "5" in error_msg[:3] or "timeout" in error_msg.lower():
                    wait_time = INITIAL_BACKOFF * (2 ** (retry_count - 1))
                    logger.warning(f"API error: {error_msg}. Retrying in {wait_time} seconds. Attempt {retry_count}/{MAX_RETRIES}")

                    if retry_count >= MAX_RETRIES:
                        logger.error(f"Failed after {MAX_RETRIES} attempts: {error_msg}")
                        return "Unable to analyze the audio due to service unavailability. Please manually review the transcription or try again later."

                    time.sleep(wait_time)
                else:
                    logger.error(f"Error analyzing audio: {error_msg}")
                    raise Exception(f"Failed to analyze audio: {error_msg}")
    except Exception as e:
        logger.error(f"Error processing audio: {str(e)}")
        return f"Error: Unable to process the audio file. {str(e)}"
