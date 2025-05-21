"""
Chatbot utility for the Intelligent FIR System.
This module provides functionality to answer user queries about cases and IPC sections.
"""

import json
import logging
import re
from datetime import datetime
from extensions import db
from models import FIR, User, LegalSection
# Try to import ML analyzer, but handle the case when it's not available
try:
    from utils.ml_analyzer import analyze_complaint
    ML_ANALYZER_AVAILABLE = True
except ImportError:
    ML_ANALYZER_AVAILABLE = False
    # Define a fallback function
    def analyze_complaint(text):
        return {
            "sections": [
                {
                    "section_code": "N/A",
                    "section_name": "ML Analyzer Not Available",
                    "section_description": "The ML analyzer is not available. Please install the required packages.",
                    "relevance": "Please consult with a legal professional for accurate analysis.",
                    "confidence": 0
                }
            ]
        }

# Configure logging
logger = logging.getLogger(__name__)

class FIRChatbot:
    """
    Chatbot for handling FIR-related queries.
    """

    def __init__(self):
        """Initialize the chatbot with common patterns and responses."""
        # Define common query patterns
        self.patterns = {
            'case_status': [
                r'status of (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'what is the status of (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'where is (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'update on (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)'
            ],
            'case_details': [
                r'details of (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'information about (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'tell me about (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)'
            ],
            'legal_sections': [
                r'what (?:are|is) the (?:legal sections|ipc sections|sections) for (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'legal sections in (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)',
                r'ipc sections in (?:my|the) (?:case|fir)(?: number)? ?([a-zA-Z0-9]+)'
            ],
            'section_info': [
                r'what is (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$',
                r'tell me about (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$',
                r'information about (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$',
                r'explain (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$',
                r'^(?:section|ipc) section ([0-9A-Za-z]+)$',
                r'details of (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$',
                r'what does (?:section|ipc)(?: section)? ([0-9A-Za-z]+) (?:mean|say|state)',
                r'meaning of (?:section|ipc)(?: section)? ([0-9A-Za-z]+)$'
            ],
            'analyze_complaint': [
                r'analyze (?:this|my) complaint[:\s]+(.*)',
                r'what sections apply to[:\s]+(.*)',
                r'which ipc sections apply to[:\s]+(.*)',
                r'legal sections for[:\s]+(.*)',
                r'(?:my|the) case (?:is|involves|about)[:\s]+(.*)',
                r'(?:someone|a person) (?:stole|took|robbed|attacked|assaulted|threatened|killed|murdered|raped|cheated|defrauded|harassed)(.*)',
                r'(?:i|we|my|our) (?:was|were|have been|has been) (?:robbed|attacked|assaulted|threatened|defrauded|harassed|cheated)(.*)',
                r'(?:there was|there has been) (?:a|an) (?:theft|robbery|assault|attack|murder|rape|fraud|harassment|accident|incident)(.*)'
            ],
            'list_sections': [
                r'(?:list|show|tell me about|what are)(?: the)? (?:common|popular|important|all) (?:ipc|indian penal code) sections$',
                r'(?:list|show|tell me)(?: the)? (?:ipc|indian penal code) sections$',
                r'(?:what|which) (?:ipc|indian penal code) sections (?:are there|exist|are available)$',
                r'(?:give me|show me) (?:a list of|some) (?:ipc|indian penal code) sections$'
            ]
        }

        # Generic responses
        self.generic_responses = [
            "I'm here to help with information about your FIR and legal sections. You can ask about case status, details, specific IPC sections, or describe a case for legal analysis.",
            "I don't understand that query. You can ask about case status, case details, information about specific IPC sections, or describe a situation to get relevant IPC sections.",
            "Please provide a valid FIR number to get information about your case.",
            "You can ask questions like 'What is the status of my case FIR20230101123456?', 'What is IPC section 302?', or 'Someone stole my phone yesterday, which sections apply?'"
        ]

    def process_query(self, query, user_id=None):
        """
        Process a user query and return a response.

        Args:
            query: The user's query text
            user_id: The ID of the user making the query (for access control)

        Returns:
            dict: A response object with text and any additional data
        """
        if not query:
            return self._create_response("Please ask a question about your case or IPC sections.")

        query = query.strip().lower()

        # Log the query for debugging
        logger.info(f"Processing query: {query}")
        logger.info(f"Query type: {type(query)}")
        logger.info(f"Query length: {len(query)}")

        # Check for greetings
        if self._is_greeting(query):
            return self._create_response("Hello! I'm your FIR assistant. How can I help you today?")

        # Check for direct IPC section queries (e.g., "1", "76", "302", "IPC 376")
        # This is a common way users might ask about sections
        ipc_direct_match = re.match(r'^(?:ipc\s*)?([0-9]{1,3}[A-Za-z]?|[0-9]{1,3})$', query)
        if ipc_direct_match:
            section_code = ipc_direct_match.group(1)
            logger.info(f"Direct IPC section query detected: {section_code}")
            return self._get_section_info(section_code)

        # Check for "IPC section X" format
        ipc_section_match = re.match(r'^(?:ipc|indian penal code)?\s*section\s*([0-9]{1,3}[A-Za-z]?)$', query)
        if ipc_section_match:
            section_code = ipc_section_match.group(1)
            logger.info(f"IPC section query detected: {section_code}")
            return self._get_section_info(section_code)

        # Try to match the query against known patterns
        logger.info("Trying to match query against patterns")
        for intent, patterns in self.patterns.items():
            logger.info(f"Checking intent: {intent} with {len(patterns)} patterns")
            for pattern in patterns:
                logger.info(f"Trying pattern: {pattern}")
                match = re.search(pattern, query, re.IGNORECASE)
                if match:
                    logger.info(f"Pattern matched: {pattern} for intent: {intent}")
                    logger.info(f"Match groups: {match.groups()}")

                    # Check if this is a list_sections intent (which doesn't have a capture group)
                    if intent == 'list_sections':
                        logger.info("List sections intent matched")
                        return self._list_common_sections()

                    # For other intents, extract the captured group
                    try:
                        captured_value = match.group(1)
                        logger.info(f"Captured value: {captured_value}")

                        if intent == 'case_status':
                            return self._get_case_status(captured_value, user_id)
                        elif intent == 'case_details':
                            return self._get_case_details(captured_value, user_id)
                        elif intent == 'legal_sections':
                            return self._get_case_legal_sections(captured_value, user_id)
                        elif intent == 'section_info':
                            # Special handling for IPC section queries
                            # If the query is like "what is ipc section 302", we need to extract just "302"
                            if captured_value.lower().startswith('section'):
                                # Extract the number after "section"
                                section_match = re.search(r'section\s+([0-9A-Za-z]+)', captured_value, re.IGNORECASE)
                                if section_match:
                                    captured_value = section_match.group(1)
                                    logger.info(f"Extracted section number: {captured_value}")

                            return self._get_section_info(captured_value)
                        elif intent == 'analyze_complaint':
                            return self._analyze_complaint_text(captured_value)
                    except IndexError:
                        logger.error(f"No capture group found for pattern: {pattern}")
                        if intent == 'list_sections':
                            return self._list_common_sections()
                        else:
                            return self._create_response("I'm sorry, I couldn't understand your query. Please try again with a different wording.")

        # If no pattern matches, check for keywords
        if 'help' in query or 'assist' in query:
            return self._create_response(
                "I can help you with the following:\n\n"
                "1️⃣ Check the status of your FIR\n   Example: 'What is the status of my case FIR20230101123456?'\n\n"
                "2️⃣ Get details about your case\n   Example: 'Tell me about my case FIR20230101123456'\n\n"
                "3️⃣ Get information about IPC sections\n   Example: 'What is IPC section 302?'\n\n"
                "4️⃣ Analyze a case description to find applicable IPC sections\n   Examples:\n"
                "   - 'Analyze this complaint: My phone was stolen yesterday'\n"
                "   - 'Someone broke into my house and stole valuables'\n"
                "   - 'My case is about being threatened by my neighbor'\n"
                "   - 'I was assaulted by a group of people yesterday'\n\n"
                "Just describe your situation, and I'll identify which IPC sections might apply!"
            )

        # Check for IPC-related keywords
        if 'ipc' in query or 'section' in query or 'penal code' in query:
            # Extract potential section numbers - allow for 1-3 digits followed by optional letter
            section_matches = re.findall(r'([0-9]{1,3}[A-Za-z]?)', query)
            if section_matches:
                logger.info(f"Found potential IPC section in query: {section_matches[0]}")
                return self._get_section_info(section_matches[0])
            else:
                # If they're asking about IPC but no specific section, give general info
                return self._create_response(
                    "The Indian Penal Code (IPC) is the official criminal code of India. "
                    "It covers all substantive aspects of criminal law. "
                    "You can ask me about specific sections like 'What is IPC 302?' or "
                    "type 'list common IPC sections' to see frequently referenced sections."
                )

        # Default response if no intent is matched
        return self._create_response(self.generic_responses[1])

    def _is_greeting(self, query):
        """Check if the query is a greeting."""
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon', 'good evening', 'howdy']
        return any(greeting in query for greeting in greetings)

    def _get_case_status(self, fir_number, user_id):
        """Get the status of a case by FIR number."""
        try:
            # Clean the FIR number
            fir_number = fir_number.strip().upper()

            # Query the database
            fir = FIR.query.filter_by(fir_number=fir_number).first()

            if not fir:
                return self._create_response(f"I couldn't find any case with FIR number {fir_number}. Please check the number and try again.")

            # Check if the user has access to this FIR
            if user_id and not self._user_has_access(user_id, fir):
                return self._create_response("You don't have permission to access information about this case.")

            # Get status information
            status_label = fir.get_status_label()

            # Create a response based on the status
            if fir.status == 'draft':
                response = f"FIR #{fir_number} is currently in draft status. It has not been officially submitted yet."
            elif fir.status == 'filed':
                filed_date = fir.filed_at.strftime('%d-%m-%Y') if fir.filed_at else 'recently'
                response = f"FIR #{fir_number} was filed on {filed_date} and is awaiting assignment to an investigating officer."
            elif fir.status == 'under_investigation':
                officer_name = fir.processing_officer.full_name if fir.processing_officer else 'an officer'
                response = f"FIR #{fir_number} is currently under investigation by {officer_name}."
            elif fir.status == 'closed':
                response = f"FIR #{fir_number} has been closed."
            else:
                response = f"FIR #{fir_number} is currently in {status_label} status."

            return self._create_response(response, {'fir_id': fir.id, 'status': fir.status})

        except Exception as e:
            logger.error(f"Error getting case status: {str(e)}")
            return self._create_response("I'm sorry, I encountered an error while retrieving the case status. Please try again later.")

    def _get_case_details(self, fir_number, user_id):
        """Get details about a case by FIR number."""
        try:
            # Clean the FIR number
            fir_number = fir_number.strip().upper()

            # Query the database
            fir = FIR.query.filter_by(fir_number=fir_number).first()

            if not fir:
                return self._create_response(f"I couldn't find any case with FIR number {fir_number}. Please check the number and try again.")

            # Check if the user has access to this FIR
            if user_id and not self._user_has_access(user_id, fir):
                return self._create_response("You don't have permission to access information about this case.")

            # Create a detailed response
            complainant_name = fir.complainant.full_name if fir.complainant else 'Unknown'
            filed_date = fir.filed_at.strftime('%d-%m-%Y') if fir.filed_at else 'Not yet filed'
            incident_date = fir.incident_date.strftime('%d-%m-%Y') if fir.incident_date else 'Not specified'
            incident_location = fir.incident_location or 'Not specified'
            status = fir.get_status_label()

            response = f"Details for FIR #{fir_number}:\n\n"
            response += f"Status: {status}\n"
            response += f"Filed on: {filed_date}\n"
            response += f"Complainant: {complainant_name}\n"
            response += f"Incident date: {incident_date}\n"
            response += f"Incident location: {incident_location}\n"

            if fir.processing_officer:
                response += f"Investigating Officer: {fir.processing_officer.full_name}\n"

            # Add a summary of the incident
            if fir.incident_description:
                # Truncate long descriptions
                description = fir.incident_description[:150] + "..." if len(fir.incident_description) > 150 else fir.incident_description
                response += f"\nIncident summary: {description}"

            return self._create_response(response, {'fir_id': fir.id})

        except Exception as e:
            logger.error(f"Error getting case details: {str(e)}")
            return self._create_response("I'm sorry, I encountered an error while retrieving the case details. Please try again later.")

    def _get_case_legal_sections(self, fir_number, user_id):
        """Get legal sections for a case by FIR number."""
        try:
            # Clean the FIR number
            fir_number = fir_number.strip().upper()

            # Query the database
            fir = FIR.query.filter_by(fir_number=fir_number).first()

            if not fir:
                return self._create_response(f"I couldn't find any case with FIR number {fir_number}. Please check the number and try again.")

            # Check if the user has access to this FIR
            if user_id and not self._user_has_access(user_id, fir):
                return self._create_response("You don't have permission to access information about this case.")

            # Check if legal sections are available
            if not fir.legal_sections:
                return self._create_response(f"No legal sections have been mapped for FIR #{fir_number} yet.")

            # Parse the legal sections JSON
            try:
                sections = json.loads(fir.legal_sections)
            except:
                return self._create_response(f"There was an error parsing the legal sections for FIR #{fir_number}.")

            if not sections:
                return self._create_response(f"No legal sections have been mapped for FIR #{fir_number} yet.")

            # Create a response with the legal sections
            response = f"Legal sections applicable to FIR #{fir_number}:\n\n"

            for i, section in enumerate(sections, 1):
                confidence = section.get('confidence', 0)
                confidence_text = f" (Confidence: {int(confidence * 100)}%)" if confidence > 0 else ""
                response += f"{i}. Section {section['code']}: {section['name']}{confidence_text}\n"
                response += f"   {section['description']}\n"
                if section.get('relevance'):
                    response += f"   Relevance: {section['relevance']}\n"
                response += "\n"

            response += "Note: These sections are determined by AI analysis and may not be exhaustive. The final determination will be made by the investigating officer."

            return self._create_response(response, {'fir_id': fir.id, 'sections': sections})

        except Exception as e:
            logger.error(f"Error getting case legal sections: {str(e)}")
            return self._create_response("I'm sorry, I encountered an error while retrieving the legal sections. Please try again later.")

    def _get_section_info(self, section_code):
        """Get information about a specific IPC section."""
        try:
            # Clean the section code
            section_code = section_code.strip().upper()
            if section_code.startswith('IPC'):
                section_code = section_code[3:].strip()

            # Log the query for debugging
            logger.info(f"Searching for IPC section: {section_code}")

            # Query the database
            section = None

            # Try exact match first
            section = LegalSection.query.filter_by(code=section_code).first()

            # If no exact match, try a more flexible search
            if not section:
                logger.info(f"No exact match for {section_code}, trying flexible search")
                section = LegalSection.query.filter(LegalSection.code.like(f"%{section_code}%")).first()

            # If still no match, try searching by name
            if not section:
                logger.info(f"No code match for {section_code}, trying name search")
                section = LegalSection.query.filter(LegalSection.name.ilike(f"%{section_code}%")).first()

            if not section:
                # List available sections to help the user
                available_sections = LegalSection.query.limit(5).all()
                section_list = ", ".join([s.code for s in available_sections])

                return self._create_response(
                    f"I couldn't find information about IPC section {section_code}. "
                    f"Please check the section number and try again.\n\n"
                    f"Some available sections are: {section_list}... (and more)"
                )

            # Create a response with the section information
            response = f"Information about IPC Section {section.code}:\n\n"
            response += f"Name: {section.name}\n"
            response += f"Description: {section.description}\n\n"

            # Add some context about when this section applies
            response += "This section typically applies to cases involving "

            # Map common sections to contexts
            contexts = {
                '299': 'culpable homicide where death is caused with the intention of causing death',
                '300': 'murder where culpable homicide is committed with the intention of causing death',
                '302': 'murder or homicide with punishment of death or imprisonment for life',
                '304': 'culpable homicide not amounting to murder',
                '304A': 'death caused by negligence',
                '304B': 'dowry death within 7 years of marriage',
                '305': 'abetment of suicide of a child or insane person',
                '306': 'abetment of suicide',
                '307': 'attempted murder',
                '308': 'attempted culpable homicide',
                '323': 'voluntarily causing hurt',
                '324': 'voluntarily causing hurt by dangerous weapons',
                '326': 'voluntarily causing grievous hurt by dangerous weapons',
                '326A': 'acid attacks',
                '354': 'assault or criminal force to woman with intent to outrage her modesty',
                '354A': 'sexual harassment',
                '354B': 'assault or use of criminal force with intent to disrobe a woman',
                '354C': 'voyeurism',
                '354D': 'stalking',
                '375': 'rape',
                '376': 'rape or sexual assault',
                '376D': 'gang rape',
                '379': 'theft',
                '380': 'theft in dwelling house',
                '384': 'extortion',
                '392': 'robbery',
                '395': 'dacoity (robbery by five or more persons)',
                '406': 'criminal breach of trust',
                '420': 'cheating and dishonestly inducing delivery of property',
                '498A': 'cruelty by husband or relatives of husband',
                '504': 'intentional insult with intent to provoke breach of peace',
                '506': 'criminal intimidation',
                '509': 'word, gesture or act intended to insult the modesty of a woman'
            }

            if section.code in contexts:
                response += contexts[section.code] + "."
            else:
                response += "specific criminal offenses as defined in the Indian Penal Code."

            return self._create_response(response, {'section': {'code': section.code, 'name': section.name, 'description': section.description}})

        except Exception as e:
            logger.error(f"Error getting section info: {str(e)}", exc_info=True)
            return self._create_response("I'm sorry, I encountered an error while retrieving information about this section. Please try again later.")

    def _analyze_complaint_text(self, complaint_text):
        """Analyze a complaint text to determine applicable IPC sections."""
        try:
            if not complaint_text or len(complaint_text.strip()) < 10:
                return self._create_response("Please provide a more detailed description of the case for analysis.")

            # Check if ML analyzer is available
            if not ML_ANALYZER_AVAILABLE:
                return self._create_response(
                    "I'm sorry, but the ML analyzer is not available at the moment. "
                    "This feature requires additional packages to be installed. "
                    "Please contact the system administrator to enable this feature."
                )

            # Use the ML analyzer to determine applicable sections
            analysis_result = analyze_complaint(complaint_text)

            if not analysis_result or not analysis_result.get('sections'):
                return self._create_response("I couldn't determine any applicable IPC sections for this case description. Please provide more details or consult with a legal professional.")

            sections = analysis_result.get('sections', [])

            # Create a response with the applicable sections
            response = "Based on your description, the following IPC sections may apply:\n\n"

            for section in sections:
                confidence = section.get('confidence', 0)

                # Format confidence level for better readability
                if confidence > 0.8:
                    confidence_level = "Very High"
                elif confidence > 0.6:
                    confidence_level = "High"
                elif confidence > 0.4:
                    confidence_level = "Moderate"
                elif confidence > 0.2:
                    confidence_level = "Low"
                else:
                    confidence_level = "Very Low"

                confidence_text = f" (Relevance: {confidence_level})" if confidence > 0 else ""

                # Add section header with better formatting
                response += f"📋 Section {section['section_code']}: {section['section_name']}{confidence_text}\n"

                # Add section description
                response += f"   {section['section_description']}\n"

                # Add matching keywords if available
                if section.get('keywords_matched') and len(section.get('keywords_matched', [])) > 0:
                    keywords = ", ".join([f"'{k}'" for k in section.get('keywords_matched', [])])
                    response += f"   Keywords matched: {keywords}\n"

                # Add relevance explanation if available
                if section.get('relevance'):
                    # Clean up the relevance text to avoid redundancy
                    relevance = section.get('relevance', '')
                    # Remove confidence information as we've already displayed it
                    relevance = re.sub(r'This complaint shows .* relevance \(score: .*\) to .*\.', '', relevance).strip()
                    if relevance:
                        response += f"   Why this applies: {relevance}\n"

                response += "\n"

            # Add a more helpful note at the end
            response += "📝 Note: This analysis is based on the information you provided and uses AI to identify potentially applicable IPC sections. The actual sections applied in a legal case may vary based on the complete evidence and legal interpretation.\n\n"
            response += "If you'd like to provide more details about the case, I can refine this analysis further."

            return self._create_response(response, {'analysis': analysis_result})

        except Exception as e:
            logger.error(f"Error analyzing complaint: {str(e)}")
            return self._create_response("I'm sorry, I encountered an error while analyzing the complaint. Please try again later.")

    def _user_has_access(self, user_id, fir):
        """Check if a user has access to a specific FIR."""
        try:
            # Query the user
            user = User.query.get(user_id)

            if not user:
                return False

            # Admins and police have access to all FIRs
            if user.is_admin() or user.is_police():
                return True

            # Regular users only have access to their own FIRs
            return user.id == fir.complainant_id

        except Exception as e:
            logger.error(f"Error checking user access: {str(e)}")
            return False

    def _list_common_sections(self):
        """List common IPC sections."""
        try:
            # Define categories of common sections
            categories = {
                "Basic Principles": ["1", "2", "3", "4", "5"],
                "General Exceptions": ["76", "80", "81", "82", "84", "87", "96", "97", "100"],
                "Abetment & Conspiracy": ["107", "108", "109", "120A", "120B"],
                "Offenses Against the State": ["121", "124A", "125", "128"],
                "Public Tranquility": ["141", "143", "146", "147", "153A"],
                "Offenses Against Human Body": ["299", "300", "302", "304", "304A", "307", "323", "324", "326", "354"],
                "Sexual Offenses": ["375", "376", "354A", "354B", "354C", "354D"],
                "Property Offenses": ["378", "379", "380", "392", "395", "406", "420"],
                "Public Order & Tranquility": ["499", "504", "506", "509"]
            }

            response = "Here are some commonly referenced IPC sections by category:\n\n"

            for category, section_codes in categories.items():
                response += f"{category}\n"
                response += "-" * len(category) + "\n"

                # Get section details from database
                sections = LegalSection.query.filter(LegalSection.code.in_(section_codes)).all()
                section_dict = {section.code: section for section in sections}

                # Add each section to the response
                for code in section_codes:
                    if code in section_dict:
                        section = section_dict[code]
                        # Truncate description if too long
                        description = section.description
                        if len(description) > 50:
                            description = description[:50] + "..."
                        response += f"• Section {section.code}: {section.name} - {description}\n"
                    else:
                        response += f"• Section {code}: Information not available\n"

                response += "\n"

            response += "You can ask for more details about any specific section by typing 'What is IPC section [number]?'"

            return self._create_response(response)

        except Exception as e:
            logger.error(f"Error listing common sections: {str(e)}", exc_info=True)
            return self._create_response("I'm sorry, I encountered an error while retrieving the list of common IPC sections. Please try again later.")

    def _create_response(self, text, data=None):
        """Create a structured response object."""
        response = {
            'text': text,
            'timestamp': datetime.now().isoformat()
        }

        if data:
            response['data'] = data

        return response


# Create a singleton instance
chatbot = FIRChatbot()

def get_response(query, user_id=None):
    """
    Get a response from the chatbot.

    Args:
        query: The user's query text
        user_id: The ID of the user making the query (for access control)

    Returns:
        dict: A response object with text and any additional data
    """
    return chatbot.process_query(query, user_id)
