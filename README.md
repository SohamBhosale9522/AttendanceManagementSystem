# 🎓 Attendance Management System (Dual-Engine DBMS Web Application)

A modern, responsive, full-stack college Attendance Management System built with **Flask (Python)**, **MySQL 8.0 (Relational Engine)**, and **MongoDB (NoSQL Document Engine)**. This web application completely replaces manual terminal SQL executions with an interactive, faculty-facing administrative portal.

---

## 🌟 Key Features

1. **Faculty Authentication & Security**
   - Secure login and session management protected by `scrypt` cryptographic password hashing.
   - Comprehensive CSRF (Cross-Site Request Forgery) protection across all mutating HTTP requests.
   - Route-level role-based authorization ensuring protected access.
   - Dual faculty demo accounts pre-seeded (`faculty1` & `admin`).

2. **Real-Time Interactive Dashboard**
   - Live metrics fetched directly from MySQL (`Student`, `Course`, `Attendance_Record`) and MongoDB (`leave_applications`).
   - Dynamic **Chart.js** attendance status distribution (Present, Late, Absent).
   - Course-wise attendance comparison stacked bar chart.
   - Instant quick-action shortcuts for recording attendance, auditing defaulters, and managing leaves.

3. **Student Directory & Enrolment**
   - Searchable, filterable student records by Roll Number, Name, Department, and Semester.
   - Backend validation for new student registrations with automatic uniqueness enforcement.

4. **Course Catalog & Class Tracking**
   - Course overview displaying faculty assignments, semester info, and total recorded sessions.
   - Direct breakdown of attendance counts per course.

5. **Session Attendance Marking & Audit Automation**
   - Authorized faculty can mark attendance as **Present**, **Late**, or **Absent**.
   - Spatial GIS location tagging utilizing MySQL `POINT NOT NULL SRID 4326` campus coordinates.
   - Status corrections and removals.
   - **Automated MySQL Triggers:** Every insert, update, or deletion automatically logs the user, timestamp, and modification details into the `AuditLog` table.
   - Strict composite uniqueness (`student_id`, `course_id`, `attendance_date`) prevents duplicate daily records.

6. **Defaulter List Analysis (MySQL Stored Procedure)**
   - Interactive threshold control defaulting to **75%**.
   - Direct execution of the stored procedure:
     ```sql
     CALL GenerateDefaulterList(course_id, attendance_threshold);
     ```
   - Color-coded progress bars highlighting defaulters below the selected threshold alongside a full class roster comparison.

7. **Leave Applications (MongoDB Document Engine)**
   - NoSQL collection `leave_applications` managing flexible student leave documents.
   - Filter by status (`Pending`, `Approved`, `Rejected`) and category (`Medical`, `Personal`).
   - Faculty approval and rejection actions with atomic MongoDB `$set` updates.

8. **Read-Only Audit Trail**
   - Dedicated viewer for the MySQL `AuditLog` table showing exact database trigger events.
   - Filterable by event type (`INSERT`, `UPDATE`, `DELETE`) and date.

9. **Database Health & Diagnostic Inspector**
   - Live diagnostic monitor verifying active connections, response latency, table row counts, and MongoDB collections.
   - Safe masking that protects passwords and connection secrets from ever leaking to the frontend.

---

## 🛠️ Technology Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | HTML5, CSS3, JavaScript | Modern blue-and-white theme, CSS Grid & Flexbox |
| **UI Framework** | Bootstrap 5.3 & Bootstrap Icons | Clean, responsive layout for desktop, tablet, and mobile |
| **Data Visualization** | Chart.js 4.4 | Real-time doughnut and stacked bar charts |
| **Backend Framework** | Python 3.11 / Flask 3.1 | Modular architecture with Flask Blueprints |
| **Relational Database** | MySQL Server 8.0 | Tables, Triggers, Stored Procedures, Spatial Data |
| **NoSQL Database** | MongoDB 7+ / 8+ | Document store with aggregation pipelines |
| **RDBMS Driver** | `mysql-connector-python` | Parameterized SQL execution & stored procedure calls |
| **NoSQL Driver** | `pymongo` | Thread-safe connection-pooled document queries |
| **Production Server** | Gunicorn WSGI | Ready for containerized & cloud production deployment |

