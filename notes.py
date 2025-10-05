"""
The example app dealt with items, this app deals with notes.
Everything had to be customized for notes.
There's also created and updated times.
Example app's classes was a bit complex and required additions to most functions,
could've probably been simplified.
"""
import db
from datetime import datetime

def get_all_classes():
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def add_note(title, content, user_id, classes):
    sql = """INSERT INTO notes (title, content, user_id, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?)"""
    now = datetime.now().isoformat()
    db.execute(sql, [title, content, user_id, now, now])

    note_id = db.last_insert_id()

    sql = "INSERT INTO note_classes (note_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [note_id, class_title, class_value])

    return note_id

def get_classes(note_id):
    sql = "SELECT title, value FROM note_classes WHERE note_id = ?"
    return db.query(sql, [note_id])

def get_user_notes(user_id):
    sql = """SELECT n.id, n.title, n.content, n.created_at, n.updated_at,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Status'  LIMIT 1) AS status,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Priority' LIMIT 1) AS priority,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Context'  LIMIT 1) AS context
             FROM notes n
             WHERE n.user_id = ?
             ORDER BY n.updated_at DESC, n.id DESC"""
    return db.query(sql, [user_id])

def get_note(note_id):
    sql = """SELECT notes.id, notes.title, notes.content,
                    notes.created_at, notes.updated_at,
                    notes.user_id, users.username
             FROM notes, users
             WHERE notes.user_id = users.id AND notes.id = ?"""
    result = db.query(sql, [note_id])
    return result[0] if result else None

def update_note(note_id, title, content, classes):
    sql = """UPDATE notes SET title = ?, content = ?, updated_at = ?
             WHERE id = ?"""
    now = datetime.now().isoformat()
    db.execute(sql, [title, content, now, note_id])

    sql = "DELETE FROM note_classes WHERE note_id = ?"
    db.execute(sql, [note_id])

    sql = "INSERT INTO note_classes (note_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [note_id, class_title, class_value])

def remove_note(note_id):
    sql = "DELETE FROM note_classes WHERE note_id = ?"
    db.execute(sql, [note_id])
    sql = "DELETE FROM notes WHERE id = ?"
    db.execute(sql, [note_id])

def search_notes(user_id, query):
    sql = """SELECT id, title, content, created_at, updated_at
             FROM notes
             WHERE user_id = ? AND (title LIKE ? OR content LIKE ?)
             ORDER BY updated_at DESC"""
    like = "%" + query + "%"
    return db.query(sql, [user_id, like, like])
