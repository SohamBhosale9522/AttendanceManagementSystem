from decimal import Decimal
from flask import Blueprint, render_template, request, flash
from utils.security import login_required
from utils.db import get_db_cursor, execute_procedure

defaulter_bp = Blueprint('defaulters', __name__)

@defaulter_bp.route('/defaulters', methods=['GET', 'POST'])
@login_required
def defaulter_list():
    courses = []
    selected_course_id = request.values.get('course_id', type=int)
    threshold = request.values.get('threshold', default=75.0, type=float)
    
    defaulters = []
    all_students_in_course = []
    selected_course = None
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT course_id, course_code, course_name, faculty_name FROM Course ORDER BY course_code")
            courses = cursor.fetchall()
            
        if courses and not selected_course_id:
            selected_course_id = courses[0]['course_id']
            
        if selected_course_id:
            for c in courses:
                if c['course_id'] == selected_course_id:
                    selected_course = c
                    break
                    
            # 1. Call the existing stored procedure GenerateDefaulterList
            defaulters = execute_procedure('GenerateDefaulterList', [selected_course_id, threshold])
            
            # 2. Fetch full attendance records for all students in this course for complete visibility
            with get_db_cursor(commit=False) as cursor:
                cursor.execute(
                    "SELECT s.student_id, s.roll_no, s.student_name, "
                    "COUNT(ar.attendance_id) AS total_classes, "
                    "SUM(ar.status IN ('Present', 'Late')) AS attended_classes, "
                    "ROUND(100.0 * SUM(ar.status IN ('Present', 'Late')) / COUNT(ar.attendance_id), 2) AS attendance_percentage "
                    "FROM Attendance_Record ar "
                    "JOIN Student s ON ar.student_id = s.student_id "
                    "WHERE ar.course_id = %s "
                    "GROUP BY s.student_id, s.roll_no, s.student_name "
                    "ORDER BY attendance_percentage ASC",
                    (selected_course_id,)
                )
                all_students_in_course = cursor.fetchall()
                
    except Exception as e:
        flash(f"Error calculating defaulter list: {str(e)}", "danger")
        
    return render_template(
        'defaulters.html',
        courses=courses,
        selected_course_id=selected_course_id,
        selected_course=selected_course,
        threshold=threshold,
        defaulters=defaulters,
        all_students=all_students_in_course
    )
