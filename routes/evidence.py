"""
Routes for evidence management
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
import os
import json
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
import uuid

from models import db, FIR, Evidence, User
from utils.evidence_analyzer import extract_metadata, analyze_evidence, get_file_type, suggest_evidence_category, EVIDENCE_TYPES, CATEGORIES

# Configure logging
import logging
logger = logging.getLogger(__name__)

# Create blueprint
evidence_bp = Blueprint('evidence', __name__, url_prefix='/evidence')

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'tiff',  # Images
                         'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'xls', 'xlsx', 'csv',  # Documents
                         'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv', 'webm',  # Videos
                         'mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac'}  # Audio
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@evidence_bp.route('/manage/<int:fir_id>')
@login_required
def manage_evidence(fir_id):
    """
    Manage evidence for a specific FIR
    
    Args:
        fir_id: The ID of the FIR
    """
    # Get the FIR
    fir = FIR.query.get_or_404(fir_id)
    
    # Check if the user has permission to view this FIR
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to manage evidence for this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    # Get all evidence for this FIR
    evidence_items = Evidence.query.filter_by(fir_id=fir.id).all()
    
    return render_template('evidence/manage.html', fir=fir, evidence_items=evidence_items)

@evidence_bp.route('/view/<int:evidence_id>')
@login_required
def view_evidence(evidence_id):
    """
    View a specific evidence item
    
    Args:
        evidence_id: The ID of the evidence
    """
    # Get the evidence
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Get the FIR
    fir = FIR.query.get_or_404(evidence.fir_id)
    
    # Check if the user has permission to view this evidence
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to view this evidence.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    return render_template('evidence/view.html', evidence=evidence, fir=fir)

@evidence_bp.route('/upload/<int:fir_id>', methods=['POST'])
@login_required
def upload_evidence(fir_id):
    """
    Upload evidence for a specific FIR
    
    Args:
        fir_id: The ID of the FIR
    """
    # Get the FIR
    fir = FIR.query.get_or_404(fir_id)
    
    # Check if the user has permission to upload evidence for this FIR
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to upload evidence for this FIR.', 'danger')
        return redirect(url_for('fir.dashboard'))
    
    # Check if a file was uploaded
    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(request.url)
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(request.url)
    
    # Check if the file is allowed
    if file and allowed_file(file.filename):
        try:
            # Secure the filename
            original_filename = secure_filename(file.filename)
            
            # Generate a unique filename
            unique_filename = f"{uuid.uuid4()}_{original_filename}"
            
            # Create the upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.static_folder, 'uploads', 'evidence')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save the file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Determine the file type
            file_type = get_file_type(file_path)
            
            # Extract metadata
            metadata = extract_metadata(file_path)
            
            # Get form data
            description = request.form.get('description', '')
            category = request.form.get('category', '')
            tags = request.form.get('tags', '')
            location = request.form.get('location', '')
            collected_at_str = request.form.get('collected_at', '')
            analyze = 'analyze' in request.form
            
            # Parse collected_at if provided
            collected_at = None
            if collected_at_str:
                try:
                    collected_at = datetime.fromisoformat(collected_at_str)
                except ValueError:
                    logger.warning(f"Invalid collected_at format: {collected_at_str}")
            
            # Parse tags
            tags_list = []
            if tags:
                tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # If no category provided, suggest one
            if not category:
                category = suggest_evidence_category(file_type)
            
            # Create a new evidence record
            evidence = Evidence(
                fir_id=fir.id,
                type=file_type,
                file_path=os.path.join('static', 'uploads', 'evidence', unique_filename),
                description=description,
                category=category,
                location=location,
                collected_at=collected_at,
                uploaded_at=datetime.now(timezone.utc)
            )
            
            # Set tags and metadata
            evidence.set_tags(tags_list)
            evidence.set_metadata(metadata)
            
            # Add initial custody event
            evidence.add_custody_event(
                user_id=current_user.id,
                action="Evidence uploaded",
                notes=f"Uploaded by {current_user.username}"
            )
            
            # Save to database
            db.session.add(evidence)
            db.session.commit()
            
            # Analyze the evidence if requested
            if analyze:
                try:
                    analysis_result = analyze_evidence(file_path, file_type)
                    evidence.set_analysis(analysis_result)
                    
                    # Extract tags from analysis
                    if analysis_result and 'tags' in analysis_result:
                        new_tags = analysis_result['tags']
                        if new_tags:
                            current_tags = evidence.get_tags()
                            # Add new tags that aren't already in the list
                            for tag in new_tags:
                                if tag not in current_tags:
                                    current_tags.append(tag)
                            evidence.set_tags(current_tags)
                    
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error analyzing evidence: {str(e)}")
                    flash(f"Evidence uploaded but analysis failed: {str(e)}", 'warning')
            
            flash('Evidence uploaded successfully', 'success')
            return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))
        except Exception as e:
            logger.error(f"Error uploading evidence: {str(e)}")
            flash(f"Error uploading evidence: {str(e)}", 'danger')
            return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))
    else:
        flash('File type not allowed', 'danger')
        return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))

@evidence_bp.route('/delete/<int:evidence_id>', methods=['POST'])
@login_required
def delete_evidence(evidence_id):
    """
    Delete a specific evidence item
    
    Args:
        evidence_id: The ID of the evidence
    """
    # Get the evidence
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Get the FIR
    fir = FIR.query.get_or_404(evidence.fir_id)
    
    # Check if the user has permission to delete this evidence
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id):
        flash('You do not have permission to delete this evidence.', 'danger')
        return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))
    
    try:
        # Delete the file if it exists
        if evidence.file_path and os.path.exists(evidence.file_path):
            os.remove(evidence.file_path)
        
        # Delete the evidence record
        db.session.delete(evidence)
        db.session.commit()
        
        flash('Evidence deleted successfully', 'success')
    except Exception as e:
        logger.error(f"Error deleting evidence: {str(e)}")
        flash(f"Error deleting evidence: {str(e)}", 'danger')
    
    return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))

@evidence_bp.route('/edit/<int:evidence_id>', methods=['GET', 'POST'])
@login_required
def edit_evidence(evidence_id):
    """
    Edit a specific evidence item
    
    Args:
        evidence_id: The ID of the evidence
    """
    # Get the evidence
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Get the FIR
    fir = FIR.query.get_or_404(evidence.fir_id)
    
    # Check if the user has permission to edit this evidence
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to edit this evidence.', 'danger')
        return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))
    
    if request.method == 'POST':
        try:
            # Update evidence details
            evidence.description = request.form.get('description', '')
            evidence.category = request.form.get('category', '')
            evidence.location = request.form.get('location', '')
            
            # Parse collected_at if provided
            collected_at_str = request.form.get('collected_at', '')
            if collected_at_str:
                try:
                    evidence.collected_at = datetime.fromisoformat(collected_at_str)
                except ValueError:
                    logger.warning(f"Invalid collected_at format: {collected_at_str}")
            
            # Parse tags
            tags = request.form.get('tags', '')
            if tags:
                tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
                evidence.set_tags(tags_list)
            else:
                evidence.tags = None
            
            # Add custody event
            evidence.add_custody_event(
                user_id=current_user.id,
                action="Evidence details updated",
                notes=f"Updated by {current_user.username}"
            )
            
            # Save changes
            db.session.commit()
            
            flash('Evidence updated successfully', 'success')
            return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))
        except Exception as e:
            logger.error(f"Error updating evidence: {str(e)}")
            flash(f"Error updating evidence: {str(e)}", 'danger')
            return redirect(url_for('evidence.edit_evidence', evidence_id=evidence.id))
    
    # Prepare tags for display
    tags_string = ', '.join(evidence.get_tags()) if evidence.tags else ''
    
    return render_template('evidence/edit.html', evidence=evidence, fir=fir, tags_string=tags_string)

@evidence_bp.route('/analyze/<int:evidence_id>')
@login_required
def analyze_evidence_route(evidence_id):
    """
    Analyze a specific evidence item
    
    Args:
        evidence_id: The ID of the evidence
    """
    # Get the evidence
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Get the FIR
    fir = FIR.query.get_or_404(evidence.fir_id)
    
    # Check if the user has permission to analyze this evidence
    if not (current_user.is_admin() or current_user.is_police() or 
            fir.complainant_id == current_user.id or
            fir.processing_officer_id == current_user.id):
        flash('You do not have permission to analyze this evidence.', 'danger')
        return redirect(url_for('evidence.manage_evidence', fir_id=fir.id))
    
    try:
        # Check if the file exists
        if not evidence.file_path or not os.path.exists(evidence.file_path):
            flash('Evidence file not found', 'danger')
            return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))
        
        # Analyze the evidence
        analysis_result = analyze_evidence(evidence.file_path, evidence.type)
        evidence.set_analysis(analysis_result)
        
        # Extract tags from analysis
        if analysis_result and 'tags' in analysis_result:
            new_tags = analysis_result['tags']
            if new_tags:
                current_tags = evidence.get_tags()
                # Add new tags that aren't already in the list
                for tag in new_tags:
                    if tag not in current_tags:
                        current_tags.append(tag)
                evidence.set_tags(current_tags)
        
        # Add custody event
        evidence.add_custody_event(
            user_id=current_user.id,
            action="Evidence analyzed",
            notes=f"Analyzed by {current_user.username}"
        )
        
        # Save changes
        db.session.commit()
        
        flash('Evidence analyzed successfully', 'success')
    except Exception as e:
        logger.error(f"Error analyzing evidence: {str(e)}")
        flash(f"Error analyzing evidence: {str(e)}", 'danger')
    
    return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))

@evidence_bp.route('/verify/<int:evidence_id>')
@login_required
def verify_evidence(evidence_id):
    """
    Verify a specific evidence item
    
    Args:
        evidence_id: The ID of the evidence
    """
    # Get the evidence
    evidence = Evidence.query.get_or_404(evidence_id)
    
    # Get the FIR
    fir = FIR.query.get_or_404(evidence.fir_id)
    
    # Check if the user has permission to verify this evidence
    if not (current_user.is_admin() or current_user.is_police()):
        flash('Only administrators and police officers can verify evidence.', 'danger')
        return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))
    
    try:
        # Toggle verification status
        evidence.is_verified = not evidence.is_verified
        
        # Add custody event
        action = "Evidence verified" if evidence.is_verified else "Evidence verification removed"
        evidence.add_custody_event(
            user_id=current_user.id,
            action=action,
            notes=f"{action} by {current_user.username}"
        )
        
        # Save changes
        db.session.commit()
        
        flash(f'Evidence {action.lower()} successfully', 'success')
    except Exception as e:
        logger.error(f"Error verifying evidence: {str(e)}")
        flash(f"Error verifying evidence: {str(e)}", 'danger')
    
    return redirect(url_for('evidence.view_evidence', evidence_id=evidence.id))
