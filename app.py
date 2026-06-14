from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey123"

# إنشاء قاعدة البيانات
def init_db():
    conn = sqlite3.connect("habit.db")
    
    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        completed INTEGER DEFAULT 0,
        user_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# الصفحة الرئيسية
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")

    conn = sqlite3.connect("habit.db")
    habits = conn.execute(
        "SELECT * FROM habits WHERE user_id=?",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("index.html", habits=habits)

# تسجيل
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("habit.db")
        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# تسجيل دخول
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("habit.db")
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "❌ البيانات غلط"

    return render_template("login.html")

# إضافة عادة
@app.route("/add", methods=["POST"])
def add():
    if "user_id" not in session:
        return redirect("/login")

    habit = request.form["habit"]

    conn = sqlite3.connect("habit.db")
    conn.execute(
        "INSERT INTO habits (name, completed, user_id) VALUES (?, 0, ?)",
        (habit, session["user_id"])
    )
    conn.commit()
    conn.close()

    return redirect("/")

# حذف عادة
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("habit.db")
    conn.execute("DELETE FROM habits WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/")

# إنجاز عادة ✔️
@app.route("/complete/<int:id>")
def complete(id):
    conn = sqlite3.connect("habit.db")
    conn.execute(
        "UPDATE habits SET completed=1 WHERE id=?",
        (id,)
    )
    conn.commit()
    conn.close()

    return redirect("/")

# تسجيل خروج
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)