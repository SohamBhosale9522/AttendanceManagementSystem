# Attendance Management System

## Project Overview

The Attendance Management System is a DBMS mini project that manages student attendance, course details, classroom locations, attendance percentages, defaulter lists, and leave applications using MySQL and MongoDB.

## Technologies Used

- MySQL 8.0
- MongoDB
- SQL
- JavaScript for MongoDB Shell
- Visual Studio Code

## Features

1. Student, classroom, and course management.
2. Attendance recording with Present, Absent, and Late statuses.
3. Attendance percentage calculation.
4. Defaulter identification based on attendance thresholds.
5. SQL pattern matching and nested queries.
6. Aggregate functions using `GROUP BY` and `HAVING`.
7. Spatial data for classroom and attendance locations.
8. Triggers for attendance audit logging.
9. Stored procedure for generating defaulter lists.
10. Faculty database permissions and access control.
11. MongoDB leave applications and aggregation queries.

## Database Design

### MySQL Tables

- `Student` — stores student details.
- `Classroom` — stores classroom information and location.
- `Course` — stores course details.
- `Attendance_Record` — stores attendance records.
- `AuditLog` — records attendance changes.

### MongoDB Collection

- `leave_applications` — stores student leave application documents.

## Project Structure

```text
AttendanceManagementSystem/
├── mysql/
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_queries.sql
│   ├── 04_triggers_procedure.sql
│   └── 05_security.sql
├── mongodb/
│   └── leave_applications.js
└── README.md
```

## Setup Instructions

### MySQL Setup

1. Install MySQL Server 8.0 and ensure the MySQL service is running.
2. Open the project folder in Visual Studio Code.
3. Connect to MySQL using the MySQL command-line client.
4. Execute the SQL files in the following order:

   1. `mysql/01_schema.sql`
   2. `mysql/02_sample_data.sql`
   3. `mysql/03_queries.sql`
   4. `mysql/04_triggers_procedure.sql`
   5. `mysql/05_security.sql`

5. Verify the tables and sample data.
6. Test the triggers, stored procedure, and faculty permissions.

**Note:** Run the schema and sample-data scripts on a fresh database in the specified order. The schema script must have the correct `NOT NULL` definition for the spatially indexed location column. Avoid rerunning sample-data scripts without checking for duplicate records.

### MongoDB Setup

1. Install MongoDB Server and MongoDB Shell (`mongosh`).
2. Ensure the MongoDB service is running.
3. Open the VS Code terminal in the project directory.
4. Execute the MongoDB script using:

```powershell
mongosh "mongodb://localhost:27017/AttendanceManagement" --file ".\mongodb\leave_applications.js"
```

5. Review the inserted documents and aggregation query results.

## Example Stored Procedure

```sql
CALL GenerateDefaulterList(1, 75.00);
```

This procedure generates a list of students whose attendance percentage for course ID `1` is below the specified threshold of 75%.

## Expected Results

- Student and course details can be retrieved using SQL queries.
- Attendance records can be filtered and grouped by status.
- Attendance percentages and defaulter lists can be generated.
- Attendance changes are recorded in the audit log.
- Faculty access is restricted according to granted database permissions.
- Leave applications can be stored and queried using MongoDB.

## Conclusion

The project demonstrates relational database design, primary and foreign key constraints, SQL queries, aggregate functions, spatial data, triggers, stored procedures, database access control, and NoSQL document operations using MongoDB.
