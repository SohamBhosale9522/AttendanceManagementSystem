from flask import Blueprint, render_template, request, flash
from utils.security import login_required
from utils.db import get_db_cursor

audit_bp = Blueprint('audit', __name__)

@audit_bp.route('/audit-logs')
@login_required
def list_logs():
    action_type = request.args.get('action_type', '').strip()
    date_filter = request.args.get('date', '').strip()
    
    query = (
        "SELECT log_id, attendance_id, action_type, action_details, changed_by, changed_at "
        "FROM AuditLog WHERE 1=1"
    )
    params = []
    
    if action_type in ('INSERT', 'UPDATE', 'DELETE'):
        query += " AND action_type = %s"
        params.append(action_type)
        
    if date_filter:
        query += " AND DATE(changed_at) = %s"
        params.append(date_filter)
        
    query += " ORDER BY changed_at DESC, log_id DESC LIMIT 100"
    
    logs = []
    action_types = []
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            logs = cursor.fetchall()
            
            cursor.execute("SELECT DISTINCT action_type FROM AuditLog ORDER BY action_type")
            action_types = [r['action_type'] for r in cursor.fetchall()]
    except Exception as e:
        flash(f"Error fetching audit logs: {str(e)}", "danger")
        
    return render_template(
        'audit_logs.html',
        logs=logs,
        selected_action=action_type,
        selected_date=date_filter,
        action_types=action_types
    )
