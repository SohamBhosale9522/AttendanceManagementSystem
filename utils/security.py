import secrets
from functools import wraps
from flask import session, redirect, url_for, flash, request, abort
from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hashes a plaintext password using scrypt or pbkdf2."""
    return generate_password_hash(password)

def verify_password(stored_hash: str, password: str) -> bool:
    """Verifies a plaintext password against the stored hash."""
    if not stored_hash or not password:
        return False
    return check_password_hash(stored_hash, password)

def generate_csrf_token():
    """Generates a unique CSRF token for the current session."""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(32)
    return session['_csrf_token']

def validate_csrf():
    """Validates the CSRF token on mutating HTTP methods (POST, PUT, DELETE, PATCH)."""
    if request.method in ('POST', 'PUT', 'DELETE', 'PATCH'):
        token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
        expected = session.get('_csrf_token')
        if not expected or not token or not secrets.compare_digest(token, expected):
            abort(400, description="Invalid or missing CSRF token. Please refresh the page and try again.")

def login_required(f):
    """Decorator to require login for routes."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require administrator role."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('auth.login', next=request.url))
        if session.get('role') != 'admin':
            flash("Administrator privileges are required for this action.", "danger")
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function
