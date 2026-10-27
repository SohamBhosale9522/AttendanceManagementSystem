from flask import Blueprint, render_template
from utils.security import login_required
from config import Config, get_mysql_connection, get_mongo_db

db_bp = Blueprint('database', __name__)

@db_bp.route('/database-status')
@login_required
def status():
    # Safely masked configuration information
    db_info = {
        'mysql': {
            'status': False,
            'host': Config.MYSQL_HOST,
            'port': Config.MYSQL_PORT,
            'database': Config.MYSQL_DATABASE,
            'user': Config.MYSQL_USER,
            'version': 'Unknown',
            'tables': [],
            'error': None
        },
        'mongodb': {
            'status': False,
            'host_masked': Config.MONGO_URI.split('@')[-1] if '@' in Config.MONGO_URI else Config.MONGO_URI,
            'database': Config.MONGO_DB_NAME,
            'collections': [],
            'error': None
        }
    }
    
    # 1. MySQL Diagnostic
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT VERSION() AS ver;")
        db_info['mysql']['version'] = cursor.fetchone()['ver']
        
        cursor.execute(
            "SELECT table_name, table_rows, data_length, create_time "
            "FROM information_schema.tables "
            "WHERE table_schema = %s "
            "ORDER BY table_name;",
            (Config.MYSQL_DATABASE,)
        )
        table_meta = cursor.fetchall()
        
        # Get exact row counts for each user table
        for t in table_meta:
            tname = t['table_name']
            cursor.execute(f"SELECT COUNT(*) AS exact_cnt FROM `{tname}`")
            exact_cnt = cursor.fetchone()['exact_cnt']
            db_info['mysql']['tables'].append({
                'name': tname,
                'count': exact_cnt,
                'created': t.get('create_time')
            })
            
        cursor.close()
        conn.close()
        db_info['mysql']['status'] = True
    except Exception as e:
        db_info['mysql']['status'] = False
        db_info['mysql']['error'] = str(e)
        
    # 2. MongoDB Diagnostic
    try:
        db = get_mongo_db()
        db.command('ping')
        for cname in db.list_collection_names():
            cnt = db[cname].count_documents({})
            db_info['mongodb']['collections'].append({
                'name': cname,
                'count': cnt
            })
        db_info['mongodb']['status'] = True
    except Exception as e:
        db_info['mongodb']['status'] = False
        db_info['mongodb']['error'] = str(e)
        
    return render_template('db_status.html', db_info=db_info)
