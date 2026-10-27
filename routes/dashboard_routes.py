from flask import Blueprint, render_template
from utils.security import login_required
from utils.db import get_db_cursor
from config import get_mongo_db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    stats = {
        'total_students': 0,
        'total_courses': 0,
        'total_attendance': 0,
        'pending_leaves': 0,
        'total_leaves': 0,
        'attendance_distribution': {'Present': 0, 'Late': 0, 'Absent': 0},
        'course_stats': [],
        'recent_attendance': [],
        'recent_leaves': []
    }
    
    # 1. Fetch relational statistics from MySQL
    try:
        with get_db_cursor(commit=False) as cursor:
            # Student count
            cursor.execute("SELECT COUNT(*) AS cnt FROM Student")
            stats['total_students'] = cursor.fetchone()['cnt']
            
            # Course count
            cursor.execute("SELECT COUNT(*) AS cnt FROM Course")
            stats['total_courses'] = cursor.fetchone()['cnt']
            
            # Attendance records count
            cursor.execute("SELECT COUNT(*) AS cnt FROM Attendance_Record")
            stats['total_attendance'] = cursor.fetchone()['cnt']
            
            # Attendance distribution (Present, Late, Absent)
            cursor.execute(
                "SELECT status, COUNT(*) AS count "
                "FROM Attendance_Record "
                "GROUP BY status"
            )
            for row in cursor.fetchall():
                st = row['status']
                if st in stats['attendance_distribution']:
                    stats['attendance_distribution'][st] = row['count']
                    
            # Attendance summary per course
            cursor.execute(
                "SELECT c.course_code, c.course_name, "
                "COUNT(ar.attendance_id) AS total_records, "
                "SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) AS present_count, "
                "SUM(CASE WHEN ar.status = 'Late' THEN 1 ELSE 0 END) AS late_count, "
                "SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) AS absent_count "
                "FROM Course c "
                "LEFT JOIN Attendance_Record ar ON c.course_id = ar.course_id "
                "GROUP BY c.course_id, c.course_code, c.course_name "
                "ORDER BY c.course_code"
            )
            stats['course_stats'] = cursor.fetchall()
            
            # Recent attendance activities
            cursor.execute(
                "SELECT ar.attendance_id, ar.attendance_date, ar.status, ar.marked_by, ar.marked_at, "
                "s.student_name, s.roll_no, c.course_code, c.course_name "
                "FROM Attendance_Record ar "
                "JOIN Student s ON ar.student_id = s.student_id "
                "JOIN Course c ON ar.course_id = c.course_id "
                "ORDER BY ar.attendance_date DESC, ar.marked_at DESC "
                "LIMIT 6"
            )
            stats['recent_attendance'] = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching MySQL dashboard data: {e}")
        
    # 2. Fetch NoSQL leave applications statistics from MongoDB
    try:
        db = get_mongo_db()
        stats['pending_leaves'] = db.leave_applications.count_documents({"status": "Pending"})
        stats['total_leaves'] = db.leave_applications.count_documents({})
        stats['recent_leaves'] = list(
            db.leave_applications.find().sort("applied_at", -1).limit(5)
        )
    except Exception as e:
        print(f"Error fetching MongoDB dashboard data: {e}")
        
    return render_template('dashboard.html', stats=stats)
