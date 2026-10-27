import os
from datetime import datetime
from flask import Flask, render_template, session
from config import Config
from utils.security import generate_csrf_token, validate_csrf

# Import route blueprints
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.student_routes import student_bp
from routes.course_routes import course_bp
from routes.attendance_routes import attendance_bp
from routes.defaulter_routes import defaulter_bp
from routes.leave_routes import leave_bp
from routes.audit_routes import audit_bp
from routes.db_routes import db_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CSRF Protection Hook & Context Processor
    @app.before_request
    def before_request():
        validate_csrf()
        
    @app.context_processor
    def inject_csrf_token():
        return dict(
            csrf_token=generate_csrf_token,
            current_user={
                'username': session.get('username'),
                'full_name': session.get('full_name'),
                'role': session.get('role'),
                'email': session.get('email')
            }
        )
        
    # Custom Jinja Filters
    @app.template_filter('format_datetime')
    def format_datetime(val, fmt='%b %d, %Y %I:%M %p'):
        if not val:
            return '-'
        if isinstance(val, str):
            try:
                val = datetime.fromisoformat(val.replace('Z', '+00:00'))
            except Exception:
                return val
        if hasattr(val, 'strftime'):
            return val.strftime(fmt)
        return str(val)

    @app.template_filter('format_date')
    def format_date(val, fmt='%b %d, %Y'):
        if not val:
            return '-'
        if isinstance(val, str):
            try:
                val = datetime.strptime(val[:10], '%Y-%m-%d')
            except Exception:
                return val
        if hasattr(val, 'strftime'):
            return val.strftime(fmt)
        return str(val)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(defaulter_bp)
    app.register_blueprint(leave_bp)
    app.register_blueprint(audit_bp)
    app.register_blueprint(db_bp)
    
    # Custom Error Handlers
    @app.errorhandler(400)
    def bad_request_error(e):
        return render_template(
            'error.html',
            error_code=400,
            error_title="Bad Request",
            error_message=getattr(e, 'description', "The request could not be processed due to invalid parameters or CSRF mismatch.")
        ), 400

    @app.errorhandler(404)
    def not_found_error(e):
        return render_template(
            'error.html',
            error_code=404,
            error_title="Page Not Found",
            error_message="The requested resource or page does not exist."
        ), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template(
            'error.html',
            error_code=500,
            error_title="Internal System Error",
            error_message="A database or backend processing error occurred. Please verify database connectivity."
        ), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(host='0.0.0.0', port=port, debug=debug)
