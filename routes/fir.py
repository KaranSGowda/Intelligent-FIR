import os
import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import FIR, Evidence, User, Role
from utils.openai_helper import map_legal_sections, analyze_image
from utils.ml_analyzer import analyze_complaint
from utils.legal_mapper import get_legal_sections_for_fir
from utils.pdf_generator import generate_fir_pdf, generate_fir_pdf_simple, generate_and_store_fir_pdf
from utils.speech_recognition import SpeechToText
import tempfile
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)

fir_bp = Blueprint('fir', __name__)

# Initialize the speech recognition
speech_recognizer = SpeechToText()

@fir_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('fir.dashboard'))
    return render_template('index.html')

@fir_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))

        # For police users, show assigned cases
        if current_user.is_police():
            firs = FIR.query.filter_by(processing_officer_id=current_user.id).all()
        else:
            # For regular users, show their complaints
            firs = FIR.query.filter_by(complainant_id=current_user.id).all()

        logger.info(f"Retrieved {len(firs)} FIRs for user {current_user.id}")
        return render_template('fir/dashboard.html', firs=firs)

    except Exception as e:
        logger.error(f"Dashboard error: {str(e)}", exc_info=True)
        return render_template('error.html', error="An error occurred while loading the dashboard. Please try again later."), 500

