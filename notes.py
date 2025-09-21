"""
The example app dealt with items, this app deals with notes.
Everything had to be customized for notes.
There's also created and updated times.
"""
import db
from datetime import datetime

def add_note(title, content, user_id):
    sql = """INSERT INTO notes (title, content, user_id, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?)"""
    now = datetime.now().isoformat()
    db.execute(sql, [title, content, user_id, now, now])

def get_user_notes(user_id):
    sql = """SELECT id, title, content, created_at, updated_at
             FROM notes
             WHERE user_id = ?
             ORDER BY updated_at DESC"""
    return db.query(sql, [user_id])

def get_note(note_id):
    sql = """SELECT notes.id, notes.title, notes.content, 
                    notes.created_at, notes.updated_at,
                    notes.user_id, users.username
             FROM notes, users
             WHERE notes.user_id = users.id AND notes.id = ?"""
    result = db.query(sql, [note_id])
    return result[0] if result else None

def update_note(note_id, title, content):
    sql = """UPDATE notes SET title = ?, content = ?, updated_at = ?
             WHERE id = ?"""
    now = datetime.now().isoformat()
    db.execute(sql, [title, content, now, note_id])

def remove_note(note_id):
    sql = "DELETE FROM notes WHERE id = ?"
    db.execute(sql, [note_id])

def search_notes(user_id, query):
    sql = """SELECT id, title, content, created_at, updated_at
             FROM notes
             WHERE user_id = ? AND (title LIKE ? OR content LIKE ?)
             ORDER BY updated_at DESC"""
    like = "%" + query + "%"
    return db.query(sql, [user_id, like, like])
