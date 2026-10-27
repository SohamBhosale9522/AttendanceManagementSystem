from flask import Blueprint, render_template, flash
from utils.security import login_required
from utils.db import get_db_cursor

course_bp = Blueprint('courses', __name__)

@course_bp.route('/courses')
@login_required
def list_courses():
    courses = []
    try:
        with get_db_cursor(commit=False) as cursor:
            # Query 10 from 03_queries.sql with full status breakdown
            cursor.execute(
                "SELECT c.course_id, c.course_code, c.course_name, c.faculty_name, c.semester, "
                "COUNT(ar.attendance_id) AS total_records, "
                "SUM(CASE WHEN ar.status = 'Present' THEN 1 ELSE 0 END) AS present_count, "
                "SUM(CASE WHEN ar.status = 'Late' THEN 1 ELSE 0 END) AS late_count, "
                "SUM(CASE WHEN ar.status = 'Absent' THEN 1 ELSE 0 END) AS absent_count "
                "FROM Course c "
                "LEFT JOIN Attendance_Record ar ON c.course_id = ar.course_id "
                "GROUP BY c.course_id, c.course_code, c.course_name, c.faculty_name, c.semester "
                "ORDER BY c.course_code ASC"
            )
            courses = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching course list: {str(e)}", "danger")
        
    return render_template('courses.html', courses=courses)
