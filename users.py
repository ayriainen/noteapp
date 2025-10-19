"""
Similar to the example app users.py except without items, credit there.
User page notes and stats took some work although stats has some repetition. 
"""
from werkzeug.security import check_password_hash, generate_password_hash
import db

def get_user(user_id):
    """Get user by id."""
    sql = "SELECT id, username FROM users WHERE id = ?"
    result = db.query(sql, [user_id])
    return result[0] if result else None

def get_user_by_username(username):
    """Get user by username."""
    sql = "SELECT id, username FROM users WHERE username = ?"
    result = db.query(sql, [username])
    return result[0] if result else None

def create_user(username, password):
    """Create user with username and hashed password."""
    password_hash = generate_password_hash(password)
    sql = "INSERT INTO users (username, password_hash) VALUES (?, ?)"
    db.execute(sql, [username, password_hash])

def check_login(username, password):
    """Checking username and password correctness."""
    sql = "SELECT id, password_hash FROM users WHERE username = ?"
    result = db.query(sql, [username])
    if not result:
        return None

    user_id = result[0]["id"]
    password_hash = result[0]["password_hash"]
    if check_password_hash(password_hash, password):
        return user_id
    else:
        return None

def get_notes(user_id):
    """Get all of a user's notes."""
    sql = """SELECT n.id, n.title, n.updated_at,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Status'  LIMIT 1) AS status,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Priority' LIMIT 1) AS priority,
                    (SELECT value FROM note_classes WHERE note_id = n.id AND title = 'Context'  LIMIT 1) AS context,
                    EXISTS(SELECT 1 FROM shares s WHERE s.note_id = n.id) AS shared
             FROM notes n
             WHERE n.user_id = ?
             ORDER BY n.updated_at DESC, n.id DESC"""
    return db.query(sql, [user_id])

def get_note_stats(user_id):
    """Get stats about a user's notes for the userpage stats display."""
    sql = "SELECT COUNT(*) AS total FROM notes WHERE user_id = ?"
    total = db.query(sql, [user_id])[0]["total"]

    sql = """SELECT COALESCE(
                     (SELECT value
                        FROM note_classes
                       WHERE note_id = n.id AND title = 'Status'
                       LIMIT 1),
                     'Unassigned') AS value,
                    COUNT(*) AS count
             FROM notes n
             WHERE n.user_id = ?
             GROUP BY value
             ORDER BY (value='Unassigned'), value"""
    by_status = db.query(sql, [user_id])

    sql = """SELECT COALESCE(
                     (SELECT value
                        FROM note_classes
                       WHERE note_id = n.id AND title = 'Priority'
                       LIMIT 1),
                     'Unassigned') AS value,
                    COUNT(*) AS count
             FROM notes n
             WHERE n.user_id = ?
             GROUP BY value
             ORDER BY (value='Unassigned'), value"""
    by_priority = db.query(sql, [user_id])

    sql = """SELECT COALESCE(
                     (SELECT value
                        FROM note_classes
                       WHERE note_id = n.id AND title = 'Context'
                       LIMIT 1),
                     'Unassigned') AS value,
                    COUNT(*) AS count
             FROM notes n
             WHERE n.user_id = ?
             GROUP BY value
             ORDER BY (value='Unassigned'), value"""
    by_context = db.query(sql, [user_id])

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_context": by_context,
    }
