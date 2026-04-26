from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- DATABASE ----------------------
def get_db():
    conn = sqlite3.connect("tickets.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        department TEXT,
        issue TEXT,
        priority TEXT,
        status TEXT,
        date TEXT
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ---------------------- LOGIN ----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form["password"] == "admin123":
            session["user"] = True
            return redirect("/")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ---------------------- DASHBOARD ----------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()

    # Filters
    priority = request.args.get("priority")
    status = request.args.get("status")
    search = request.args.get("search")

    query = "SELECT * FROM tickets WHERE 1=1"
    params = []

    if priority:
        query += " AND priority=?"
        params.append(priority)

    if status:
        query += " AND status=?"
        params.append(status)

    if search:
        query += " AND issue LIKE ?"
        params.append(f"%{search}%")

    cursor.execute(query, params)
    tickets = cursor.fetchall()

    # Stats
    cursor.execute("SELECT COUNT(*) FROM tickets")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Open'")
    open_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE priority='High'")
    high_count = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tickets WHERE status='Closed'")
    closed_count = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        tickets=tickets,
        total=total,
        open_count=open_count,
        high_count=high_count,
        closed_count=closed_count
    )

# ---------------------- ADD ----------------------
@app.route("/add", methods=["POST"])
def add_ticket():
    if "user" not in session:
        return redirect("/login")

    name = request.form["name"]
    dept = request.form["dept"]
    issue = request.form["issue"]
    priority = request.form["priority"]

    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (name, department, issue, priority, status, date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, dept, issue, priority, "Open", date))

    conn.commit()
    conn.close()

    return redirect("/")

# ---------------------- CLOSE ----------------------
@app.route("/close/<int:id>")
def close_ticket(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE tickets SET status='Closed' WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

# ---------------------- DELETE ----------------------
@app.route("/delete/<int:id>")
def delete_ticket(id):
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tickets WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

# ---------------------- RUN ----------------------
if __name__ == "__main__":
    app.run(debug=True)