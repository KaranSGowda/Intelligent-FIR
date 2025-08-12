import os
import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import FIR, Evidence, User, Role
from models import __dict__ as models_dict
import models
from utils.openai_helper import map_legal_sections, analyze_image
from utils.ml_analyzer import analyze_complaint
from utils.legal_mapper import get_legal_sections_for_fir
from utils.pdf_generator import generate_fir_pdf, generate_fir_pdf_simple, generate_and_store_fir_pdf
import tempfile
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)

fir_bp = Blueprint('fir', __name__, url_prefix='/fir')

# ...existing code...

@fir_bp.route('/transcribe_whisper', methods=['POST'])
@login_required
def transcribe_whisper():
    """Accepts an audio file upload, transcribes it using OpenAI Whisper, and returns the text."""
    try:
        import whisper
        audio = request.files.get('audio')
        if not audio:
            return jsonify({'success': False, 'error': 'No audio file uploaded.'}), 400
        # Save to a temp file
        temp_dir = tempfile.mkdtemp()
        audio_path = os.path.join(temp_dir, secure_filename(audio.filename or 'audio.webm'))
        audio.save(audio_path)
        # Get language from form (optional)
        language = request.form.get('language', 'auto')
        model = whisper.load_model('base')
        transcribe_args = {'task': 'transcribe'}
        if language and language != 'auto':
            transcribe_args['language'] = language
        result = model.transcribe(audio_path, **transcribe_args)
        text = result.get('text', '')
        # Clean up temp file
        try:
            os.remove(audio_path)
            os.rmdir(temp_dir)
        except Exception:
            pass
        return jsonify({'success': True, 'text': text})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
import os
import json
import uuid
from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import FIR, Evidence, User, Role
from models import __dict__ as models_dict
import models
from utils.openai_helper import map_legal_sections, analyze_image
from utils.ml_analyzer import analyze_complaint
from utils.legal_mapper import get_legal_sections_for_fir
from utils.pdf_generator import generate_fir_pdf, generate_fir_pdf_simple, generate_and_store_fir_pdf
import tempfile
import logging
import queue
import threading
import time

logger = logging.getLogger(__name__)

fir_bp = Blueprint('fir', __name__, url_prefix='/fir')

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

            # Regular form submission - create a new FIR
            try:
                incident_description = request.form.get('incident_description', '')

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
                            evidence.file_path = f"uploads/images/{filename}"  # Store web-compatible path
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
        # For now, always generate a new PDF to avoid database issues
        # TODO: Implement PDF caching once database schema is stable
        logger.info(f"Generating new PDF for FIR {fir.fir_number}")

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

        # For now, skip storing PDF path in database to avoid schema issues
        # TODO: Implement PDF path storage once database schema is stable
        logger.info(f"Generated PDF for FIR {fir.fir_number}: {pdf_path}")

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



@fir_bp.route('/add_note/<int:fir_id>', methods=['POST'])
@login_required
def add_investigation_note(fir_id):
    """Add an investigation note to a FIR (police/admin only)"""
    fir = FIR.query.get_or_404(fir_id)
    # Only admin or assigned police officer can add notes
    if not (current_user.is_admin() or (current_user.is_police() and fir.processing_officer_id == current_user.id)):
        msg = 'You do not have permission to add investigation notes to this FIR.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=msg), 403
        flash(msg, 'danger')
        return redirect(url_for('fir.view_fir', fir_id=fir.id))

    note_content = request.form.get('note_content', '').strip()
    if not note_content:
        msg = 'Note content cannot be empty.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=msg), 400
        flash(msg, 'warning')
        return redirect(url_for('fir.view_fir', fir_id=fir.id))

    InvestigationNoteModel = models_dict.get('InvestigationNote')
    if not InvestigationNoteModel:
        msg = 'InvestigationNote model not found.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=msg), 500
        flash(msg, 'danger')
        return redirect(url_for('fir.view_fir', fir_id=fir.id))
    note = InvestigationNoteModel(
        fir_id=fir.id,
        officer_id=current_user.id,
        content=note_content
    )
    try:
        db.session.add(note)
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=True, note={
                'content': note.content,
                'author': current_user.full_name,
                'created_at': note.created_at.strftime('%d-%m-%Y %H:%M')
            })
        flash('Investigation note added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        msg = f'Error adding note: {str(e)}'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=msg), 500
        flash(msg, 'danger')
    return redirect(url_for('fir.view_fir', fir_id=fir.id))

@fir_bp.route('/view/<int:fir_id>/delete_note', methods=['POST'])
@login_required
def delete_investigation_note(fir_id):
    fir = FIR.query.get_or_404(fir_id)
    # Only admin or assigned police officer can delete notes
    if not (current_user.is_admin() or (current_user.is_police() and fir.processing_officer_id == current_user.id)):
        msg = 'You do not have permission to delete investigation notes for this FIR.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(success=False, message=msg), 403
        flash(msg, 'danger')
        return redirect(url_for('fir.view_fir', fir_id=fir.id))

    data = request.get_json()
    note_index = data.get('index')
    if note_index is None:
        return jsonify(success=False, message='Invalid note index.'), 400

    notes = fir.investigation_notes
    if note_index < 0 or note_index >= len(notes):
        return jsonify(success=False, message='Note not found.'), 404

    note = notes[note_index]
    try:
        db.session.delete(note)
        db.session.commit()
        return jsonify(success=True)
    except Exception as e:
        db.session.rollback()
        return jsonify(success=False, message=f'Error deleting note: {str(e)}'), 500


