from flask import Flask, render_template, request, redirect, session, url_for, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "hemlig_nyckel_123"
DATABASE = "forum.db"

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()

@app.route("/")
def index():
    db = get_db()
    topics = db.execute("""
        SELECT topics.id, topics.title, topics.created_at, users.username
        FROM topics JOIN users ON topics.user_id = users.id
        ORDER BY topics.created_at DESC
    """).fetchall()
    return render_template("index.html", topics=topics)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        fullname = request.form["fullname"]

        db = get_db()
        hash_pw = generate_password_hash(password)
        try:
            db.execute("INSERT INTO users (username, password_hash, fullname) VALUES (?, ?, ?)",
                       (username, hash_pw, fullname))
            db.commit()
            return redirect("/login")
        except sqlite3.IntegrityError:
            return "Användarnamnet är redan taget."
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect("/")
        else:
            return "Fel användarnamn eller lösenord."
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/topic/<int:id>")
def topic(id):
    db = get_db()
    topic = db.execute("""
        SELECT topics.*, users.username 
        FROM topics JOIN users ON topics.user_id = users.id
        WHERE topics.id = ?
    """, (id,)).fetchone()

    posts = db.execute("""
        SELECT posts.*, users.username
        FROM posts JOIN users ON posts.user_id = users.id
        WHERE topic_id = ?
        ORDER BY posts.created_at ASC
    """, (id,)).fetchall()

    return render_template("topic.html", topic=topic, posts=posts)

@app.route("/new_topic", methods=["GET", "POST"])
def new_topic():
    if "user_id" not in session:
        return redirect("/login")
    if request.method == "POST":
        title = request.form["title"]
        db = get_db()
        db.execute("INSERT INTO topics (title, user_id) VALUES (?, ?)", (title, session["user_id"]))
        db.commit()
        return redirect("/")
    return render_template("new_topic.html")

@app.route("/reply/<int:topic_id>", methods=["POST"])
def reply(topic_id):
    if "user_id" not in session:
        return redirect("/login")
    content = request.form["content"]
    db = get_db()
    db.execute("INSERT INTO posts (content, topic_id, user_id) VALUES (?, ?, ?)",
               (content, topic_id, session["user_id"]))
    db.commit()
    return redirect(url_for("topic", id=topic_id))

if __name__ == "__main__":
    app.run(debug=True)