@fir_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new_fir():
    if request.method == 'POST':
        # Check if this is a form submission or API call for transcription
        if 'transcribe' in request.form:
            try:
                # Handle audio file upload for transcription
                if 'audio' not in request.files:
                    return jsonify({'error': 'No audio file provided'}), 400

                audio_file = request.files['audio']
                if not audio_file:
                    return jsonify({'error': 'No audio file selected'}), 400

                # Save the audio file
                filename = secure_filename(f"{uuid.uuid4()}.webm")
                audio_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'audio', filename)
                audio_file.save(audio_path)

                # Set a longer server-side timeout for transcription operations

                logger.info(f"Starting transcription for audio file: {audio_path}")
                start_time = time.time()
                transcription_result = queue.Queue()

                def transcribe_with_timeout():
                    try:
                        # First try a quick transcription with a smaller model for faster results
                        try:
                            logger.info("Attempting quick transcription with small model...")
                            # Use a smaller model for faster results
                            result = speech_recognizer.transcribe_audio_quick(audio_path)
                            if result:
                                logger.info("Quick transcription successful")
                                transcription_result.put(('success', result))
                                return
                        except Exception as quick_error:
                            logger.warning(f"Quick transcription failed: {str(quick_error)}")

                        # If quick transcription fails, try the full transcription
                        logger.info("Attempting full transcription with medium model...")
                        result = speech_recognizer.transcribe_audio(audio_path)
                        if result:
                            logger.info("Full transcription successful")
                            transcription_result.put(('success', result))
                            return

                        # If all internal methods fail, return an error
                        logger.error("All transcription methods failed")
                        transcription_result.put(('error', "All transcription methods failed"))
                    except Exception as e:
                        logger.error(f"Transcription thread error: {str(e)}", exc_info=True)
                        transcription_result.put(('error', str(e)))

                # Start transcription in a separate thread
                transcription_thread = threading.Thread(target=transcribe_with_timeout)
                transcription_thread.daemon = True
                transcription_thread.start()

                # Wait for result with timeout (90 seconds)
                try:
                    # First check if we can get a quick result (15 seconds)
                    try:
                        result_type, result_value = transcription_result.get(timeout=15)
                        elapsed_time = time.time() - start_time
                        logger.info(f"Transcription completed quickly in {elapsed_time:.2f} seconds with status: {result_type}")

                        if result_type == 'success':
                            return jsonify({
                                'transcription': result_value,
                                'audio_path': audio_path,
                                'processing_time': f"{elapsed_time:.2f} seconds"
                            }), 200
                    except queue.Empty:
                        # Quick result not available, send a progress update to client
                        # This is a non-blocking response that tells the client we're still working
                        logger.info("Quick transcription not available, continuing to wait...")

                    # Wait longer for the full result (up to 90 seconds total)
                    try:
                        result_type, result_value = transcription_result.get(timeout=75)  # 15 + 75 = 90 seconds total
                        elapsed_time = time.time() - start_time
                        logger.info(f"Transcription completed in {elapsed_time:.2f} seconds with status: {result_type}")

                        if result_type == 'success':
                            return jsonify({
                                'transcription': result_value,
                                'audio_path': audio_path,
                                'processing_time': f"{elapsed_time:.2f} seconds"
                            }), 200
                        else:
                            # If all methods fail, return a generic message
                            return jsonify({
                                'transcription': 'Audio recorded but transcription failed. Please type your complaint manually.',
                                'audio_path': audio_path,
                                'warning': f'Automatic transcription failed: {result_value}. The audio has been saved.',
                                'processing_time': f"{elapsed_time:.2f} seconds"
                            }), 200
                    except queue.Empty:
                        # Full timeout occurred
                        elapsed_time = time.time() - start_time
                        logger.error(f"Transcription timed out after {elapsed_time:.2f} seconds")
                        return jsonify({
                            'transcription': 'Audio recorded but transcription timed out. Please type your complaint manually.',
                            'audio_path': audio_path,
                            'warning': 'Transcription process took too long. The audio has been saved.',
                            'processing_time': f"{elapsed_time:.2f} seconds"
                        }), 200

                except Exception as timeout_error:
                    # Handle any other errors during the timeout process
                    elapsed_time = time.time() - start_time
                    logger.error(f"Error during transcription timeout handling: {str(timeout_error)}")
                    return jsonify({
                        'transcription': 'Audio recorded but an error occurred during transcription. Please type your complaint manually.',
                        'audio_path': audio_path,
                        'warning': f'Error during transcription: {str(timeout_error)}. The audio has been saved.',
                        'processing_time': f"{elapsed_time:.2f} seconds"
                    }), 200
            except Exception as e:
                logger.error(f"General transcription error: {str(e)}", exc_info=True)
                return jsonify({
                    'error': 'An error occurred while processing your audio.',
                    'message': 'Please try again or type your complaint manually.'
                }), 500
        else:
            # Regular form submission - create a new FIR
            try:
                incident_description = request.form.get('incident_description', '')
                transcription = request.form.get('transcription', '')
                incident_date_str = request.form.get('incident_date', '')
                incident_location = request.form.get('incident_location', '')

                # Parse incident date if provided
                incident_date = None
                if incident_date_str:
                    try:
                        incident_date = datetime.strptime(incident_date_str, '%Y-%m-%dT%H:%M')
                    except ValueError:
                        flash('Invalid date format.', 'danger')
                        return redirect(url_for('fir.new_fir'))

                # Create a new FIR
                fir = FIR()
                fir.complainant_id = current_user.id
                fir.incident_description = incident_description
                fir.transcription = transcription
                fir.incident_date = incident_date
                fir.incident_location = incident_location
                fir.status = "draft"
                fir.fir_number = f"FIR{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

                db.session.add(fir)
                db.session.flush()  # Get the FIR ID without committing

                # Analyze the complaint text
                if incident_description:
                    # Get the user's language preference
                    language_code = None
                    try:
                        from utils.language_utils import get_user_language
                        language_code = get_user_language()
                        logger.info(f"Using language from session for complaint analysis: {language_code}")
                    except ImportError:
                        language_code = "en-IN"  # Default to Indian English
                        logger.info(f"Using default language for complaint analysis: {language_code}")

                    # Get complaint analysis - using try/except for each AI operation separately
                    # to ensure partial success is still possible
                    try:
                        complaint_analysis = analyze_complaint(incident_description, language_code)
                        if complaint_analysis and 'urgency_level' in complaint_analysis:
                            fir.urgency_level = complaint_analysis['urgency_level']
                    except Exception as e:
                        error_msg = str(e)
                        if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                            flash('Unable to analyze complaint due to API quota limitations. The FIR will still be created with default settings.', 'warning')
                        else:
                            flash(f'Error during complaint analysis: {str(e)}', 'warning')

                    # Map legal sections - separate try/except to allow this to work
                    # even if the previous analysis failed
                    try:
                        legal_mapping = map_legal_sections(incident_description)
                        legal_sections = get_legal_sections_for_fir(legal_mapping)
                        # Store the legal sections as JSON
                        fir.legal_sections = json.dumps(legal_sections)
                    except Exception as e:
                        error_msg = str(e)
                        if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                            flash('Unable to map legal sections due to API quota limitations. You may need to manually add relevant legal sections.', 'warning')
                        else:
                            flash(f'Error mapping legal sections: {str(e)}', 'warning')

                # Handle evidence uploads
                if 'evidence' in request.files:
                    evidence_files = request.files.getlist('evidence')
                    for file in evidence_files:
                        if file and file.filename:
                            filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', filename)
                            file.save(file_path)

                            # Create evidence record
                            evidence = Evidence()
                            evidence.fir_id = fir.id
                            evidence.type = 'image'
                            evidence.file_path = file_path
                            evidence.description = request.form.get('evidence_description', '')
                            db.session.add(evidence)

                db.session.commit()
                flash('FIR created successfully!', 'success')
                return redirect(url_for('fir.view_fir', fir_id=fir.id))
            except Exception as e:
                db.session.rollback()
                flash(f'Error creating FIR: {str(e)}', 'danger')

    return render_template('fir/new.html')

