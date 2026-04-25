from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"

# ---------------------- DATABASE ----------------------
def get_db():
    conn = sqlite3.connect("tickets.db")
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

# ---------------------- HOME ----------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    tickets = cursor.fetchall()
    conn.close()

    return render_template("index.html", tickets=tickets)

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
    cursor.execute("INSERT INTO tickets VALUES (NULL,?,?,?,?,?,?)",
                   (name, dept, issue, priority, "Open", date))
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
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)