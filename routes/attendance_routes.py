from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from utils.security import login_required
from utils.db import get_db_cursor

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance')
@login_required
def list_attendance():
    date_filter = request.args.get('date', '').strip()
    student_id = request.args.get('student_id', '').strip()
    course_id = request.args.get('course_id', '').strip()
    status_filter = request.args.get('status', '').strip()
    
    query = (
        "SELECT ar.attendance_id, ar.student_id, ar.course_id, ar.classroom_id, "
        "ar.attendance_date, ar.status, ar.marked_at, ar.marked_by, "
        "ST_AsText(ar.location) AS location_coords, "
        "s.roll_no, s.student_name, "
        "c.course_code, c.course_name, "
        "cl.room_name "
        "FROM Attendance_Record ar "
        "JOIN Student s ON ar.student_id = s.student_id "
        "JOIN Course c ON ar.course_id = c.course_id "
        "LEFT JOIN Classroom cl ON ar.classroom_id = cl.classroom_id "
        "WHERE 1=1"
    )
    params = []
    
    if date_filter:
        query += " AND ar.attendance_date = %s"
        params.append(date_filter)
        
    if student_id and student_id.isdigit():
        query += " AND ar.student_id = %s"
        params.append(int(student_id))
        
    if course_id and course_id.isdigit():
        query += " AND ar.course_id = %s"
        params.append(int(course_id))
        
    if status_filter in ('Present', 'Late', 'Absent'):
        query += " AND ar.status = %s"
        params.append(status_filter)
        
    query += " ORDER BY ar.attendance_date DESC, ar.marked_at DESC, ar.attendance_id DESC"
    
    records = []
    students = []
    courses = []
    classrooms = []
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            records = cursor.fetchall()
            
            cursor.execute("SELECT student_id, roll_no, student_name FROM Student ORDER BY roll_no")
            students = cursor.fetchall()
            
            cursor.execute("SELECT course_id, course_code, course_name FROM Course ORDER BY course_code")
            courses = cursor.fetchall()
            
            cursor.execute("SELECT classroom_id, room_name, ST_AsText(location) as loc FROM Classroom ORDER BY room_name")
            classrooms = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching attendance records: {str(e)}", "danger")
        
    return render_template(
        'attendance.html',
        records=records,
        students=students,
        courses=courses,
        classrooms=classrooms,
        selected_date=date_filter,
        selected_student_id=student_id,
        selected_course_id=course_id,
        selected_status=status_filter
    )

@attendance_bp.route('/attendance/mark', methods=['POST'])
@login_required
def mark_attendance():
    student_id = request.form.get('student_id', '').strip()
    course_id = request.form.get('course_id', '').strip()
    classroom_id = request.form.get('classroom_id', '').strip()
    attendance_date = request.form.get('attendance_date', '').strip()
    status = request.form.get('status', '').strip()
    
    # Validation
    if not student_id.isdigit() or not course_id.isdigit():
        flash("Please select a valid student and course.", "danger")
        return redirect(url_for('attendance.list_attendance'))
        
    if status not in ('Present', 'Late', 'Absent'):
        flash("Status must be Present, Late, or Absent.", "danger")
        return redirect(url_for('attendance.list_attendance'))
        
    try:
        datetime.strptime(attendance_date, '%Y-%m-%d')
    except ValueError:
        flash("Invalid attendance date format (YYYY-MM-DD expected).", "danger")
        return redirect(url_for('attendance.list_attendance'))
        
    classroom_val = int(classroom_id) if classroom_id and classroom_id.isdigit() else None
    marked_by = session.get('username', 'faculty_user')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check duplicate attendance constraint (student_id, course_id, attendance_date)
            cursor.execute(
                "SELECT attendance_id FROM Attendance_Record "
                "WHERE student_id = %s AND course_id = %s AND attendance_date = %s",
                (int(student_id), int(course_id), attendance_date)
            )
            if cursor.fetchone():
                flash(f"Attendance record already exists for this student, course, and date.", "warning")
                return redirect(url_for('attendance.list_attendance'))
                
            # Retrieve classroom coordinates if available, otherwise campus geofence default
            location_point = 'POINT(73.7500 18.6250)'
            if classroom_val:
                cursor.execute(
                    "SELECT ST_AsText(location) AS loc FROM Classroom WHERE classroom_id = %s",
                    (classroom_val,)
                )
                cl_res = cursor.fetchone()
                if cl_res and cl_res['loc']:
                    location_point = cl_res['loc']
                    
            cursor.execute(
                "INSERT INTO Attendance_Record "
                "(student_id, course_id, classroom_id, attendance_date, status, marked_by, location) "
                "VALUES (%s, %s, %s, %s, %s, %s, ST_GeomFromText(%s, 4326))",
                (int(student_id), int(course_id), classroom_val, attendance_date, status, marked_by, location_point)
            )
        flash("Attendance successfully recorded! Audit log generated.", "success")
    except Exception as e:
        flash(f"Failed to record attendance: {str(e)}", "danger")
        
    return redirect(url_for('attendance.list_attendance'))

@attendance_bp.route('/attendance/update/<int:attendance_id>', methods=['POST'])
@login_required
def update_attendance(attendance_id):
    new_status = request.form.get('status', '').strip()
    if new_status not in ('Present', 'Late', 'Absent'):
        flash("Status must be Present, Late, or Absent.", "danger")
        return redirect(url_for('attendance.list_attendance'))
        
    marked_by = session.get('username', 'faculty_user')
    
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "UPDATE Attendance_Record SET status = %s, marked_by = %s WHERE attendance_id = %s",
                (new_status, marked_by, attendance_id)
            )
            if cursor.rowcount == 0:
                flash("Attendance record not found.", "warning")
            else:
                flash("Attendance status updated successfully! Audit log logged.", "success")
    except Exception as e:
        flash(f"Failed to update attendance: {str(e)}", "danger")
        
    return redirect(url_for('attendance.list_attendance'))

@attendance_bp.route('/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required
def delete_attendance(attendance_id):
    try:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "DELETE FROM Attendance_Record WHERE attendance_id = %s",
                (attendance_id,)
            )
            if cursor.rowcount == 0:
                flash("Attendance record not found.", "warning")
            else:
                flash("Attendance record deleted and logged in audit history.", "info")
    except Exception as e:
        flash(f"Failed to delete attendance: {str(e)}", "danger")
        
    return redirect(url_for('attendance.list_attendance'))
