from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from extensions import db
from models import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('fir.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        selected_role = request.form.get('login_as', 'public')  # Default to public if not specified

        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            flash('Invalid username or password.', 'danger')
            return render_template('login.html')

        # Check if user has permission for the selected role
        if (selected_role == 'admin' and not user.is_admin()) or \
           (selected_role == 'police' and not user.is_police()):
            flash('You do not have permission to log in with the selected role.', 'danger')
            return render_template('login.html')

        login_user(user)
        flash('Logged in successfully.', 'success')

        # Redirect based on selected role
        if selected_role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif selected_role == 'police':
            return redirect(url_for('admin.cases'))
        else:  # Public user
            return redirect(url_for('fir.dashboard'))

    return render_template('login.html')

@auth_bp.route('/role-select')
@login_required
def role_select():
    """Allow users to select which role they want to use"""
    # If the user only has one role, redirect directly
    if current_user.is_public() and not current_user.is_police() and not current_user.is_admin():
        return redirect(url_for('fir.dashboard'))
    elif current_user.is_police() and not current_user.is_admin():
        return redirect(url_for('admin.cases'))
    elif current_user.is_admin() and not current_user.is_police():
        return redirect(url_for('admin.dashboard'))

    # Otherwise, show the role selection page
    return render_template('role_select.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('fir.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')
        address = request.form.get('address')

        # Check if username or email already exists
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))

        # Create new user (always as a public user through registration page)
        new_user = User(
            username=username,
            email=email,
            full_name=full_name,
            phone=phone,
            address=address,
            role=Role.PUBLIC
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in as a public user.', 'success')
        return redirect(url_for('auth.login'))

    # Add message explaining that this is for public users only
    flash('This registration form is for public users only. Police and admin accounts are created by administrators.', 'info')
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name')
        current_user.email = request.form.get('email')
        current_user.phone = request.form.get('phone')
        current_user.address = request.form.get('address')

        # Check if password is being updated
        password = request.form.get('password')
        if password and password.strip():
            current_user.set_password(password)

        db.session.commit()
        flash('Profile updated successfully.', 'success')

    return render_template('profile.html', user=current_user)
