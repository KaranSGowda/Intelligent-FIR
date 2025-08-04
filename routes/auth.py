# Add session test route after Blueprint is defined

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from models import User, Role
import logging

# Configure logging
logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)

# Add session test route after Blueprint is defined
@auth_bp.route('/session_test')
def session_test():
    from flask_login import current_user
    if current_user.is_authenticated:
        return f"[SESSION TEST] Logged in as: {current_user.username} (role: {current_user.role})"
    else:
        return "[SESSION TEST] Not logged in."

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        print("[DEBUG] User already authenticated, redirecting to dashboard")
        return redirect(url_for('fir.dashboard'))

    print("[DEBUG] Login page accessed, method:", request.method)

    if request.method == 'POST':
        print("[DEBUG] Login form submitted")
        from models import User, Role
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        print(f"[DEBUG] Login attempt: username={username}")

        # Input validation
        if not username or not password:
            print("[DEBUG] Missing username or password")
            flash('Username and password are required.', 'danger')
            return render_template('login.html')

        try:
            print("[DEBUG] Querying user from database...")
            user = User.query.filter_by(username=username).first()
            if not user:
                print("[DEBUG] User not found")
                flash('Incorrect username or password.', 'danger')
                return render_template('login.html')
            else:
                print(f"[DEBUG] User found: {user.username}, role={user.role}")

            print("[DEBUG] Checking password...")
            if not user.check_password(password):
                print("[DEBUG] Incorrect password")
                flash('Incorrect username or password.', 'danger')
                return render_template('login.html')
            else:
                print("[DEBUG] Password check passed")
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            print(f"[DEBUG] Login error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return render_template('login.html')

        try:
            print("[DEBUG] Logging in user...")
            login_user(user, remember=True)
            logger.info(f"User {username} logged in successfully with role {user.role}")
            print(f"[DEBUG] User {username} logged in successfully with role {user.role}")
            flash('Logged in successfully.', 'success')

            # Redirect based on user's actual role
            if user.is_admin():
                print("[DEBUG] Redirecting to admin dashboard")
                return redirect(url_for('admin.dashboard'))
            elif user.is_police():
                print("[DEBUG] Redirecting to admin cases")
                return redirect(url_for('admin.cases'))
            else:  # Public user
                print("[DEBUG] Redirecting to fir dashboard")
                return redirect(url_for('fir.dashboard'))
        except Exception as e:
            logger.error(f"Login session error: {str(e)}")
            print(f"[DEBUG] Login session error: {str(e)}")
            flash('An error occurred during login. Please try again.', 'danger')
            return render_template('login.html')

    print("[DEBUG] Rendering login page (GET or failed POST)")
    return render_template('login.html')

    # ...existing register logic here...

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
        from models import User, Role
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        role = request.form.get('role', 'public').strip().lower()

        print(f"[DEBUG] Registration attempt: username={username}, email={email}, role={role}")

        # Input validation
        if not username or not email or not password or not full_name:
            print("[DEBUG] Missing required fields")
            flash('Username, email, password, and full name are required.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            print("[DEBUG] Password too short")
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        # Basic email validation
        if '@' not in email or '.' not in email:
            print("[DEBUG] Invalid email format")
            flash('Please enter a valid email address.', 'danger')
            return render_template('register.html')

        if role not in [Role.PUBLIC, Role.POLICE, Role.ADMIN]:
            print(f"[DEBUG] Invalid role: {role}")
            flash('Invalid role selected.', 'danger')
            return render_template('register.html')

        try:
            # Check if username or email already exists
            user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
            if user_exists:
                print("[DEBUG] Username or email already exists")
                flash('Username or email already exists.', 'danger')
                return render_template('register.html')
        except Exception as e:
            logger.error(f"Registration validation error: {str(e)}")
            print(f"[DEBUG] Registration validation error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')

        try:
            user = User()
            user.username = username
            user.email = email
            user.full_name = full_name
            user.role = role
            user.phone = phone if phone else None
            user.address = address if address else None
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            print(f"[DEBUG] Registration successful for {username}")
            flash(f'Registration successful! You can now log in as a {role} user.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            logger.error(f"Registration error: {str(e)}")
            print(f"[DEBUG] Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return render_template('register.html')

    # Add message explaining that this is for public users only
    flash('This registration form is for public users only. Police and admin accounts are created by administrators.', 'info')
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        username = current_user.username if current_user.is_authenticated else 'Unknown'
        logout_user()
        logger.info(f"User {username} logged out successfully")
        flash('Logged out successfully.', 'success')
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        flash('Logged out.', 'info')  # Still show success message to user

    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        try:
            # Get form data with validation
            full_name = request.form.get('full_name', '').strip()
            email = request.form.get('email', '').strip()
            phone = request.form.get('phone', '').strip()
            address = request.form.get('address', '').strip()
            password = request.form.get('password', '')

            # Validate required fields
            if not full_name or not email:
                flash('Full name and email are required.', 'danger')
                return render_template('profile.html', user=current_user)

            # Basic email validation
            if '@' not in email or '.' not in email:
                flash('Please enter a valid email address.', 'danger')
                return render_template('profile.html', user=current_user)

            # Check if email is already taken by another user
            existing_user = User.query.filter(User.email == email, User.id != current_user.id).first()
            if existing_user:
                flash('Email address is already in use by another account.', 'danger')
                return render_template('profile.html', user=current_user)

            # Update user information
            current_user.full_name = full_name
            current_user.email = email
            current_user.phone = phone if phone else None
            current_user.address = address if address else None

            # Check if password is being updated
            if password and password.strip():
                if len(password) < 6:
                    flash('Password must be at least 6 characters long.', 'danger')
                    return render_template('profile.html', user=current_user)
                current_user.set_password(password)

            db.session.commit()
            flash('Profile updated successfully.', 'success')
        except Exception as e:
            db.session.rollback()
            logger.error(f"Profile update error: {str(e)}")
            flash('An error occurred while updating your profile. Please try again.', 'danger')

    return render_template('profile.html', user=current_user)
