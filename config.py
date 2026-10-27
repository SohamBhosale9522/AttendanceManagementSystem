import os
from dotenv import load_dotenv
import mysql.connector
from pymongo import MongoClient

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-fallback-dev-secret-key-change-in-prod')
    
    # MySQL Database Config
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT', 3306))
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'AttendanceManagement')
    MYSQL_USER = os.getenv('MYSQL_USER', 'faculty_user')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'ReplaceWithAStrongPassword!')
    
    # MongoDB Config
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
    MONGO_DB_NAME = os.getenv('MONGO_DB_NAME', 'AttendanceManagement')
    
    # Security & Session Settings
    SESSION_COOKIE_HTTPONLY = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() == 'true'
    SESSION_COOKIE_SAMESITE = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'

# Global reusable MongoClient instance (thread-safe connection pool)
_mongo_client = None

def get_mysql_connection():
    """Returns a new MySQL database connection."""
    return mysql.connector.connect(
        host=Config.MYSQL_HOST,
        port=Config.MYSQL_PORT,
        user=Config.MYSQL_USER,
        password=Config.MYSQL_PASSWORD,
        database=Config.MYSQL_DATABASE,
        autocommit=False
    )

def get_mongo_client():
    """Returns the shared MongoClient instance with connection pooling."""
    global _mongo_client
    if _mongo_client is None:
        _mongo_client = MongoClient(Config.MONGO_URI, serverSelectionTimeoutMS=3000)
    return _mongo_client

def get_mongo_db():
    """Returns the MongoDB database instance."""
    return get_mongo_client()[Config.MONGO_DB_NAME]

def close_mongo_client():
    """Closes the global MongoClient if opened."""
    global _mongo_client
    if _mongo_client is not None:
        _mongo_client.close()
        _mongo_client = None

def test_db_connections():
    """Tests MySQL and MongoDB connections and returns status info."""
    results = {
        'mysql': {'status': False, 'message': '', 'tables': []},
        'mongodb': {'status': False, 'message': '', 'collections': []}
    }
    
    # Test MySQL
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor()
        cursor.execute("SHOW TABLES;")
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        results['mysql']['status'] = True
        results['mysql']['message'] = 'Connected successfully to MySQL 8.0'
        results['mysql']['tables'] = tables
    except Exception as e:
        results['mysql']['status'] = False
        results['mysql']['message'] = f'MySQL Connection Error: {str(e)}'
        
    # Test MongoDB
    try:
        db = get_mongo_db()
        db.command('ping')
        collections = db.list_collection_names()
        results['mongodb']['status'] = True
        results['mongodb']['message'] = 'Connected successfully to MongoDB'
        results['mongodb']['collections'] = collections
    except Exception as e:
        results['mongodb']['status'] = False
        results['mongodb']['message'] = f'MongoDB Connection Error: {str(e)}'
        
    return results