---

## 🏛️ Database Architecture

### MySQL 8.0 Relational Tables (`AttendanceManagement`)
- `Student`: Stores student identity (`student_id`, `roll_no`, `student_name`, `email`, `department`, `semester`, `created_at`).
- `Classroom`: Room details with GIS spatial point (`classroom_id`, `room_name`, `capacity`, `location POINT SRID 4326`).
- `Course`: Academic course offerings (`course_id`, `course_code`, `course_name`, `faculty_name`, `semester`).
- `Attendance_Record`: Daily student attendance (`attendance_id`, `student_id`, `course_id`, `classroom_id`, `attendance_date`, `status`, `marked_by`, `location POINT SRID 4326`, `marked_at`).
- `AuditLog`: System modifications log (`log_id`, `attendance_id`, `action_type`, `action_details`, `changed_by`, `changed_at`).
- `Faculty_User`: Hashed faculty authentication credentials (`user_id`, `username`, `password_hash`, `full_name`, `email`, `role`).

### MySQL Database Triggers
- `trg_attendance_insert`: Automatically logs an `INSERT` entry into `AuditLog` upon recording new attendance.
- `trg_attendance_update`: Automatically logs an `UPDATE` entry with prior and updated status into `AuditLog`.
- `trg_attendance_delete`: Automatically logs a `DELETE` entry into `AuditLog` before a record is removed.

### MySQL Stored Procedure
```sql
CALL GenerateDefaulterList(p_course_id, p_threshold);
```
Aggregates attendance ratios using `GROUP BY` and `HAVING attendance_percentage < p_threshold`, sorting by attendance in ascending order.

### MongoDB Collection (`AttendanceManagement.leave_applications`)
Flexible NoSQL document schema:
```json
{
  "_id": "ObjectId(...)",
  "application_id": "LA001",
  "student_roll_no": "IT001",
  "student_name": "Aarav Sharma",
  "leave_type": "Medical",
  "reason": "Fever and medical checkup",
  "start_date": "2026-10-26T00:00:00Z",
  "end_date": "2026-10-27T00:00:00Z",
  "status": "Pending",
  "applied_at": "2026-10-25T09:18:25Z",
  "reviewed_by": "faculty1",
  "reviewed_at": "2026-10-27T10:15:00Z"
}
```

---

## 📁 Project Structure

```text
AttendanceManagementSystem/
├── app.py                      # Flask Application Factory & Server entry point
├── config.py                   # Centralized configuration & connection pooling
├── requirements.txt            # Python dependencies
├── .env                        # Local environment secrets (ignored by Git)
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git exclusions (venv, .env, __pycache__)
├── Procfile                    # Cloud Procfile for Gunicorn deployment
├── runtime.txt                 # Python runtime definition (python-3.11.0)
├── README.md                   # Complete documentation & deployment guide
├── database/                   # Canonical SQL scripts
│   ├── 01_schema.sql
│   ├── 02_sample_data.sql
│   ├── 03_queries.sql
│   ├── 04_triggers_procedure.sql
│   └── 05_security.sql
├── mysql/                      # Mirrored database scripts
├── mongodb/
│   └── leave_applications.js   # MongoDB sample documents & aggregation queries
├── routes/
│   ├── __init__.py
│   ├── auth_routes.py          # Faculty authentication & sessions
│   ├── dashboard_routes.py     # Metrics, feeds, & Chart.js endpoints
│   ├── student_routes.py       # Student directory & enrolment
│   ├── course_routes.py        # Course catalog & attendance ratios
│   ├── attendance_routes.py    # Session logging, updates, & GIS tags
│   ├── defaulter_routes.py     # Stored procedure runner
│   ├── leave_routes.py         # MongoDB NoSQL leave workflow
│   ├── audit_routes.py         # Read-only audit trail
│   └── db_routes.py            # Diagnostic connection monitor
├── utils/
│   ├── __init__.py
│   ├── db.py                   # Context managers & stored procedure helpers
│   └── security.py             # CSRF tokens & scrypt password hashing
├── templates/
│   ├── base.html               # Master layout with sidebar & top navbar
│   ├── login.html              # Sleek collegiate login page
│   ├── dashboard.html          # Interactive dashboard & charts
│   ├── students.html           # Students directory & add student modal
│   ├── courses.html            # Course catalog
│   ├── attendance.html         # Attendance table & mark attendance modal
│   ├── defaulters.html         # Defaulter list with threshold slider
│   ├── leaves.html             # MongoDB leave applications
│   ├── audit_logs.html         # Read-only trigger logs
│   ├── db_status.html          # Dual-engine connection status
│   └── error.html              # Error pages (400, 404, 500)
├── static/
│   ├── css/
│   │   └── style.css           # Blue-and-white collegiate UI styling
│   ├── js/
│   │   ├── main.js             # Mobile drawer, filters, toasts
│   │   └── dashboard_charts.js # Chart.js doughnut & stacked bar configs
│   └── images/
│       └── logo.svg            # AttendTrack emblem
└── tests/
    ├── __init__.py
    └── test_app.py             # Complete 16-test automated verification suite
```

