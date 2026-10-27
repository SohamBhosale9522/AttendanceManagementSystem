
USE AttendanceManagement;

INSERT INTO Student
(roll_no, student_name, email, department, semester)
VALUES
('IT001', 'Aarav Sharma', 'aarav@example.com', 'IT', 5),
('IT002', 'Priya Patil', 'priya@example.com', 'IT', 5),
('IT003', 'Rohan Deshmukh', 'rohan@example.com', 'IT', 5),
('IT004', 'Sneha Kulkarni', 'sneha@example.com', 'IT', 5),
('IT005', 'Aditya Joshi', 'aditya@example.com', 'IT', 5);

INSERT INTO Classroom (room_name, capacity, location)
VALUES
('Lab A', 60, ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
('Room 201', 40, ST_GeomFromText('POINT(73.7510 18.6260)', 4326));

INSERT INTO Course
(course_code, course_name, faculty_name, semester)
VALUES
('IT501', 'Database Management Systems', 'Prof. Mehta', 5),
('IT502', 'Data Structures and Algorithms', 'Prof. Kulkarni', 5),
('IT503', 'Operating Systems', 'Prof. Patil', 5);

INSERT INTO Attendance_Record
(student_id, course_id, classroom_id, attendance_date,
 status, marked_by, location)
VALUES
(1, 1, 1, '2026-10-20', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(2, 1, 1, '2026-10-20', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(3, 1, 1, '2026-10-20', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(4, 1, 1, '2026-10-20', 'Late', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(5, 1, 1, '2026-10-20', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),

(1, 2, 2, '2026-10-21', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7510 18.6260)', 4326)),
(2, 2, 2, '2026-10-21', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7510 18.6260)', 4326)),
(3, 2, 2, '2026-10-21', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7510 18.6260)', 4326)),
(4, 2, 2, '2026-10-21', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7510 18.6260)', 4326)),
(5, 2, 2, '2026-10-21', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7510 18.6260)', 4326)),

(1, 1, 1, '2026-10-22', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(2, 1, 1, '2026-10-22', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(3, 1, 1, '2026-10-22', 'Present', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(4, 1, 1, '2026-10-22', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326)),
(5, 1, 1, '2026-10-22', 'Absent', 'faculty1',
 ST_GeomFromText('POINT(73.7500 18.6250)', 4326));