@fir_bp.route('/view/<int:fir_id>')
@login_required
def view_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)

    # Check if the user has permission to view this FIR
    if not (current_user.is_admin() or current_user.is_police() or
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to view this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))

    return render_template('fir/view.html', fir=fir)

@fir_bp.route('/update/<int:fir_id>', methods=['POST'])
@login_required
def update_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)

    # Check if the user has permission to update this FIR
    if not (current_user.is_admin() or current_user.is_police() or
            (fir.complainant_id == current_user.id and fir.status == "draft")):
        flash('You do not have permission to update this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))

    try:
        # Update FIR fields
        fir.incident_description = request.form.get('incident_description', fir.incident_description)
        fir.incident_location = request.form.get('incident_location', fir.incident_location)

        incident_date_str = request.form.get('incident_date')
        if incident_date_str:
            try:
                fir.incident_date = datetime.strptime(incident_date_str, '%Y-%m-%dT%H:%M')
            except ValueError:
                flash('Invalid date format.', 'danger')

        # Status updates for police/admin only
        if current_user.is_admin() or current_user.is_police():
            new_status = request.form.get('status')
            if new_status and new_status != fir.status:
                fir.status = new_status

                # If changing to filed status, set the filed_at date
                if new_status == "filed" and not fir.filed_at:
                    fir.filed_at = datetime.now(timezone.utc)

        db.session.commit()
        flash('FIR updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating FIR: {str(e)}', 'danger')

    return redirect(url_for('fir.view_fir', fir_id=fir.id))

@fir_bp.route('/delete/<int:fir_id>', methods=['POST'])
@login_required
def delete_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)

    # Only admin or the owner of a draft FIR can delete it
    if not (current_user.is_admin() or
            (fir.complainant_id == current_user.id and fir.status == "draft")):
        flash('You do not have permission to delete this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))

    try:
        db.session.delete(fir)
        db.session.commit()
        flash('FIR deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting FIR: {str(e)}', 'danger')

    return redirect(url_for('fir.dashboard'))

@fir_bp.route('/submit/<int:fir_id>', methods=['POST'])
@login_required
def submit_fir(fir_id):
    fir = FIR.query.get_or_404(fir_id)

    # Only the owner of a draft FIR can submit it
    if not (fir.complainant_id == current_user.id and fir.status == "draft"):
        flash('You do not have permission to submit this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))

    try:
        fir.status = "filed"
        fir.filed_at = datetime.now(timezone.utc)

        # Analyze the complaint if not already done
        if not fir.legal_sections and fir.incident_description:
            # Map legal sections - using separate try/except blocks for each AI feature
            try:
                legal_mapping = map_legal_sections(fir.incident_description)
                legal_sections = get_legal_sections_for_fir(legal_mapping)
                # Store the legal sections as JSON
                fir.legal_sections = json.dumps(legal_sections)
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                    flash('Unable to map legal sections due to API quota limitations. The FIR will still be filed, but you may need to manually add relevant legal sections.', 'warning')
                else:
                    flash(f'Error mapping legal sections: {str(e)}', 'warning')

            # Get the user's language preference
            language_code = None
            try:
                from utils.language_utils import get_user_language
                language_code = get_user_language()
                logger.info(f"Using language from session for urgency analysis: {language_code}")
            except ImportError:
                language_code = "en-IN"  # Default to Indian English
                logger.info(f"Using default language for urgency analysis: {language_code}")

            # Get complaint analysis for urgency - separate try/except to allow partial success
            try:
                complaint_analysis = analyze_complaint(fir.incident_description, language_code)
                if complaint_analysis and 'urgency_level' in complaint_analysis:
                    fir.urgency_level = complaint_analysis['urgency_level']
            except Exception as e:
                error_msg = str(e)
                if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
                    flash('Unable to analyze complaint for urgency due to API quota limitations. Using default urgency level.', 'warning')
                else:
                    flash(f'Error during urgency analysis: {str(e)}', 'warning')

        db.session.commit()

        # Generate and store PDF for the FIR
        try:
            pdf_path = generate_and_store_fir_pdf(fir.id)
            if pdf_path:
                logger.info(f"Generated and stored PDF for FIR {fir.fir_number}: {pdf_path}")
            else:
                logger.warning(f"Failed to generate PDF for FIR {fir.fir_number}")
        except Exception as pdf_error:
            logger.error(f"Error generating PDF for FIR {fir.fir_number}: {str(pdf_error)}")
            # Don't stop the process if PDF generation fails

        flash('FIR submitted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting FIR: {str(e)}', 'danger')

    return redirect(url_for('fir.view_fir', fir_id=fir.id))

@fir_bp.route('/generate_pdf/<int:fir_id>')
@login_required
def generate_pdf(fir_id):
    fir = FIR.query.get_or_404(fir_id)

    # Check if the user has permission to view this FIR
    if not (current_user.is_admin() or current_user.is_police() or
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to generate PDF for this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))

    try:
        # Check if we already have a stored PDF
        if fir.pdf_path and os.path.exists(fir.pdf_path):
            logger.info(f"Using existing PDF for FIR {fir.fir_number}: {fir.pdf_path}")
            return send_file(fir.pdf_path, as_attachment=True, download_name=f"FIR_{fir.fir_number}.pdf")

        # If no stored PDF or it doesn't exist, generate a new one
        logger.info(f"No existing PDF found for FIR {fir.fir_number}, generating new one")

        # Generate the PDF
        user = User.query.get(fir.complainant_id)

        # Parse legal sections from JSON if available
        legal_sections = []
        if fir.legal_sections:
            try:
                legal_sections_data = json.loads(fir.legal_sections)
                # Convert to objects with the expected attributes for the PDF generator
                for section_data in legal_sections_data:
                    # Create a dynamic object with the required attributes
                    section_obj = type('LegalSection', (), {
                        'code': section_data.get('section_code', section_data.get('code', 'Unknown')),
                        'name': section_data.get('section_name', section_data.get('name', 'Unknown')),
                        'description': section_data.get('section_description', section_data.get('description', ''))
                    })()
                    legal_sections.append(section_obj)
            except Exception as json_error:
                logger.error(f"Error parsing legal sections JSON: {str(json_error)}")
                flash('Warning: Could not parse legal sections data.', 'warning')

        # Get evidence items
        evidence = Evidence.query.filter_by(fir_id=fir.id).all()

        # Try to generate the enhanced PDF first
        try:
            pdf_path = generate_fir_pdf(fir, user, legal_sections, evidence)
        except Exception as pdf_error:
            logger.warning(f"Enhanced PDF generation failed, falling back to simple version: {str(pdf_error)}")
            # If enhanced PDF generation fails, fall back to simple version
            pdf_path = generate_fir_pdf_simple(fir, user, legal_sections)
            flash('Using simplified PDF format due to technical limitations.', 'warning')

        # Store the PDF path in the database
        fir.pdf_path = pdf_path
        db.session.commit()
        logger.info(f"Generated and stored new PDF for FIR {fir.fir_number}: {pdf_path}")

        # Return the PDF file
        return send_file(pdf_path, as_attachment=True, download_name=f"FIR_{fir.fir_number}.pdf")
    except Exception as e:
        logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
        flash(f'Error generating PDF: {str(e)}', 'danger')
        return redirect(url_for('fir.view_fir', fir_id=fir.id))

# API endpoint for analyzing legal sections
@fir_bp.route('/analyze_legal_sections', methods=['POST'])
@login_required
def analyze_legal_sections():
    try:
        # Get the text from the request
        data = request.json
        if not data or 'text' not in data:
            return jsonify({'error': 'No text provided for analysis'}), 400

        text = data['text']
        if not text.strip():
            return jsonify({'error': 'Empty text provided for analysis'}), 400

        # Get language code if provided
        language_code = data.get('language_code')

        # If no language code provided, try to get from session
        if not language_code:
            try:
                from utils.language_utils import get_user_language
                language_code = get_user_language()
                logger.info(f"Using language from session for legal analysis: {language_code}")
            except ImportError:
                language_code = "en-IN"  # Default to Indian English
                logger.info(f"Using default language for legal analysis: {language_code}")

        # Map legal sections with language code
        legal_mapping = map_legal_sections(text)
        legal_sections = get_legal_sections_for_fir(legal_mapping)

        # Also analyze the complaint with our ML model
        try:
            # analyze_complaint is already imported at the top
            ml_analysis = analyze_complaint(text, language_code)
            ml_sections = ml_analysis.get('sections', [])

            # Combine the results (add ML sections that aren't already in the list)
            existing_codes = {section.get('section_code') for section in legal_sections}
            for ml_section in ml_sections:
                if ml_section.get('section_code') not in existing_codes:
                    legal_sections.append(ml_section)
                    existing_codes.add(ml_section.get('section_code'))
        except Exception as ml_error:
            logger.warning(f"ML analysis failed, using only API results: {str(ml_error)}")

        # Return the sections with language information
        return jsonify({
            'sections': legal_sections,
            'language_code': language_code
        }), 200
    except Exception as e:
        error_msg = str(e)
        status_code = 500

        # More informative error messages for different error types
        if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
            error_msg = "API quota exceeded. The text could not be analyzed due to API limitations."
            # Use 429 for rate limit/quota issues
            status_code = 429

        return jsonify({
            'error': error_msg
        }), status_code

# API endpoint for analyzing uploaded images
@fir_bp.route('/analyze_image', methods=['POST'])
@login_required
def api_analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if not image_file:
        return jsonify({'error': 'No image file selected'}), 400

    # Initialize image_path variable
    image_path = None

    try:
        # Save the image file
        filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'images', filename)
        image_file.save(image_path)

        # Analyze the image
        analysis = analyze_image(image_path)

        return jsonify({
            'analysis': analysis,
            'image_path': image_path
        }), 200
    except Exception as e:
        error_msg = str(e)
        status_code = 500

        # More informative error messages for different error types
        if "quota" in error_msg.lower() or "insufficient" in error_msg.lower():
            error_msg = "API quota exceeded. The image was saved but could not be analyzed due to API limitations. You can still attach it as evidence."
            # Use 429 for rate limit/quota issues
            status_code = 429
        elif "format" in error_msg.lower() or "invalid" in error_msg.lower():
            error_msg = "The image format could not be processed. Please try a different image."
            # Use 415 for unsupported media type
            status_code = 415

        return jsonify({
            'error': error_msg,
            'image_path': image_path
        }), status_code

