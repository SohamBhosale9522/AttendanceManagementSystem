import re
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.security import login_required
from config import get_mongo_db

leave_bp = Blueprint('leaves', __name__)

@leave_bp.route('/leaves')
@login_required
def list_leaves():
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    leave_type_filter = request.args.get('leave_type', '').strip()
    
    query = {}
    if search:
        regex_pattern = re.compile(re.escape(search), re.IGNORECASE)
        query["$or"] = [
            {"student_name": {"$regex": regex_pattern}},
            {"student_roll_no": {"$regex": regex_pattern}},
            {"application_id": {"$regex": regex_pattern}},
            {"reason": {"$regex": regex_pattern}}
        ]
        
    if status_filter in ('Pending', 'Approved', 'Rejected'):
        query["status"] = status_filter
        
    if leave_type_filter in ('Medical', 'Personal', 'Duty', 'Academic'):
        query["leave_type"] = leave_type_filter
        
    leaves = []
    status_counts = {'Total': 0, 'Pending': 0, 'Approved': 0, 'Rejected': 0}
    type_counts = {}
    
    try:
        db = get_mongo_db()
        cursor = db.leave_applications.find(query).sort("applied_at", -1)
        leaves = list(cursor)
        
        # Aggregate status counts
        status_pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        for item in db.leave_applications.aggregate(status_pipeline):
            st = item['_id']
            if st in status_counts:
                status_counts[st] = item['count']
        status_counts['Total'] = db.leave_applications.count_documents({})
        
        # Aggregate type counts
        type_pipeline = [
            {"$group": {"_id": "$leave_type", "count": {"$sum": 1}}}
        ]
        for item in db.leave_applications.aggregate(type_pipeline):
            lt = item['_id']
            if lt:
                type_counts[lt] = item['count']
                
    except Exception as e:
        flash(f"MongoDB connection/query error: {str(e)}", "danger")
        
    return render_template(
        'leaves.html',
        leaves=leaves,
        search=search,
        selected_status=status_filter,
        selected_type=leave_type_filter,
        status_counts=status_counts,
        type_counts=type_counts
    )

@leave_bp.route('/leaves/update-status', methods=['POST'])
@login_required
def update_leave_status():
    app_id = request.form.get('application_id', '').strip()
    new_status = request.form.get('status', '').strip()
    
    if not app_id or new_status not in ('Approved', 'Rejected', 'Pending'):
        flash("Invalid leave application or status selection.", "danger")
        return redirect(url_for('leaves.list_leaves'))
        
    reviewer = session.get('username', 'faculty_user')
    
    try:
        db = get_mongo_db()
        result = db.leave_applications.update_one(
            {"application_id": app_id},
            {
                "$set": {
                    "status": new_status,
                    "reviewed_by": reviewer,
                    "reviewed_at": datetime.utcnow()
                }
            }
        )
        if result.matched_count > 0:
            flash(f"Leave application {app_id} status updated to '{new_status}' in MongoDB.", "success")
        else:
            flash(f"Leave application {app_id} not found in MongoDB.", "warning")
    except Exception as e:
        flash(f"Failed to update leave application: {str(e)}", "danger")
        
    return redirect(url_for('leaves.list_leaves'))
