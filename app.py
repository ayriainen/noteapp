"""
This is the main file, mostly resembling the example app's app.py.
Note sharing added bothersome complexity.
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
        me = session["user_id"]
        your_notes = notes.get_user_notes(me)
        shared_notes = notes.get_shared_with_user(me)
        return render_template("index.html", notes=your_notes, shared_notes=shared_notes)
    return render_template("index.html", notes=[], shared_notes=[])

@app.route("/note/<int:note_id>")
def show_note(note_id):
    require_login()
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    me = session["user_id"]
    if note["user_id"] != me and not notes.is_shared_with(note_id, me):
        abort(403)
    classes = notes.get_classes(note_id)
    shared_users = notes.get_shares(note_id) if note["user_id"] == me else []
    comments = notes.get_comments(note_id)
    return render_template("show_note.html",
                           note=note,
                           classes=classes,
                           shared_users=shared_users,
                           comments=comments)

@app.route("/search")
def search():
    require_login()
    query = request.args.get("query")
    if query:
        results = notes.search_accessible(session["user_id"], query)
    else:
        query = ""
        results = []
    return render_template("search.html", query=query, results=results)

@app.route("/new_note")
def new_note():
    require_login()
    classes = notes.get_all_classes()
    return render_template("new_note.html", classes=classes)

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

    all_classes = notes.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    note_id = notes.add_note(title, content, user_id, classes)
    return redirect("/note/" + str(note_id))

@app.route("/edit_note/<int:note_id>")
def edit_note(note_id):
    require_login()
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    if note["user_id"] != session["user_id"]:
        abort(403)

    all_classes = notes.get_all_classes()
    classes = {}
    for my_class in all_classes:
        classes[my_class] = ""
    for entry in notes.get_classes(note_id):
        classes[entry["title"]] = entry["value"]

    return render_template("edit_note.html", note=note, classes=classes, all_classes=all_classes)

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

    all_classes = notes.get_all_classes()

    classes = []
    for entry in request.form.getlist("classes"):
        if entry:
            class_title, class_value = entry.split(":")
            if class_title not in all_classes:
                abort(403)
            if class_value not in all_classes[class_title]:
                abort(403)
            classes.append((class_title, class_value))

    notes.update_note(note_id, title, content, classes)

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

@app.route("/share_note", methods=["POST"])
def share_note():
    require_login()
    check_csrf()

    note_id = int(request.form["note_id"])
    username = request.form["username"].strip()

    note = notes.get_note(note_id)
    if not note or note["user_id"] != session["user_id"]:
        abort(403)

    target = users.get_user_by_username(username)
    if not target:
        flash("ERROR: User not found")
        return redirect("/note/" + str(note_id))
    if target["id"] == session["user_id"]:
        flash("ERROR: You already own this note")
        return redirect("/note/" + str(note_id))

    if not notes.is_shared_with(note_id, target["id"]):
        notes.add_share(note_id, target["id"])
        flash("Shared with " + target["username"])
    else:
        flash("Already shared with " + target["username"])

    return redirect("/note/" + str(note_id))

@app.route("/unshare_note", methods=["POST"])
def unshare_note():
    require_login()
    check_csrf()

    note_id = int(request.form["note_id"])
    user_id = int(request.form["user_id"])

    note = notes.get_note(note_id)
    if not note or note["user_id"] != session["user_id"]:
        abort(403)

    notes.remove_share(note_id, user_id)
    flash("Sharing removed")
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
    return redirect("/login")

@app.route("/add_comment", methods=["POST"])
def add_comment():
    require_login()
    check_csrf()
    note_id = int(request.form["note_id"])
    content = request.form["content"].strip()
    if not content or len(content) > 2000:
        flash("ERROR: Comment can be at most 2000 characters")
        return redirect("/note/" + str(note_id))
    note = notes.get_note(note_id)
    if not note:
        abort(404)
    me = session["user_id"]
    if note["user_id"] != me and not notes.is_shared_with(note_id, me):
        abort(403)
    notes.add_comment(note_id, me, content)
    return redirect("/note/" + str(note_id))

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
def edit_comment(comment_id):
    require_login()
    comment = notes.get_comment(comment_id)
    if not comment:
        abort(404)
    note = notes.get_note(comment["note_id"])
    if not note:
        abort(404)
    me = session["user_id"]
    if comment["user_id"] != me:
        abort(403)
    if request.method == "GET":
        return render_template("edit_comment.html", comment=comment, note=note)
    check_csrf()
    content = request.form["content"].strip()
    if not content or len(content) > 2000:
        flash("ERROR: Comment must be 1–2000 characters")
        return redirect("/edit_comment/" + str(comment_id))
    notes.update_comment(comment_id, content)
    return redirect("/note/" + str(comment["note_id"]))

@app.route("/remove_comment/<int:comment_id>", methods=["POST"])
def remove_comment(comment_id):
    require_login()
    check_csrf()
    comment = notes.get_comment(comment_id)
    if not comment:
        abort(404)
    note = notes.get_note(comment["note_id"])
    if not note:
        abort(404)
    me = session["user_id"]
    if comment["user_id"] != me:
        abort(403)
    notes.remove_comment(comment_id)
    return redirect("/note/" + str(comment["note_id"]))

@app.route("/user/<int:user_id>")
def show_user(user_id):
    user = users.get_user(user_id)
    if not user:
        abort(404)

    # only own notes for now
    if "user_id" in session and session["user_id"] == user_id:
        user_notes = users.get_notes(user_id)
        note_stats = users.get_note_stats(user_id)
    else:
        user_notes = []
        note_stats = None

    return render_template("show_user.html", user=user, notes=user_notes, stats=note_stats)

# "localhost" url wasn't working with the example app execution, only ip was
# so instead of "flask run" it's "python3 app.py"
if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
