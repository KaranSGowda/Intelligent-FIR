"""
Routes for legal section management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
import json
import logging

from models import db, LegalSection, FIR
from utils.legal_mapper import initialize_legal_sections
from utils.ml_analyzer import train_model, analyze_complaint

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
legal_sections_bp = Blueprint('legal_sections', __name__, url_prefix='/legal-sections')

@legal_sections_bp.route('/')
@login_required
def index():
    """
    Display all legal sections
    """
    # Only admin and police can access this page
    if not (current_user.is_admin() or current_user.is_police()):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    # Get all legal sections
    sections = LegalSection.query.order_by(LegalSection.code).all()
    
    return render_template('legal_sections/index.html', sections=sections)

@legal_sections_bp.route('/view/<int:section_id>')
@login_required
def view(section_id):
    """
    View a specific legal section
    """
    # Only admin and police can access this page
    if not (current_user.is_admin() or current_user.is_police()):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    # Get the section
    section = LegalSection.query.get_or_404(section_id)
    
    # Get FIRs that reference this section
    firs_with_section = []
    all_firs = FIR.query.filter(FIR.legal_sections.isnot(None)).all()
    
    for fir in all_firs:
        try:
            sections = json.loads(fir.legal_sections)
            for s in sections:
                if s.get('code') == section.code:
                    firs_with_section.append({
                        'fir': fir,
                        'confidence': s.get('confidence', 0),
                        'relevance': s.get('relevance', '')
                    })
                    break
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Sort by confidence (descending)
    firs_with_section.sort(key=lambda x: x['confidence'], reverse=True)
    
    return render_template('legal_sections/view.html', section=section, firs=firs_with_section)

@legal_sections_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """
    Create a new legal section
    """
    # Only admin can create sections
    if not current_user.is_admin():
        flash('You do not have permission to create legal sections.', 'danger')
        return redirect(url_for('legal_sections.index'))
    
    if request.method == 'POST':
        code = request.form.get('code')
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Validate input
        if not code or not name:
            flash('Code and name are required.', 'danger')
            return render_template('legal_sections/create.html')
        
        # Check if section already exists
        existing_section = LegalSection.query.filter_by(code=code).first()
        if existing_section:
            flash(f'Section with code {code} already exists.', 'danger')
            return render_template('legal_sections/create.html')
        
        # Create new section
        section = LegalSection(
            code=code,
            name=name,
            description=description
        )
        
        try:
            db.session.add(section)
            db.session.commit()
            flash('Legal section created successfully.', 'success')
            return redirect(url_for('legal_sections.index'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating legal section: {str(e)}")
            flash(f'Error creating legal section: {str(e)}', 'danger')
            return render_template('legal_sections/create.html')
    
    return render_template('legal_sections/create.html')

@legal_sections_bp.route('/edit/<int:section_id>', methods=['GET', 'POST'])
@login_required
def edit(section_id):
    """
    Edit a legal section
    """
    # Only admin can edit sections
    if not current_user.is_admin():
        flash('You do not have permission to edit legal sections.', 'danger')
        return redirect(url_for('legal_sections.index'))
    
    # Get the section
    section = LegalSection.query.get_or_404(section_id)
    
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Validate input
        if not name:
            flash('Name is required.', 'danger')
            return render_template('legal_sections/edit.html', section=section)
        
        # Update section
        section.name = name
        section.description = description
        
        try:
            db.session.commit()
            flash('Legal section updated successfully.', 'success')
            return redirect(url_for('legal_sections.view', section_id=section.id))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating legal section: {str(e)}")
            flash(f'Error updating legal section: {str(e)}', 'danger')
            return render_template('legal_sections/edit.html', section=section)
    
    return render_template('legal_sections/edit.html', section=section)

@legal_sections_bp.route('/delete/<int:section_id>', methods=['POST'])
@login_required
def delete(section_id):
    """
    Delete a legal section
    """
    # Only admin can delete sections
    if not current_user.is_admin():
        flash('You do not have permission to delete legal sections.', 'danger')
        return redirect(url_for('legal_sections.index'))
    
    # Get the section
    section = LegalSection.query.get_or_404(section_id)
    
    try:
        db.session.delete(section)
        db.session.commit()
        flash('Legal section deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting legal section: {str(e)}")
        flash(f'Error deleting legal section: {str(e)}', 'danger')
    
    return redirect(url_for('legal_sections.index'))

@legal_sections_bp.route('/initialize', methods=['POST'])
@login_required
def initialize():
    """
    Initialize the database with common IPC sections
    """
    # Only admin can initialize sections
    if not current_user.is_admin():
        flash('You do not have permission to initialize legal sections.', 'danger')
        return redirect(url_for('legal_sections.index'))
    
    try:
        initialize_legal_sections()
        flash('Legal sections initialized successfully.', 'success')
    except Exception as e:
        logger.error(f"Error initializing legal sections: {str(e)}")
        flash(f'Error initializing legal sections: {str(e)}', 'danger')
    
    return redirect(url_for('legal_sections.index'))

@legal_sections_bp.route('/train-model', methods=['POST'])
@login_required
def train_ml_model():
    """
    Train the ML model for legal section classification
    """
    # Only admin can train the model
    if not current_user.is_admin():
        flash('You do not have permission to train the ML model.', 'danger')
        return redirect(url_for('legal_sections.index'))
    
    try:
        success = train_model()
        if success:
            flash('ML model trained successfully.', 'success')
        else:
            flash('Error training ML model.', 'danger')
    except Exception as e:
        logger.error(f"Error training ML model: {str(e)}")
        flash(f'Error training ML model: {str(e)}', 'danger')
    
    return redirect(url_for('legal_sections.index'))

@legal_sections_bp.route('/analyze', methods=['GET', 'POST'])
@login_required
def analyze():
    """
    Analyze a complaint text and show applicable legal sections
    """
    # Only admin and police can access this page
    if not (current_user.is_admin() or current_user.is_police()):
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    if request.method == 'POST':
        complaint_text = request.form.get('complaint_text')
        
        if not complaint_text:
            flash('Complaint text is required.', 'danger')
            return render_template('legal_sections/analyze.html')
        
        try:
            # Analyze the complaint
            analysis = analyze_complaint(complaint_text)
            sections = analysis.get('sections', [])
            
            return render_template('legal_sections/analyze.html', 
                                  complaint_text=complaint_text, 
                                  sections=sections,
                                  analyzed=True)
        except Exception as e:
            logger.error(f"Error analyzing complaint: {str(e)}")
            flash(f'Error analyzing complaint: {str(e)}', 'danger')
            return render_template('legal_sections/analyze.html', complaint_text=complaint_text)
    
    return render_template('legal_sections/analyze.html')

@legal_sections_bp.route('/api/analyze', methods=['POST'])
@login_required
def api_analyze():
    """
    API endpoint to analyze a complaint text
    """
    # Only admin and police can access this API
    if not (current_user.is_admin() or current_user.is_police()):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    complaint_text = data.get('complaint_text')
    
    if not complaint_text:
        return jsonify({'error': 'Complaint text is required'}), 400
    
    try:
        # Analyze the complaint
        analysis = analyze_complaint(complaint_text)
        return jsonify(analysis)
    except Exception as e:
        logger.error(f"Error analyzing complaint: {str(e)}")
        return jsonify({'error': str(e)}), 500