@fir_bp.route('/voice-transcription')
@login_required
def voice_transcription():
    """Render the voice transcription page"""
    # Check if there's a transcription in the session
    transcription_text = session.get('voice_transcription', '')

    # Also check if there's a transcription in the query parameters
    if not transcription_text and request.args.get('text'):
        transcription_text = request.args.get('text')

    return render_template('voice_transcription.html', transcription_text=transcription_text)

@fir_bp.route('/save-transcription', methods=['POST'])
@login_required
def save_transcription():
    """Save transcription to session"""
    try:
        data = request.get_json()
        if data and 'transcription' in data:
            session['voice_transcription'] = data['transcription']
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'No transcription provided'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@fir_bp.route('/transcribe-audio', methods=['POST'])
@login_required
def transcribe_audio_file():
    if 'audio' not in request.files:
        return jsonify({'error': 'No audio file provided'}), 400

    audio_file = request.files['audio']

    if audio_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Initialize temp_path
    temp_path = None

    try:
        # Get file extension safely
        if audio_file.filename and '.' in audio_file.filename:
            extension = audio_file.filename.rsplit('.', 1)[1].lower()
        else:
            extension = 'wav'  # Default extension

        # Save the uploaded file temporarily
        temp_path = tempfile.mktemp(suffix='.' + extension)
        audio_file.save(temp_path)

        # Transcribe the audio
        transcription = speech_recognizer.transcribe_audio(temp_path)

        # Clean up
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        if transcription:
            return jsonify({'transcription': transcription})
        else:
            return jsonify({'error': 'Failed to transcribe audio'}), 500
    except Exception as e:
        # Clean up in case of error
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass
        return jsonify({'error': f'Error processing audio: {str(e)}'}), 500


