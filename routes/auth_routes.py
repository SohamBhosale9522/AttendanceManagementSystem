from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_db_cursor
from utils.security import verify_password, hash_password

auth_bp = Blueprint('auth', __name__)

# Fallback seed credentials if Faculty_User table is not yet migrated to cloud database
SEED_FACULTY = {
    'faculty1': {
        'user_id': 1,
        'username': 'faculty1',
        # Faculty@123
        'password_hash': 'scrypt:32768:8:1$UBXHpqe650NhvgzO$1304ad2c00815eb49deeea7788422186c8f7dca08981e7ee729577640dbaf3308c147f4e280ff8f1360ce04dfd96815a1c5d44d4c208de3ae908da31ba1c197d',
        'full_name': 'Prof. Mehta',
        'email': 'mehta@college.edu',
        'role': 'faculty'
    },
    'admin': {
        'user_id': 2,
        'username': 'admin',
        # Admin@123
        'password_hash': 'scrypt:32768:8:1$yrMPfQqBxytHVDix$9e932cd97b76df32f8768325e3638de067b300c4550cefe926e7c9862ec0a6fbcd78129b62e8ea2021525eb2c252cb08ac95ec65987100d26200b2f67facd8bf',
        'full_name': 'Administrator',
        'email': 'admin@college.edu',
        'role': 'admin'
    }
}

def ensure_faculty_table():
    """Attempts to auto-create Faculty_User table and seed users if permitted."""
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "CREATE TABLE IF NOT EXISTS Faculty_User ("
                "user_id INT AUTO_INCREMENT PRIMARY KEY, "
                "username VARCHAR(50) NOT NULL UNIQUE, "
                "password_hash VARCHAR(255) NOT NULL, "
                "full_name VARCHAR(100) NOT NULL, "
                "email VARCHAR(100), "
                "role VARCHAR(20) DEFAULT 'faculty', "
                "created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
            )
            cursor.execute("SELECT COUNT(*) AS cnt FROM Faculty_User")
            if cursor.fetchone()['cnt'] == 0:
                for u in SEED_FACULTY.values():
                    cursor.execute(
                        "INSERT IGNORE INTO Faculty_User (username, password_hash, full_name, email, role) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (u['username'], u['password_hash'], u['full_name'], u['email'], u['role'])
                    )
    except Exception:
        pass

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash("Please enter both username and password.", "danger")
            return render_template('login.html', username=username)
            
        user = None
        # Try database first
        try:
            ensure_faculty_table()
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT user_id, username, password_hash, full_name, email, role "
                    "FROM Faculty_User WHERE username = %s LIMIT 1",
                    (username,)
                )
                user = cursor.fetchone()
        except Exception:
            # Fallback to seed accounts if database table not yet present
            if username in SEED_FACULTY:
                user = SEED_FACULTY[username]
                
        # If database query yielded nothing, also check seed fallback
        if not user and username in SEED_FACULTY:
            user = SEED_FACULTY[username]
            
        if user and verify_password(user['password_hash'], password):
            # Set session variables
            session.clear()
            session['user_id'] = user['user_id']
            session['username'] = user['username']
            session['full_name'] = user['full_name']
            session['email'] = user.get('email', '')
            session['role'] = user.get('role', 'faculty')
            
            flash(f"Welcome back, {user['full_name']}!", "success")
            next_url = request.args.get('next')
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect(url_for('dashboard.index'))
        else:
            flash("Invalid username or password.", "danger")
            
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash("You have been signed out successfully. Goodbye!", "info")
    return redirect(url_for('auth.login'))