---

## 🚀 Local Setup Instructions (Windows 11 PowerShell)

### Step 1: Open the Project Directory
Open **Windows PowerShell** or terminal in Visual Studio Code:
```powershell
cd "c:\Users\Swapnil\OneDrive\Desktop\AttendanceManagementSystem"
```

### Step 2: Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(If PowerShell restricts script execution, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` once).*

### Step 3: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env`:
```powershell
Copy-Item .env.example .env
```
Ensure `.env` matches your local MySQL and MongoDB configurations:
```ini
FLASK_APP=app.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=94c8e71b2d07a9b0c80b4398e219484ca789bb0c410943899f845a7c29348e71

# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=AttendanceManagement
MYSQL_USER=faculty_user
MYSQL_PASSWORD=ReplaceWithAStrongPassword!

# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/
MONGO_DB_NAME=AttendanceManagement
```

### Step 5: Verify Databases
Ensure both MySQL and MongoDB services are active:
```powershell
Get-Service -Name MySQL80, MongoDB
```
If you ever need to initialize the databases from scratch, run:
```powershell
# MySQL Initialization:
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/01_schema.sql
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/02_sample_data.sql
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/04_triggers_procedure.sql
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe" -u root -p < database/05_security.sql

# MongoDB Initialization:
mongosh "mongodb://localhost:27017/AttendanceManagement" --file ".\mongodb\leave_applications.js"
```

### Step 6: Run Automated Tests
Execute the comprehensive test suite to verify everything works:
```powershell
python -m unittest tests/test_app.py
```
*(Expected output: `Ran 16 tests ... OK`)*.

### Step 7: Launch the Application
```powershell
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

### 🔑 Demo Credentials
| Role | Username | Password | Access Level |
|---|---|---|---|
| **Faculty Member** | `faculty1` | `Faculty@123` | Full attendance marking, leave review, defaulter analysis |
| **System Admin** | `admin` | `Admin@123` | Full portal and diagnostic access |

---

## 🌐 Online Deployment Guide (24/7 Cloud Architecture)

To run the application publicly without keeping your personal computer switched on, host the database engines and Flask application on cloud tiers.

### Architecture Overview
```
[User Browser / Mobile] 
        │ HTTPS
        ▼
[Web Host (Render / Railway / PythonAnywhere)]
   ├── Flask Application (Gunicorn)
   │     ├── MySQL Connection (SSL/TLS) ───► [Cloud MySQL (Aiven / PlanetScale / Railway)]
   │     └── Mongo Connection (SRV/SSL) ──► [MongoDB Atlas Cloud Cluster]
