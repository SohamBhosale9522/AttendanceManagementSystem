import mysql.connector
from contextlib import contextmanager
from config import Config, get_mysql_connection, get_mongo_db

@contextmanager
def get_db_cursor(dictionary=True, commit=True):
    """
    Context manager providing a MySQL cursor.
    Automatically commits on normal completion or rolls back on exceptions,
    and ensures the connection and cursor are cleanly closed.
    """
    conn = None
    cursor = None
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=dictionary)
        yield cursor
        if commit:
            conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_procedure(proc_name, params):
    """
    Safely executes a stored procedure and returns all rows from the first result set.
    """
    conn = None
    cursor = None
    results = []
    try:
        conn = get_mysql_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.callproc(proc_name, params)
        for res in cursor.stored_results():
            results.extend(res.fetchall())
        conn.commit()
        return results
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
