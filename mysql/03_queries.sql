
USE AttendanceManagement;

-- 1. Display all students
SELECT * FROM Student;

-- 2. Pattern matching: find students whose names start with A
SELECT *
FROM Student
WHERE student_name LIKE 'A%';

-- 3. Find students in the IT department
SELECT student_id, roll_no, student_name
FROM Student
WHERE department = 'IT';

-- 4. Count attendance statuses for each course
SELECT
    c.course_name,
    ar.status,
    COUNT(*) AS total_records
FROM Attendance_Record ar
JOIN Course c ON ar.course_id = c.course_id
GROUP BY c.course_name, ar.status
ORDER BY c.course_name, ar.status;

-- 5. Calculate attendance percentage for each student in each course.
-- Present and Late both count as attended.
SELECT
    s.roll_no,
    s.student_name,
    c.course_name,
    COUNT(*) AS total_classes,
    SUM(ar.status IN ('Present', 'Late')) AS attended_classes,
    ROUND(
        100.0 * SUM(ar.status IN ('Present', 'Late')) / COUNT(*),
        2
    ) AS attendance_percentage
FROM Attendance_Record ar
JOIN Student s ON ar.student_id = s.student_id
JOIN Course c ON ar.course_id = c.course_id
GROUP BY s.student_id, s.roll_no, s.student_name,
         c.course_id, c.course_name
ORDER BY c.course_name, s.roll_no;

-- 6. GROUP BY and HAVING: students below 75% attendance
SELECT
    s.roll_no,
    s.student_name,
    c.course_name,
    ROUND(
        100.0 * SUM(ar.status IN ('Present', 'Late')) / COUNT(*),
        2
    ) AS attendance_percentage
FROM Attendance_Record ar
JOIN Student s ON ar.student_id = s.student_id
JOIN Course c ON ar.course_id = c.course_id
GROUP BY s.student_id, s.roll_no, s.student_name,
         c.course_id, c.course_name
HAVING attendance_percentage < 75;

-- 7. Nested query: students with attendance below the
-- average attendance percentage for their course
SELECT
    s.student_name,
    c.course_name,
    ROUND(
        100.0 * SUM(ar.status IN ('Present', 'Late')) / COUNT(*),
        2
    ) AS attendance_percentage
FROM Attendance_Record ar
JOIN Student s ON ar.student_id = s.student_id
JOIN Course c ON ar.course_id = c.course_id
GROUP BY s.student_id, s.student_name, c.course_id, c.course_name
HAVING attendance_percentage < (
    SELECT AVG(student_percentage)
    FROM (
        SELECT
            100.0 * SUM(ar2.status IN ('Present', 'Late'))
            / COUNT(*) AS student_percentage
        FROM Attendance_Record ar2
        WHERE ar2.course_id = c.course_id
        GROUP BY ar2.student_id
    ) AS course_attendance
);

-- 8. Find attendance records for a particular date
SELECT s.student_name, c.course_name, ar.status
FROM Attendance_Record ar
JOIN Student s ON ar.student_id = s.student_id
JOIN Course c ON ar.course_id = c.course_id
WHERE ar.attendance_date = '2026-10-20';

-- 9. Display classroom coordinates
SELECT
    classroom_id,
    room_name,
    ST_AsText(location) AS coordinates
FROM Classroom;

-- 10. Count attendance records per course
SELECT c.course_name, COUNT(*) AS total_records
FROM Course c
LEFT JOIN Attendance_Record ar ON c.course_id = ar.course_id
GROUP BY c.course_id, c.course_name;
