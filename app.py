"""
This is the main file, mostly resembling the example app's app.py.
"""
import re
import secrets
import sqlite3

from flask import Flask
from flask import abort, flash, redirect, render_template, request, session
import markupsafe

import config
import db
import notes
import users

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    if "user_id" not in session:
        abort(403)

def check_csrf():
    if "csrf_token" not in request.form:
        abort(403)
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.route("/")
def index():
    if "user_id" in session:
        user_notes = notes.get_user_notes(session["user_id"])
        return render_template("index.html", notes=user_notes)
    return render_template("index.html", notes=[])

@app.route("/note/<int:note_id>")
def show_note(note_id):
    require_login()
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    if note["user_id"] != session["user_id"]:
        abort(403)
    return render_template("show_note.html", note=note)

@app.route("/search")
def search():
    require_login()
    query = request.args.get("query")
    if query:
        results = notes.search_notes(session["user_id"], query)
    else:
        query = ""
        results = []
    return render_template("search.html", query=query, results=results)

@app.route("/new_note")
def new_note():
    require_login()
    return render_template("new_note.html")

@app.route("/create_note", methods=["POST"])
def create_note():
    require_login()
    check_csrf()

    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    content = request.form["content"]
    if not content or len(content) > 5000:
        abort(403)

    user_id = session["user_id"]
    notes.add_note(title, content, user_id)

    note_id = db.last_insert_id()
    return redirect("/note/" + str(note_id))

@app.route("/edit_note/<int:note_id>")
def edit_note(note_id):
    require_login()
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    if note["user_id"] != session["user_id"]:
        abort(403)
    return render_template("edit_note.html", note=note)

@app.route("/update_note", methods=["POST"])
def update_note():
    require_login()
    check_csrf()

    note_id = request.form["note_id"]
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    if note["user_id"] != session["user_id"]:
        abort(403)

    title = request.form["title"]
    if not title or len(title) > 100:
        abort(403)
    content = request.form["content"]
    if not content or len(content) > 5000:
        abort(403)

    notes.update_note(note_id, title, content)
    return redirect("/note/" + str(note_id))

@app.route("/remove_note/<int:note_id>", methods=["GET", "POST"])
def remove_note(note_id):
    require_login()

    note = notes.get_note(note_id)
    if not note:
        abort(404)
    if note["user_id"] != session["user_id"]:
        abort(403)

    if request.method == "GET":
        return render_template("remove_note.html", note=note)

    if request.method == "POST":
        check_csrf()
        if "remove" in request.form:
            notes.remove_note(note_id)
            return redirect("/")
        else:
            return redirect("/note/" + str(note_id))

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/create_user", methods=["POST"])
def create_user():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]

    if password1 != password2:
        flash("ERROR: Passwords do not match")
        return redirect("/register")

    if len(username) < 3 or len(username) > 20:
        flash("ERROR: Username must be between 3 and 20 characters")
        return redirect("/register")

    if len(password1) < 3:
        flash("ERROR: Password must be at least 3 characters")
        return redirect("/register")

    try:
        users.create_user(username, password1)
    except sqlite3.IntegrityError:
        flash("ERROR: Username is already taken")
        return redirect("/register")

    flash("Account created successfully! Please log in.")
    return redirect("/login")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user_id = users.check_login(username, password)
        if user_id:
            session["user_id"] = user_id
            session["username"] = username
            session["csrf_token"] = secrets.token_hex(16)
            return redirect("/")
        else:
            flash("ERROR: Invalid username or password")
            return redirect("/login")

@app.route("/logout")
def logout():
    if "user_id" in session:
        del session["user_id"]
        del session["username"]
        del session["csrf_token"]
    return redirect("/")

# "localhost" url wasn't working with the example app execution, only ip was
# so instead of "flask run" it's "python3 app.py"
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