```

---

### Step 1: Push Code to GitHub
1. Open PowerShell in the project directory:
   ```powershell
   cd "c:\Users\Swapnil\OneDrive\Desktop\AttendanceManagementSystem"
   git status
   ```
2. Create a new repository on [GitHub](https://github.com/new), named for instance `attendance-management-system`.
3. Link and push your local commits:
   ```powershell
   git remote add origin https://github.com/<your-username>/attendance-management-system.git
   git branch -M main
   git push -u origin main
   ```
   *(Note: The `.gitignore` automatically prevents your `.env` secrets and `venv` from ever uploading to GitHub).*

---

### Step 2: Provision Cloud Databases

#### A. Cloud MongoDB (Free MongoDB Atlas)
1. Sign up at [MongoDB Atlas](https://www.mongodb.com/atlas/database).
2. Create a free **M0 Shared Cluster**.
3. Under **Security > Database Access**, add a database user (e.g., `app_faculty` with a strong password).
4. Under **Security > Network Access**, click **Add IP Address** and choose `0.0.0.0/0` (Allow Access from Anywhere).
5. Under **Deployment > Database > Connect**, choose **Drivers > Python** and copy your connection string:
   ```
   mongodb+srv://app_faculty:<password>@cluster0.abcde.mongodb.net/?retryWrites=true&w=majority
   ```
6. Open **mongosh** or **MongoDB Compass** and load the sample leave applications by importing `mongodb/leave_applications.js`.

#### B. Cloud MySQL 8 (Free Aiven / Railway / PlanetScale)
1. Sign up at [Aiven.io](https://aiven.io) or [Railway.app](https://railway.app).
2. Provision a free/developer MySQL 8.0 service.
3. Note your cloud host, port (e.g. `3306`), username, password, and database name.
4. Run the canonical schema scripts (`database/01_schema.sql`, `02_sample_data.sql`, `04_triggers_procedure.sql`, and `05_security.sql`) on your cloud MySQL database using MySQL Workbench or CLI.

---

### Step 3: Deploy Flask App to Render / Railway

1. Sign up at [Render.com](https://render.com).
2. Click **New + > Web Service** and connect your GitHub repository.
3. Configure the service settings:
   - **Environment:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
4. Under **Environment Variables**, configure your production variables:

| Environment Variable | Recommended Value |
|---|---|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | *(A random 64-character hex key)* |
| `MYSQL_HOST` | `your-cloud-mysql-host.aivencloud.com` |
| `MYSQL_PORT` | `3306` |
| `MYSQL_DATABASE` | `AttendanceManagement` |
| `MYSQL_USER` | `faculty_user` or cloud user |
| `MYSQL_PASSWORD` | `YourCloudMySQLPassword` |
| `MONGO_URI` | `mongodb+srv://app_faculty:pwd@cluster.mongodb.net/` |
| `MONGO_DB_NAME` | `AttendanceManagement` |
| `SESSION_COOKIE_SECURE` | `True` |
| `SESSION_COOKIE_HTTPONLY` | `True` |
| `SESSION_COOKIE_SAMESITE` | `Lax` |

5. Click **Create Web Service**. Render will install the dependencies, bind Gunicorn to the web port, and issue a live HTTPS address (e.g. `https://attendance-portal.onrender.com`).

---

## 🧪 Verification & Demonstration Guide

During your college DBMS presentation or project viva:

1. **Relational Schema & Foreign Keys:** Show the Students directory and Courses catalog to illustrate 1-to-many relationships and relational constraints.
2. **Interactive Defaulter List:** Navigate to **Defaulter List**, select Course `IT501`, adjust the threshold slider to `75%`, and run the stored procedure `GenerateDefaulterList`. Show how the backend calls the MySQL procedure directly.
3. **Automated Audit Triggers:** Go to **Attendance Records**, mark an attendance record for a student or update an existing record from Present to Late. Then navigate to **Audit Logs** to demonstrate that the MySQL trigger immediately logged the modification with user and timestamp.
4. **NoSQL Document Storage:** Navigate to **Leave Applications** to demonstrate MongoDB document querying, filtering by status/type, and updating a pending application to Approved with atomic MongoDB document persistence.
5. **Database Diagnostics:** Open **Database Info** to demonstrate dual-engine connection monitoring without exposing credentials.

---

## 📜 License & Acknowledgments

Developed as an academic DBMS mini-project demonstrating modern dual-engine database architecture (MySQL 8.0 relational integrity + MongoDB NoSQL flexible document storage) coupled with Python Flask web engineering.
