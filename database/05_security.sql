USE AttendanceManagement;

CREATE USER IF NOT EXISTS 'faculty_user'@'localhost'
IDENTIFIED BY 'ReplaceWithAStrongPassword!';

-- Faculty can view and add students, view courses, and classrooms
GRANT SELECT, INSERT ON AttendanceManagement.Student
TO 'faculty_user'@'localhost';

GRANT SELECT ON AttendanceManagement.Course
TO 'faculty_user'@'localhost';

GRANT SELECT ON AttendanceManagement.Classroom
TO 'faculty_user'@'localhost';

-- Faculty can view, insert, update, and delete attendance records
GRANT SELECT, INSERT, UPDATE, DELETE
ON AttendanceManagement.Attendance_Record
TO 'faculty_user'@'localhost';

-- Faculty can view the audit log
GRANT SELECT ON AttendanceManagement.AuditLog
TO 'faculty_user'@'localhost';

-- Faculty can execute defaulter list procedure
GRANT EXECUTE ON PROCEDURE AttendanceManagement.GenerateDefaulterList
TO 'faculty_user'@'localhost';

-- Faculty can manage login credentials
GRANT SELECT, INSERT, UPDATE ON AttendanceManagement.Faculty_User
TO 'faculty_user'@'localhost';

-- Display the faculty account's permissions
SHOW GRANTS FOR 'faculty_user'@'localhost';
