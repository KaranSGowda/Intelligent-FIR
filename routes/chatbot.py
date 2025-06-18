"""
Chatbot routes for the Intelligent FIR System.
"""

import sys
import os
import json
from datetime import datetime
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.chatbot import get_response

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
def chatbot_interface():
    """Render the chatbot interface."""
    return render_template('chatbot/index.html')

@chatbot_bp.route('/api/query', methods=['POST'])
def chatbot_query():
    """API endpoint for chatbot queries."""
    try:
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)

        # Log request details
        logger.info(f"Received chatbot query request: {request.method}")
        logger.info(f"Request headers: {request.headers}")
        logger.info(f"Request data: {request.data}")
        current_app.logger.info(f"Received chatbot query request: {request.method}")
        current_app.logger.info(f"Request headers: {request.headers}")
        current_app.logger.info(f"Request data: {request.data}")

        # Parse JSON data
        data = request.get_json()
        logger.info(f"Parsed JSON data: {data}")
        current_app.logger.info(f"Parsed JSON data: {data}")

        # Validate query
        if not data or 'query' not in data:
            logger.warning("No query provided in request")
            current_app.logger.warning("No query provided in request")
            return jsonify({'error': 'No query provided'}), 400

        # Extract query
        query = data.get('query', '').strip()
        logger.info(f"Query: {query}")
        logger.info(f"Query type: {type(query)}")
        logger.info(f"Query length: {len(query)}")
        current_app.logger.info(f"Query: {query}")
        current_app.logger.info(f"Query type: {type(query)}")
        current_app.logger.info(f"Query length: {len(query)}")

        # Check for empty query
        if not query:
            logger.warning("Empty query")
            current_app.logger.warning("Empty query")
            return jsonify({'error': 'Empty query'}), 400

        # Get user ID if authenticated
        user_id = current_user.id if current_user.is_authenticated else None
        logger.info(f"User ID: {user_id}")
        current_app.logger.info(f"User ID: {user_id}")

        # Get response from chatbot
        logger.info("Getting response from chatbot")
        current_app.logger.info("Getting response from chatbot")

        # Check if this is a case description that should be analyzed
        case_keywords = [
            # Murder and violence
            "murder", "murdered", "murderer", "murderd", "murdred",
            "kill", "killed", "killing", "killer", "homicide", "manslaughter",
            "stab", "stabbed", "stabbing", "stabing", "stabed", "stabd",
            "shoot", "shot", "shooting", "strangle", "strangled", "strangling",
            "poison", "poisoned", "poisoning", "beat to death", "beaten to death",

            # Assault and physical harm
            "assault", "assaulted", "assaulting", "asault", "asaulted",
            "attack", "attacked", "attacking", "beat", "beaten", "beating",
            "hit", "hitting", "slap", "slapped", "slapping", "punch", "punched",
            "kick", "kicked", "kicking", "wound", "wounded", "wounding",
            "hurt", "hurting", "injury", "injured", "injuring", "harm", "harmed",

            # Theft and property crimes
            "theft", "thief", "thieves", "theif", "theift", "steal", "stole", "stolen", "stealing",
            "robbery", "robbed", "robbing", "roberry", "robed", "burglary", "burglar",
            "broke into", "breaking in", "break-in", "shoplifting", "shoplifted",
            "snatch", "snatched", "snatching", "pickpocket", "pickpocketed",

            # Sexual crimes
            "rape", "raped", "raping", "sexual assault", "sexually assaulted",
            "molest", "molested", "molesting", "sexual harassment", "sexually harassed",
            "indecent", "obscene", "lewd", "voyeurism", "stalking", "stalked",

            # Fraud and deception
            "fraud", "fraudulent", "frauded", "cheat", "cheated", "cheating", "cheeted", "cheeting",
            "deceive", "deceived", "deceiving", "scam", "scammed", "scamming",
            "forge", "forged", "forging", "forgery", "counterfeit", "counterfeited",
            "impersonate", "impersonated", "impersonating", "identity theft",

            # Other crimes
            "kidnap", "kidnapped", "kidnapping", "kidnaped", "kidnapin", "abduct", "abducted",
            "threat", "threatened", "threatening", "blackmail", "blackmailed", "extort", "extorted",
            "bribe", "bribed", "bribing", "corruption", "corrupt", "corrupted",
            "trespass", "trespassed", "trespassing", "vandalize", "vandalized",
            "defame", "defamed", "defaming", "slander", "slandered", "libel",
            "abuse", "abused", "abusing", "harass", "harassed", "harassing", "harasment", "harased",
            "accident", "damage", "damaged", "damaging"
        ]

        # List of common figurative expressions and contexts that should not be treated as crimes
        figurative_expressions = [
            "killing me", "killing time", "killing it", "killed it", "killing the game",
            "watched a movie", "saw a film", "read a book", "in a movie", "in a book",
            "in a novel", "in a story", "in a game", "video game", "playing a game",
            "hypothetically", "if someone were to", "what would happen if",
            "what if", "in theory", "theoretically", "in a hypothetical",
            "beauty", "beautiful", "gorgeous", "stunning", "amazing", "awesome",
            "metaphorically", "figuratively", "not literally"
        ]

        # Check if the query contains figurative expressions
        contains_figurative = False
        for expression in figurative_expressions:
            if expression in query.lower():
                contains_figurative = True
                logger.info(f"Detected figurative expression: {expression}")
                current_app.logger.info(f"Detected figurative expression: {expression}")
                break

        # Check if the query contains crime keywords
        is_case_description = False
        if not contains_figurative:  # Only check for crime keywords if no figurative expressions were found
            # Special case for "harrasing" which is a common misspelling
            if "harrasing" in query.lower():
                is_case_description = True
                logger.info("Detected case description with keyword: harrasing (misspelled)")
                current_app.logger.info("Detected case description with keyword: harrasing (misspelled)")
            else:
                for keyword in case_keywords:
                    if keyword in query.lower():
                        # Check if the keyword is part of a larger word (e.g., "kill" in "skill")
                        # by looking for word boundaries
                        import re
                        if re.search(r'\b' + re.escape(keyword) + r'\b', query.lower()):
                            is_case_description = True
                            logger.info(f"Detected case description with keyword: {keyword}")
                            current_app.logger.info(f"Detected case description with keyword: {keyword}")
                            break

        # Process as a case description if it contains crime keywords and no figurative expressions
        if is_case_description and not contains_figurative:
            logger.info("Detected case description for analysis")
            current_app.logger.info("Detected case description for analysis")

            # Import analyze_complaint directly
            from utils.ml_analyzer import analyze_complaint, preprocess_text
            from models import LegalSection

            # Preprocess the query to handle misspellings
            preprocessed_query = preprocess_text(query)
            logger.info(f"Preprocessed query: {preprocessed_query}")
            current_app.logger.info(f"Preprocessed query: {preprocessed_query}")

            # Special case for "harrasing" which is a common misspelling
            if "harrasing" in query.lower():
                # Add "harassing" to the preprocessed query
                preprocessed_query = preprocessed_query + " harassing"
                logger.info(f"Added 'harassing' to preprocessed query: {preprocessed_query}")
                current_app.logger.info(f"Added 'harassing' to preprocessed query: {preprocessed_query}")

            # Direct keyword matching for common crimes
            direct_matches = []

            # Common crime keywords and their corresponding IPC sections
            common_crimes = {
                # Murder and homicide
                "murder": "302",
                "murdered": "302",
                "murderer": "302",
                "murderd": "302",
                "murdred": "302",
                "killed": "302",
                "killing": "302",
                "homicide": "302",
                "manslaughter": "304",

                # Assault and physical harm
                "assault": "323",
                "assaulted": "323",
                "assaulting": "323",
                "asault": "323",
                "asaulted": "323",
                "attacked": "323",
                "beat": "323",
                "beaten": "323",
                "hit": "323",
                "slapped": "323",
                "punched": "323",
                "kicked": "323",
                "hurt": "323",
                "injury": "323",
                "injured": "323",
                "wound": "323",
                "wounded": "323",

                # Stabbing (specific type of assault)
                "stab": "324",
                "stabbed": "324",
                "stabbing": "324",
                "stabing": "324",
                "stabed": "324",
                "stabd": "324",
                "knife": "324",

                # Theft
                "theft": "379",
                "thief": "379",
                "theif": "379",
                "theift": "379",
                "stole": "379",
                "stolen": "379",
                "stealing": "379",

                # Robbery
                "robbery": "392",
                "robbed": "392",
                "robbing": "392",
                "roberry": "392",
                "robed": "392",

                # Sexual crimes
                "rape": "376",
                "raped": "376",
                "raping": "376",
                "sexual": "376",
                "molest": "376",
                "molested": "376",

                # Fraud and cheating
                "cheat": "420",
                "cheated": "420",
                "cheating": "420",
                "cheeted": "420",
                "cheeting": "420",
                "fraud": "420",
                "fraudulent": "420",
                "scam": "420",
                "scammed": "420",

                # Kidnapping
                "kidnap": "363",
                "kidnapped": "363",
                "kidnapping": "363",
                "kidnaped": "363",
                "kidnapin": "363",
                "abduct": "363",
                "abducted": "363",

                # Defamation
                "defame": "499",
                "defamed": "499",
                "defaming": "499",
                "slander": "499",
                "slandered": "499",

                # Harassment
                "harass": "354D",
                "harassed": "354D",
                "harassing": "354D",
                "harasment": "354D",
                "harased": "354D",
                "stalking": "354D",
                "stalked": "354D",

                # Threats and intimidation
                "threat": "506",
                "threatened": "506",
                "threatening": "506",
                "blackmail": "506",
                "intimidate": "506",
                "intimidated": "506"
            }

            # Check for direct matches in the preprocessed query
            for keyword, section_code in common_crimes.items():
                # Check for exact word matches
                if keyword in preprocessed_query.split():
                    # Get the section details
                    section = LegalSection.query.filter_by(code=section_code).first()
                    if section:
                        # Add to direct matches with high confidence
                        direct_matches.append({
                            'section_code': section_code,
                            'section_name': section.name,
                            'section_description': section.description,
                            'confidence': 0.85,  # High confidence for direct matches
                            'keywords_matched': [keyword],
                            'relevance': f"This section applies because your description contains '{keyword}', which is directly related to {section.name}."
                        })
                # Also check for partial matches for longer words (like "harrasing" -> "harassing")
                elif len(keyword) > 5 and keyword not in preprocessed_query.split():
                    # For longer keywords, check if any word in the query is similar to the keyword
                    for word in preprocessed_query.split():
                        # Skip short words and common words
                        if len(word) < 5 or word in ['with', 'this', 'that', 'then', 'than', 'they', 'them', 'their', 'there', 'these', 'those', 'some', 'from', 'have', 'what', 'when', 'where', 'which', 'while', 'about', 'after', 'before', 'during', 'under', 'above', 'below', 'between', 'through', 'today', 'tomorrow', 'yesterday', 'medium', 'media', 'online', 'person', 'people', 'neighbor']:
                            continue

                        # Calculate Levenshtein distance (edit distance)
                        def levenshtein_distance(s1, s2):
                            if len(s1) < len(s2):
                                return levenshtein_distance(s2, s1)
                            if len(s2) == 0:
                                return len(s1)
                            previous_row = range(len(s2) + 1)
                            for i, c1 in enumerate(s1):
                                current_row = [i + 1]
                                for j, c2 in enumerate(s2):
                                    insertions = previous_row[j + 1] + 1
                                    deletions = current_row[j] + 1
                                    substitutions = previous_row[j] + (c1 != c2)
                                    current_row.append(min(insertions, deletions, substitutions))
                                previous_row = current_row
                            return previous_row[-1]

                        # Calculate similarity as 1 - (edit_distance / max_length)
                        max_length = max(len(word), len(keyword))
                        edit_distance = levenshtein_distance(word, keyword)
                        similarity = 1 - (edit_distance / max_length)

                        # Only consider words with high similarity (at least 70%)
                        if similarity >= 0.7:
                            # Get the section details
                            section = LegalSection.query.filter_by(code=section_code).first()
                            if section:
                                # Add to direct matches with slightly lower confidence
                                direct_matches.append({
                                    'section_code': section_code,
                                    'section_name': section.name,
                                    'section_description': section.description,
                                    'confidence': 0.75,  # Slightly lower confidence for partial matches
                                    'keywords_matched': [word],
                                    'relevance': f"This section applies because your description contains '{word}', which is similar to '{keyword}' and related to {section.name}."
                                })
                            break

            # Analyze the complaint using the ML model
            logger.info("Analyzing complaint directly")
            current_app.logger.info("Analyzing complaint directly")
            analysis_result = analyze_complaint(query)
            logger.info(f"Analysis result: {analysis_result}")
            current_app.logger.info(f"Analysis result: {analysis_result}")

            # Combine direct matches with ML results
            if direct_matches:
                if not analysis_result:
                    analysis_result = {'sections': []}

                # Add direct matches to the analysis result
                for match in direct_matches:
                    # Check if this section is already in the results
                    existing = next((s for s in analysis_result.get('sections', []) if s.get('section_code') == match['section_code']), None)

                    if existing:
                        # Update the existing entry with higher confidence if direct match has higher confidence
                        if match['confidence'] > existing.get('confidence', 0):
                            existing['confidence'] = match['confidence']
                            existing['keywords_matched'] = match['keywords_matched']
                            existing['relevance'] = match['relevance']
                    else:
                        # Add the new match
                        analysis_result['sections'].append(match)

            # Format the response
            if analysis_result and analysis_result.get('sections'):
                sections = analysis_result.get('sections', [])

                # Filter sections with confidence below threshold and limit to top 3 most relevant
                CONFIDENCE_THRESHOLD = 0.30  # 30% - increased threshold for better precision
                filtered_sections = [s for s in sections if s.get('confidence', 0) >= CONFIDENCE_THRESHOLD]

                # Special case for figurative language
                figurative_expressions = ["killing me", "killing time", "killed it", "killing it"]
                for expr in figurative_expressions:
                    if expr in query.lower() and any(s.get('section_code') == '302' for s in filtered_sections):
                        # Remove murder section for figurative expressions
                        filtered_sections = [s for s in filtered_sections if s.get('section_code') != '302']

                # Sort by confidence (highest first) and take top 3
                filtered_sections = sorted(filtered_sections, key=lambda s: s.get('confidence', 0), reverse=True)[:3]

                # If we have more than one section, ensure they're significantly different
                if len(filtered_sections) > 1:
                    # Keep track of sections to remove
                    to_remove = []

                    # Check for similar sections (e.g., 379 and 380 both deal with theft)
                    for i, section1 in enumerate(filtered_sections):
                        for j, section2 in enumerate(filtered_sections[i+1:], i+1):
                            # If sections have similar keywords or are in the same category
                            keywords1 = set(section1.get('keywords_matched', []))
                            keywords2 = set(section2.get('keywords_matched', []))

                            # If they share more than 50% of keywords, consider them similar
                            if keywords1 and keywords2:
                                overlap = keywords1.intersection(keywords2)
                                if len(overlap) / min(len(keywords1), len(keywords2)) > 0.5:
                                    # Keep the one with higher confidence
                                    if section1.get('confidence', 0) < section2.get('confidence', 0):
                                        to_remove.append(i)
                                    else:
                                        to_remove.append(j)

                    # Remove similar sections (in reverse order to avoid index issues)
                    for idx in sorted(to_remove, reverse=True):
                        if idx < len(filtered_sections):
                            filtered_sections.pop(idx)

                # Check if we have any sections after filtering
                if filtered_sections:
                    # Check if this is likely a real crime description
                    # If the highest confidence is very low, it might be a false positive
                    highest_confidence = max([s.get('confidence', 0) for s in filtered_sections]) if filtered_sections else 0

                    if highest_confidence < 0.30:  # Less than 30% confidence for the best match - increased threshold
                        logger.info(f"Likely false positive - highest confidence: {highest_confidence}")
                        current_app.logger.info(f"Likely false positive - highest confidence: {highest_confidence}")

                        response = {
                            'text': "I don't think this describes a crime situation with enough detail. If you're trying to report a crime, please provide more specific details about the incident.",
                            'timestamp': datetime.now().isoformat()
                        }
                    else:
                        # Format response with filtered sections
                        response_text = "Based on your description, the following IPC sections may apply:\n\n"

                        for section in filtered_sections:
                            confidence = section.get('confidence', 0)

                            # Determine relevance level based on confidence
                            if confidence > 0.7:
                                relevance = "High"
                            elif confidence > 0.5:
                                relevance = "Moderate"
                            else:
                                relevance = "Low"

                            # Format the section information
                            response_text += f"📋 Section {section['section_code']}: {section['section_name']} (Relevance: {relevance})\n"
                            response_text += f"   {section['section_description']}\n"

                            # Add matched keywords if available
                            if section.get('keywords_matched'):
                                keywords = ', '.join(f"'{k}'" for k in section.get('keywords_matched', []))
                                if keywords:
                                    response_text += f"   Keywords matched: {keywords}\n"

                            response_text += "\n"

                        # Add a note about the analysis
                        response_text += "📝 Note: This analysis is based on the information you provided and uses AI to identify potentially applicable IPC sections. The actual sections applied in a legal case may vary based on the complete evidence and legal interpretation.\n\n"
                        response_text += "If you'd like to provide more details about the case, I can refine this analysis further."

                        response = {
                            'text': response_text,
                            'timestamp': datetime.now().isoformat(),
                            'data': {'analysis': {'sections': filtered_sections}}
                        }
                else:
                    # No sections above threshold
                    response = {
                        'text': "I couldn't determine any applicable IPC sections with sufficient confidence for this description. Please provide more specific details about the incident.",
                        'timestamp': datetime.now().isoformat()
                    }
            else:
                response = {
                    'text': "I couldn't determine any applicable IPC sections for this case description. Please provide more details or consult with a legal professional.",
                    'timestamp': datetime.now().isoformat()
                }
        else:
            # Get response from chatbot
            response = get_response(query, user_id)

        logger.info(f"Chatbot response: {response}")
        current_app.logger.info(f"Chatbot response: {response}")

        return jsonify(response)

    except Exception as e:
        import traceback
        current_app.logger.error(f"Error processing chatbot query: {str(e)}")
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': f'An error occurred while processing your query: {str(e)}'}), 500

@chatbot_bp.route('/api/history', methods=['GET'])
@login_required
def chatbot_history():
    """Get the user's chat history."""
    # This would typically fetch from a database, but for simplicity we'll return an empty history
    return jsonify({'history': []})

@chatbot_bp.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to check if the API is working."""
    current_app.logger.info("Test endpoint called")
    return jsonify({
        'status': 'success',
        'message': 'API is working',
        'time': str(datetime.now())
    })

