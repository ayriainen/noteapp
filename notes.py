"""
The example app dealt with items, this app deals with notes.
Everything had to be customized for notes.
There's also created and updated times.
Example app's classes were a bit complex and required additions to most functions,
could've probably been simplified.
Sharing added complexity with accessability.
"""
import db
from datetime import datetime

def get_all_classes():
    """Get all classes from db."""
    sql = "SELECT title, value FROM classes ORDER BY id"
    result = db.query(sql)

    classes = {}
    for title, value in result:
        classes[title] = []
    for title, value in result:
        classes[title].append(value)

    return classes

def get_classes(note_id):
    """Get a note's classes."""
    sql = "SELECT title, value FROM note_classes WHERE note_id = ?"
    return db.query(sql, [note_id])

def add_note(title, content, user_id, classes):
    """Add a note to db."""
    sql = """INSERT INTO notes (title, content, user_id, created_at, updated_at)
             VALUES (?, ?, ?, ?, ?)"""
    now = datetime.now().isoformat()
    db.execute(sql, [title, content, user_id, now, now])

    note_id = db.last_insert_id()

    sql = "INSERT INTO note_classes (note_id, title, value) VALUES (?, ?, ?)"
    for class_title, class_value in classes:
        db.execute(sql, [note_id, class_title, class_value])

    return note_id

def get_note(note_id):
    """Get a note from db."""
    sql = """SELECT notes.id, notes.title, notes.content,
                    notes.created_at, notes.updated_at,
                    notes.user_id, users.username
             FROM notes, users
             WHERE notes.user_id = users.id AND notes.id = ?"""
    result = db.query(sql, [note_id])
    return result[0] if result else None

def update_note(note_id, title, content, classes):
    """Edits or updates a note in db."""
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
    """Remove a note and it's associating info from db."""
    sql = "DELETE FROM note_classes WHERE note_id = ?"
    db.execute(sql, [note_id])
    sql = "DELETE FROM comments WHERE note_id = ?"
    db.execute(sql, [note_id])
    sql = "DELETE FROM shares WHERE note_id = ?"
    db.execute(sql, [note_id])
    sql = "DELETE FROM notes WHERE id = ?"
    db.execute(sql, [note_id])

def get_user_notes(user_id):
    """Get all of a user's notes. Correlated subquery made it a bit simpler."""
    sql = """SELECT n.id, n.title, n.content, n.created_at, n.updated_at,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Status'  LIMIT 1) AS status,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Priority' LIMIT 1) AS priority,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Context'  LIMIT 1) AS context,
                    EXISTS(SELECT 1 FROM shares s WHERE s.note_id = n.id) AS shared
             FROM notes n
             WHERE n.user_id = ?
             ORDER BY n.updated_at DESC, n.id DESC"""
    return db.query(sql, [user_id])

def get_shared_with_user(user_id):
    sql = """SELECT n.id, n.title, n.updated_at, u.username AS owner_username,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Status'  LIMIT 1) AS status,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Priority' LIMIT 1) AS priority,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Context'  LIMIT 1) AS context
             FROM notes n
             JOIN users u ON n.user_id = u.id
             WHERE EXISTS(SELECT 1 FROM shares s WHERE s.user_id = ? AND s.note_id = n.id)
             ORDER BY n.updated_at DESC, n.id DESC"""
    return db.query(sql, [user_id])

def search_notes(user_id, query):
    """Search notes that a user can access, meaning own notes and shared notes."""
    like = "%" + query + "%"
    sql = """SELECT n.id, n.title, n.updated_at, u.username AS owner_username,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Status'  LIMIT 1) AS status,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Priority' LIMIT 1) AS priority,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Context'  LIMIT 1) AS context,
                    EXISTS(SELECT 1 FROM shares s_me  WHERE s_me.note_id = n.id AND s_me.user_id = ?) AS shared_with_me,
                    CASE WHEN n.user_id = ? AND EXISTS(SELECT 1 FROM shares s_any WHERE s_any.note_id = n.id)
                         THEN 1 ELSE 0 END AS shared_by_me
             FROM notes n
             JOIN users u ON n.user_id = u.id
             WHERE (n.user_id = ? OR EXISTS(SELECT 1 FROM shares s_access WHERE s_access.note_id = n.id AND s_access.user_id = ?))
               AND (n.title LIKE ? OR n.content LIKE ?)
             ORDER BY n.updated_at DESC, n.id DESC"""
    return db.query(sql, [user_id, user_id, user_id, user_id, like, like])

def is_shared_with(note_id, user_id):
    """Check whether the note is stared with the user."""
    sql = "SELECT id FROM shares WHERE note_id = ? AND user_id = ?"
    return bool(db.query(sql, [note_id, user_id]))

def add_share(note_id, user_id):
    """Add a share to a note with a user."""
    sql = "INSERT INTO shares (note_id, user_id) VALUES (?, ?)"
    db.execute(sql, [note_id, user_id])

def remove_share(note_id, user_id):
    """Remove a note's share from a user."""
    sql = "DELETE FROM shares WHERE note_id = ? AND user_id = ?"
    db.execute(sql, [note_id, user_id])

def get_shares(note_id):
    """Get users the note is shared with."""
    sql = """SELECT users.id, users.username
             FROM shares, users
             WHERE shares.note_id = ? AND shares.user_id = users.id
             ORDER BY users.username"""
    return db.query(sql, [note_id])

def add_comment(note_id, user_id, content):
    """Shared notes can have comments. Add a comment to a note."""
    sql = """INSERT INTO comments (note_id, user_id, content, created_at)
             VALUES (?, ?, ?, ?)"""
    now = datetime.now().isoformat()
    db.execute(sql, [note_id, user_id, content, now])

def get_comments(note_id):
    """Get a note's comments."""
    sql = """SELECT comments.id,
                    comments.content,
                    comments.created_at,
                    users.id AS user_id,
                    users.username
             FROM comments, users
             WHERE comments.note_id = ? AND comments.user_id = users.id
             ORDER BY comments.id DESC"""
    return db.query(sql, [note_id])

def get_comment(comment_id):
    """Get a specific comment."""
    sql = """SELECT comments.id,
                    comments.note_id,
                    comments.user_id,
                    comments.content,
                    comments.created_at
             FROM comments
             WHERE comments.id = ?"""
    result = db.query(sql, [comment_id])
    return result[0] if result else None

def update_comment(comment_id, content):
    """Edit or update a comment in db."""
    sql = """UPDATE comments SET content = ? WHERE id = ?"""
    db.execute(sql, [content, comment_id])

def remove_comment(comment_id):
    """Remove a comment from db."""
    sql = """DELETE FROM comments WHERE id = ?"""
    db.execute(sql, [comment_id])
