import unittest
import os
import sys
import warnings
from datetime import date

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
import config
from utils.db import get_db_cursor, execute_procedure
from config import get_mongo_db, close_mongo_client

class AttendanceManagementSystemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore', category=DeprecationWarning)
        warnings.simplefilter('ignore', category=ResourceWarning)
        cls.app = create_app()
        cls.app.config['TESTING'] = True

    def setUp(self):
        # Fresh test client for every test case
        self.client = self.app.test_client()

    @classmethod
    def tearDownClass(cls):
        close_mongo_client()

    def login_faculty(self):
        """Helper to simulate faculty login session."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'faculty1'
            sess['full_name'] = 'Prof. Mehta'
            sess['role'] = 'faculty'
            sess['email'] = 'mehta@college.edu'

    def test_01_db_connections(self):
        """Test direct connection to MySQL and MongoDB."""
        res = config.test_db_connections()
        self.assertTrue(res['mysql']['status'], f"MySQL failed: {res['mysql'].get('message')}")
        self.assertTrue(res['mongodb']['status'], f"MongoDB failed: {res['mongodb'].get('message')}")
        self.assertIn('student', [t.lower() for t in res['mysql']['tables']])
        self.assertIn('leave_applications', res['mongodb']['collections'])

    def test_02_unauthenticated_redirects(self):
        """Test that unauthenticated requests to protected endpoints redirect to login."""
        protected_urls = ['/dashboard', '/students', '/courses', '/attendance', '/defaulters', '/leaves', '/audit-logs']
        for url in protected_urls:
            response = self.client.get(url, follow_redirects=False)
            self.assertEqual(response.status_code, 302, f"URL {url} did not redirect")
            self.assertIn('/login', response.headers.get('Location', ''))

    def test_03_login_page_renders(self):
        """Test that the login page loads with 200 OK."""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Faculty Username', response.data)
        self.assertIn(b'Attendance Management', response.data)

    def test_04_valid_faculty_login(self):
        """Test authenticating with valid faculty credentials."""
        with self.client as c:
            c.get('/login')
            with c.session_transaction() as sess:
                csrf = sess.get('_csrf_token')
            post_resp = c.post('/login', data={
                'csrf_token': csrf,
                'username': 'faculty1',
                'password': 'Faculty@123'
            }, follow_redirects=True)
            self.assertEqual(post_resp.status_code, 200)
            with c.session_transaction() as sess:
                self.assertEqual(sess.get('username'), 'faculty1')
            self.assertIn(b'Academic Overview Dashboard', post_resp.data)

    def test_05_invalid_login_rejection(self):
        """Test that invalid credentials fail gracefully."""
        with self.client as c:
            c.get('/login')
            with c.session_transaction() as sess:
                csrf = sess.get('_csrf_token')
            post_resp = c.post('/login', data={
                'csrf_token': csrf,
                'username': 'wrong_user',
                'password': 'WrongPassword999'
            }, follow_redirects=True)
            self.assertEqual(post_resp.status_code, 200)
            self.assertIn(b'Invalid username or password', post_resp.data)

    def test_06_dashboard_loads(self):
        """Test that authenticated dashboard loads live statistics."""
        self.login_faculty()
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Total Students', response.data)
        self.assertIn(b'Active Courses', response.data)
        self.assertIn(b'Attendance Records', response.data)
        self.assertIn(b'Pending Leaves', response.data)

    def test_07_students_directory(self):
        """Test students table retrieval."""
        self.login_faculty()
        response = self.client.get('/students')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'IT001', response.data)
        self.assertIn(b'Aarav Sharma', response.data)

    def test_08_courses_catalog(self):
        """Test course catalog retrieval."""
        self.login_faculty()
        response = self.client.get('/courses')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'IT501', response.data)
        self.assertIn(b'Database Management Systems', response.data)

    def test_09_attendance_records(self):
        """Test attendance list endpoint."""
        self.login_faculty()
        response = self.client.get('/attendance')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Attendance Logs', response.data)

    def test_10_stored_procedure_defaulter_list(self):
        """Test calling GenerateDefaulterList stored procedure."""
        self.login_faculty()
        response = self.client.get('/defaulters?course_id=1&threshold=75.0')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'GenerateDefaulterList', response.data)
        # Directly test procedure via db util
        rows = execute_procedure('GenerateDefaulterList', [1, 75.0])
        self.assertIsInstance(rows, list)
        self.assertTrue(len(rows) >= 1)
        self.assertEqual(rows[0]['roll_no'], 'IT005')

    def test_11_mongodb_leave_applications(self):
        """Test retrieving leave applications from MongoDB."""
        self.login_faculty()
        response = self.client.get('/leaves')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LA001', response.data)
        self.assertIn(b'Aarav Sharma', response.data)
        self.assertIn(b'Medical', response.data)

    def test_12_audit_logs_read_only(self):
        """Test audit logs page rendering."""
        self.login_faculty()
        response = self.client.get('/audit-logs')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Audit History Records', response.data)

    def test_13_database_status_page(self):
        """Test database diagnostics page without leaking credentials."""
        self.login_faculty()
        response = self.client.get('/database-status')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'MySQL 8.0 Relational Engine', response.data)
        self.assertIn(b'MongoDB NoSQL Document Engine', response.data)
        # Ensure password is NOT leaked in output
        self.assertNotIn(b'ReplaceWithAStrongPassword!', response.data)
        self.assertNotIn(b'Soham@12345', response.data)

    def test_14_mark_attendance_and_audit_trigger(self):
        """Test marking attendance and verifying trigger trg_attendance_insert generates AuditLog."""
        self.login_faculty()
        test_date = '2026-10-25'
        
        # Clean any preexisting test record for student 3 on 2026-10-25 in course 1
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(
                "DELETE FROM Attendance_Record WHERE student_id = 3 AND course_id = 1 AND attendance_date = %s",
                (test_date,)
            )

        with self.client as c:
            c.get('/attendance')
            with c.session_transaction() as sess:
                csrf = sess.get('_csrf_token')
            resp = c.post('/attendance/mark', data={
                'csrf_token': csrf,
                'student_id': '3',
                'course_id': '1',
                'classroom_id': '1',
                'attendance_date': test_date,
                'status': 'Present'
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'Attendance successfully recorded', resp.data)

        # Verify AuditLog has the trigger-generated INSERT entry
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM AuditLog WHERE action_type = 'INSERT' ORDER BY log_id DESC LIMIT 1"
            )
            latest_log = cursor.fetchone()
            self.assertIsNotNone(latest_log)
            self.assertIn('Present', latest_log['action_details'])
            self.assertEqual(latest_log['changed_by'], 'faculty1')

    def test_15_update_attendance_and_audit_trigger(self):
        """Test updating attendance status and verifying trigger trg_attendance_update generates AuditLog."""
        self.login_faculty()
        # Find an existing record ID and its status
        with get_db_cursor(commit=False) as cursor:
            cursor.execute("SELECT attendance_id, status FROM Attendance_Record LIMIT 1")
            rec = cursor.fetchone()
            rec_id = rec['attendance_id']
            curr_status = rec['status']

        new_status = 'Absent' if curr_status != 'Absent' else 'Present'

        with self.client as c:
            c.get('/attendance')
            with c.session_transaction() as sess:
                csrf = sess.get('_csrf_token')
            resp = c.post(f'/attendance/update/{rec_id}', data={
                'csrf_token': csrf,
                'status': new_status
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'status updated successfully', resp.data)

        # Verify AuditLog has the trigger-generated UPDATE entry
        with get_db_cursor(commit=False) as cursor:
            cursor.execute(
                "SELECT * FROM AuditLog WHERE action_type = 'UPDATE' AND attendance_id = %s ORDER BY log_id DESC LIMIT 1",
                (rec_id,)
            )
            latest_log = cursor.fetchone()
            self.assertIsNotNone(latest_log)
            self.assertIn(f'New status: {new_status}', latest_log['action_details'])

    def test_16_leave_status_update_in_mongodb(self):
        """Test approving a leave in MongoDB and validating document change."""
        self.login_faculty()
        db = get_mongo_db()
        test_app = db.leave_applications.find_one({"application_id": "LA004"})
        self.assertIsNotNone(test_app)

        with self.client as c:
            c.get('/leaves')
            with c.session_transaction() as sess:
                csrf = sess.get('_csrf_token')
            resp = c.post('/leaves/update-status', data={
                'csrf_token': csrf,
                'application_id': 'LA004',
                'status': 'Approved'
            }, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

        # Verify directly in MongoDB
        updated_doc = db.leave_applications.find_one({"application_id": "LA004"})
        self.assertEqual(updated_doc['status'], 'Approved')
        self.assertEqual(updated_doc['reviewed_by'], 'faculty1')

        # Revert LA004 back to Pending to preserve original sample state
        db.leave_applications.update_one({"application_id": "LA004"}, {"$set": {"status": "Pending"}})

if __name__ == '__main__':
    unittest.main()
