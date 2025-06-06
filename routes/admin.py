from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import User, FIR, Role
from utils.legal_mapper import initialize_legal_sections
import os
from werkzeug.utils import secure_filename
import pandas as pd

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.before_request
def check_admin():
    """Ensure only admin and police can access admin routes"""
    if not current_user.is_authenticated or (not current_user.is_admin() and not current_user.is_police()):
        flash('Access denied. You must be an administrator or police officer.', 'danger')
        return redirect(url_for('fir.dashboard'))

@admin_bp.route('/')
@login_required
def dashboard():
    """Admin dashboard with summary statistics"""
    # Initialize legal sections if needed
    initialize_legal_sections()

    # Get statistics
    total_firs = FIR.query.count()
    pending_firs = FIR.query.filter_by(status='filed').count()
    investigating_firs = FIR.query.filter_by(status='under_investigation').count()
    closed_firs = FIR.query.filter_by(status='closed').count()
    total_users = User.query.filter_by(role=Role.PUBLIC).count()

    # Get recent FIRs
    recent_firs = FIR.query.order_by(FIR.filed_at.desc()).limit(5).all()

    # Get urgent cases
    urgent_cases = FIR.query.filter(
        FIR.urgency_level.in_(['high', 'critical']),
        FIR.status.in_(['filed', 'under_investigation'])
    ).all()

    return render_template(
        'admin/dashboard.html',
        total_firs=total_firs,
        pending_firs=pending_firs,
        investigating_firs=investigating_firs,
        closed_firs=closed_firs,
        total_users=total_users,
        recent_firs=recent_firs,
        urgent_cases=urgent_cases
    )

@admin_bp.route('/cases')
@login_required
def cases():
    """List all FIR cases with filtering options"""
    status_filter = request.args.get('status', '')
    urgency_filter = request.args.get('urgency', '')

    # Build the query
    query = FIR.query

    # Apply filters
    if status_filter:
        query = query.filter_by(status=status_filter)

    if urgency_filter:
        query = query.filter_by(urgency_level=urgency_filter)

    # For police users who are not admins, only show assigned cases
    if current_user.is_police() and not current_user.is_admin():
        query = query.filter_by(processing_officer_id=current_user.id)

    # Get sorted results
    firs = query.order_by(FIR.filed_at.desc()).all()

    return render_template(
        'admin/cases.html',
        firs=firs,
        status_filter=status_filter,
        urgency_filter=urgency_filter
    )

@admin_bp.route('/users')
@login_required
def users():
    """Manage users (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    role_filter = request.args.get('role', '')

    # Build the query
    query = User.query

    # Apply filters
    if role_filter:
        query = query.filter_by(role=role_filter)

    # Get sorted results
    users = query.order_by(User.created_at.desc()).all()

    return render_template(
        'admin/users.html',
        users=users,
        role_filter=role_filter
    )

@admin_bp.route('/assign/<int:fir_id>', methods=['POST'])
@login_required
def assign_case(fir_id):
    """Assign a case to a police officer"""
    fir = FIR.query.get_or_404(fir_id)

    officer_id = request.form.get('officer_id')
    if not officer_id:
        flash('No officer selected.', 'danger')
        return redirect(url_for('admin.cases'))

    try:
        # Validate that the selected user is a police officer
        officer = User.query.get(officer_id)
        if not officer or not officer.is_police():
            flash('Invalid officer selection.', 'danger')
            return redirect(url_for('admin.cases'))

        # Assign the case
        fir.processing_officer_id = officer.id

        # Update status if needed
        if fir.status == 'filed':
            fir.status = 'under_investigation'

        db.session.commit()
        flash(f'Case assigned to {officer.full_name} successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error assigning case: {str(e)}', 'danger')

    return redirect(url_for('admin.cases'))

@admin_bp.route('/update_user/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user details and role (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    user = User.query.get_or_404(user_id)

    try:
        user.role = request.form.get('role', user.role)
        user.full_name = request.form.get('full_name', user.full_name)
        user.email = request.form.get('email', user.email)
        user.phone = request.form.get('phone', user.phone)
        user.address = request.form.get('address', user.address)

        # Check if password is being updated
        password = request.form.get('password')
        if password and password.strip():
            user.set_password(password)

        db.session.commit()
        flash('User updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating user: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    if not current_user.is_admin():
        flash('Access denied. Admin privileges required.', 'danger')
        return redirect(url_for('admin.dashboard'))

    # Prevent deleting oneself
    if user_id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))

    user = User.query.get_or_404(user_id)

    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting user: {str(e)}', 'danger')

    return redirect(url_for('admin.users'))

@admin_bp.route('/get_officers')
@login_required
def get_officers():
    """API to get all police officers"""
    officers = User.query.filter_by(role=Role.POLICE).all()
    officers_data = [{'id': officer.id, 'name': officer.full_name} for officer in officers]
    return jsonify(officers_data)

@admin_bp.route('/upload_users', methods=['GET', 'POST'])
@login_required
def upload_users():
    if not current_user.is_admin():
        flash('Only admins can upload users.', 'danger')
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        file = request.files.get('excel_file')
        if not file:
            flash('Please select a file.', 'danger')
            return render_template('admin_upload_users.html')
        filename = file.filename or ''
        if not (filename.endswith('.xlsx') or filename.endswith('.csv')):
            flash('Only .xlsx or .csv files are supported.', 'danger')
            return render_template('admin_upload_users.html')
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(file.stream)
            else:
                df = pd.read_excel(file.stream)
            # Support police_users_template.csv format
            if {'username', 'password', 'role'}.issubset(df.columns):
                created, skipped = 0, 0
                for _, row in df.iterrows():
                    if User.query.filter_by(username=row['username']).first():
                        skipped += 1
                        continue
                    user = User()
                    user.username = row['username']
                    user.full_name = row['name'] if 'name' in df.columns else ''
                    user.phone = str(row['mobile']) if 'mobile' in df.columns else ''
                    user.role = row['role']
                    user.set_password(str(row['password']))
                    user.email = ''
                    user.address = ''
                    db.session.add(user)
                    created += 1
                db.session.commit()
                flash(f'Successfully created {created} users. Skipped {skipped} existing.', 'success')
            else:
                flash('File must contain at least columns: username, password, role', 'danger')
                return render_template('admin_upload_users.html')
        except Exception as e:
            db.session.rollback()
            flash(f'Error processing file: {str(e)}', 'danger')
        return redirect(url_for('admin.upload_users'))
    return render_template('admin_upload_users.html')
