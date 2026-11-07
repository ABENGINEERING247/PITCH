import sqlite3
import json
from datetime import datetime

DB_NAME = "pitch_database.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS papers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            subject TEXT,
            created_at TEXT,
            data TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT,
            type TEXT,
            question TEXT,
            options TEXT,
            answer TEXT,
            marks REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll TEXT,
            student TEXT,
            subject TEXT,
            obtained REAL,
            total REAL,
            percentage REAL,
            grade TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_paper(paper_dict, paper_id=None):
    conn = get_connection()
    cursor = conn.cursor()
    title = f"{paper_dict.get('subject', 'Subject')} - {paper_dict.get('exam_type', 'Exam')}"
    subject = paper_dict.get('subject', '')
    data_json = json.dumps(paper_dict)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if paper_id:
        cursor.execute("UPDATE papers SET title=?, subject=?, data=? WHERE id=?", (title, subject, data_json, paper_id))
        conn.commit()
        conn.close()
        return paper_id
    else:
        cursor.execute("INSERT INTO papers (title, subject, created_at, data) VALUES (?, ?, ?, ?)", (title, subject, timestamp, data_json))
        conn.commit()
        pid = cursor.lastrowid
        conn.close()
        return pid

def list_papers():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, subject, created_at FROM papers ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_paper(paper_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM papers WHERE id=?", (paper_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row["data"])
    return None

def save_question(q_dict, subject):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO questions (subject, type, question, options, answer, marks) VALUES (?, ?, ?, ?, ?, ?)",
        (subject, q_dict.get("type"), q_dict.get("question"), json.dumps(q_dict.get("options", [])), q_dict.get("answer"), q_dict.get("marks", 1.0))
    )
    conn.commit()
    conn.close()

def list_questions():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, subject, type, question, marks FROM questions ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def save_result(res_dict):
    conn = get_connection()
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO results (roll, student, subject, obtained, total, percentage, grade, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (res_dict["roll"], res_dict["student"], res_dict["subject"], res_dict["obtained"], res_dict["total"], res_dict["percentage"], res_dict["grade"], timestamp)
    )
    conn.commit()
    conn.close()

def list_results():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT roll, student, subject, obtained, total, percentage, grade, created_at FROM results ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]
