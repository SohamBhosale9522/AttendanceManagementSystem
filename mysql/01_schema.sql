
CREATE DATABASE IF NOT EXISTS AttendanceManagement;
USE AttendanceManagement;

CREATE TABLE Student (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(20) NOT NULL UNIQUE,
    student_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE,
    department VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Classroom (
    classroom_id INT AUTO_INCREMENT PRIMARY KEY,
    room_name VARCHAR(50) NOT NULL UNIQUE,
    capacity INT NOT NULL,
    location POINT NOT NULL SRID 4326,
    CHECK (capacity > 0),
    SPATIAL INDEX idx_classroom_location (location)
);

CREATE TABLE Course (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL UNIQUE,
    course_name VARCHAR(100) NOT NULL,
    faculty_name VARCHAR(100) NOT NULL,
    semester INT NOT NULL
);

CREATE TABLE Attendance_Record (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    classroom_id INT,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL,
    marked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    marked_by VARCHAR(100) NOT NULL DEFAULT 'admin',
    location POINT NOT NULL SRID 4326,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id),
    FOREIGN KEY (classroom_id) REFERENCES Classroom(classroom_id),
    UNIQUE (student_id, course_id, attendance_date),
    SPATIAL INDEX idx_attendance_location (location)
);

CREATE TABLE AuditLog (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    attendance_id INT,
    action_type VARCHAR(20) NOT NULL,
    action_details VARCHAR(255),
    changed_by VARCHAR(100) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
