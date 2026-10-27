import re
from flask import Blueprint, render_template, request, redirect, url_for, flash
from utils.security import login_required
from utils.db import get_db_cursor

student_bp = Blueprint('students', __name__)

@student_bp.route('/students')
@login_required
def list_students():
    search = request.args.get('search', '').strip()
    dept = request.args.get('dept', '').strip()
    sem = request.args.get('sem', '').strip()
    
    query = "SELECT student_id, roll_no, student_name, email, department, semester, created_at FROM Student WHERE 1=1"
    params = []
    
    if search:
        query += " AND (student_name LIKE %s OR roll_no LIKE %s OR email LIKE %s)"
        params.extend([f"%{search}%", f"%{search}%", f"%{search}%"])
        
    if dept:
        query += " AND department = %s"
        params.append(dept)
        
    if sem and sem.isdigit():
        query += " AND semester = %s"
        params.append(int(sem))
        
    query += " ORDER BY roll_no ASC"
    
    students = []
    departments = []
    semesters = []
    
    try:
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(query, tuple(params))
            students = cursor.fetchall()
            
            cursor.execute("SELECT DISTINCT department FROM Student ORDER BY department")
            departments = [r['department'] for r in cursor.fetchall() if r['department']]
            
            cursor.execute("SELECT DISTINCT semester FROM Student ORDER BY semester")
            semesters = [r['semester'] for r in cursor.fetchall() if r['semester']]
    except Exception as e:
        flash(f"Error fetching students: {str(e)}", "danger")
        
    return render_template(
        'students.html',
        students=students,
        search=search,
        selected_dept=dept,
        selected_sem=sem,
        departments=departments,
        semesters=semesters
    )

@student_bp.route('/students/add', methods=['POST'])
@login_required
def add_student():
    roll_no = request.form.get('roll_no', '').strip()
    student_name = request.form.get('student_name', '').strip()
    email = request.form.get('email', '').strip()
    department = request.form.get('department', '').strip()
    semester = request.form.get('semester', '').strip()
    
    # Input validation
    if not roll_no or len(roll_no) > 20:
        flash("Roll number is required and cannot exceed 20 characters.", "danger")
        return redirect(url_for('students.list_students'))
        
    if not student_name or len(student_name) > 100:
        flash("Student name is required and cannot exceed 100 characters.", "danger")
        return redirect(url_for('students.list_students'))
        
    if not department or len(department) > 50:
        flash("Department is required and cannot exceed 50 characters.", "danger")
        return redirect(url_for('students.list_students'))
        
    if not semester.isdigit() or not (1 <= int(semester) <= 8):
        flash("Semester must be an integer between 1 and 8.", "danger")
        return redirect(url_for('students.list_students'))
        
    if email:
        email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_regex, email):
            flash("Please provide a valid email address.", "danger")
            return redirect(url_for('students.list_students'))
    else:
        email = None
        
    try:
        with get_db_cursor(commit=True) as cursor:
            # Check for duplicate roll_no
            cursor.execute("SELECT student_id FROM Student WHERE roll_no = %s", (roll_no,))
            if cursor.fetchone():
                flash(f"Student with roll number '{roll_no}' already exists.", "warning")
                return redirect(url_for('students.list_students'))
                
            cursor.execute(
                "INSERT INTO Student (roll_no, student_name, email, department, semester) "
                "VALUES (%s, %s, %s, %s, %s)",
                (roll_no, student_name, email, department, int(semester))
            )
        flash(f"Student {student_name} ({roll_no}) successfully registered!", "success")
    except Exception as e:
        flash(f"Failed to add student: {str(e)}", "danger")
        
    return redirect(url_for('students.list_students'))
