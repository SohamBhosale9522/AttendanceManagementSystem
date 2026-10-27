
USE AttendanceManagement;

DELIMITER $$

-- Trigger 1: Log new attendance records
CREATE TRIGGER trg_attendance_insert
AFTER INSERT ON Attendance_Record
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog
        (attendance_id, action_type, action_details, changed_by)
    VALUES
        (
            NEW.attendance_id,
            'INSERT',
            CONCAT('Status: ', NEW.status,
                   ', Date: ', NEW.attendance_date),
            NEW.marked_by
        );
END$$

-- Trigger 2: Log attendance updates
CREATE TRIGGER trg_attendance_update
AFTER UPDATE ON Attendance_Record
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog
        (attendance_id, action_type, action_details, changed_by)
    VALUES
        (
            NEW.attendance_id,
            'UPDATE',
            CONCAT('Old status: ', OLD.status,
                   ', New status: ', NEW.status),
            NEW.marked_by
        );
END$$

-- Trigger 3: Log attendance deletions
CREATE TRIGGER trg_attendance_delete
AFTER DELETE ON Attendance_Record
FOR EACH ROW
BEGIN
    INSERT INTO AuditLog
        (attendance_id, action_type, action_details, changed_by)
    VALUES
        (
            OLD.attendance_id,
            'DELETE',
            CONCAT('Deleted attendance record; old status: ',
                   OLD.status),
            OLD.marked_by
        );
END$$

-- Stored procedure: list students below the attendance threshold
CREATE PROCEDURE GenerateDefaulterList(
    IN p_course_id INT,
    IN p_threshold DECIMAL(5,2)
)
BEGIN
    SELECT
        s.student_id,
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
    WHERE ar.course_id = p_course_id
    GROUP BY s.student_id, s.roll_no, s.student_name, c.course_name
    HAVING attendance_percentage < p_threshold
    ORDER BY attendance_percentage ASC;
END$$

DELIMITER ;

-- Example: defaulter list for course ID 1 with a 75% threshold
CALL GenerateDefaulterList(1, 75.00);

-- Check the audit log
SELECT * FROM AuditLog ORDER BY changed_at DESC;
