import sqlite3, json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent.parent / "pitch.db"

def conn():
    c=sqlite3.connect(DB_PATH); c.row_factory=sqlite3.Row; return c

def init_db():
    with conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS papers(
        id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, subject TEXT, payload TEXT, created_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, type TEXT, question TEXT, payload TEXT, marks REAL)""")
        c.execute("""CREATE TABLE IF NOT EXISTS results(
        id INTEGER PRIMARY KEY AUTOINCREMENT, roll_no TEXT, student TEXT, subject TEXT,
        obtained REAL, total REAL, percentage REAL, grade TEXT, status TEXT, created_at TEXT)""")

def save_paper(paper, paper_id=None):
    title=f"{paper.get('exam_type','Exam')} - {paper.get('subject','')}"
    payload=json.dumps(paper,ensure_ascii=False)
    with conn() as c:
        if paper_id:
            c.execute("UPDATE papers SET title=?,subject=?,payload=? WHERE id=?",(title,paper.get("subject",""),payload,paper_id))
            return paper_id
        cur=c.execute("INSERT INTO papers(title,subject,payload,created_at) VALUES(?,?,?,?)",(title,paper.get("subject",""),payload,datetime.now().isoformat(timespec="seconds")))
        return cur.lastrowid

def list_papers():
    with conn() as c: rows=c.execute("SELECT * FROM papers ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]

def get_paper(pid):
    with conn() as c: row=c.execute("SELECT payload FROM papers WHERE id=?",(pid,)).fetchone()
    return json.loads(row["payload"]) if row else None

def save_question(q, subject):
    with conn() as c:
        c.execute("INSERT INTO questions(subject,type,question,payload,marks) VALUES(?,?,?,?,?)",
        (subject,q.get("type",""),q.get("question",""),json.dumps(q,ensure_ascii=False),q.get("marks",0)))

def list_questions():
    with conn() as c: rows=c.execute("SELECT * FROM questions ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]

def save_result(r):
    with conn() as c:
        c.execute("""INSERT INTO results(roll_no,student,subject,obtained,total,percentage,grade,status,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)""",(r["roll_no"],r["student"],r["subject"],r["obtained"],r["total"],r["percentage"],r["grade"],r["status"],datetime.now().isoformat(timespec="seconds")))

def list_results():
    with conn() as c: rows=c.execute("SELECT roll_no,student,subject,obtained,total,percentage,grade,status FROM results ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]
