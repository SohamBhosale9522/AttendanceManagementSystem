from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.db import get_db_cursor
from utils.security import verify_password, hash_password

auth_bp = Blueprint('auth', __name__)

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
            
        try:
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT user_id, username, password_hash, full_name, email, role "
                    "FROM Faculty_User WHERE username = %s LIMIT 1",
                    (username,)
                )
                user = cursor.fetchone()
                
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
        except Exception as e:
            flash(f"Authentication system error: {str(e)}", "danger")
            
    return render_template('login.html')

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    username = session.get('full_name', 'User')
    session.clear()
    flash(f"You have been signed out successfully. Goodbye!", "info")
    return redirect(url_for('auth.login'))
