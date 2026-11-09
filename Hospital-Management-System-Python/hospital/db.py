import os
from contextlib import contextmanager
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "hospital_management"),
        autocommit=False,
    )

@contextmanager
def connection():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def fetch_all(query, params=None):
    with connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        rows = cur.fetchall()
        cur.close()
        return rows

def fetch_one(query, params=None):
    rows = fetch_all(query, params)
    return rows[0] if rows else None

def execute(query, params=None):
    with connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params or ())
        result = (cur.lastrowid, cur.rowcount)
        cur.close()
        return result

def call_procedure(name, params=()):
    allowed = {"sp_book_appointment", "sp_add_payment", "sp_patient_appointment_history"}
    if name not in allowed:
        raise ValueError("Unsupported stored procedure")
    with connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.callproc(name, params)
        rows = []
        for result in cur.stored_results():
            rows.extend(result.fetchall())
        cur.close()
        return rows
