CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    content TEXT,
    user_id INTEGER REFERENCES users,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE classes (
    id INTEGER PRIMARY KEY,
    title TEXT,
    value TEXT
);

CREATE TABLE note_classes (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes,
    title TEXT,
    value TEXT
);

CREATE TABLE shares (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes,
    user_id INTEGER REFERENCES users
);

CREATE TABLE comments (
    id INTEGER PRIMARY KEY,
    note_id INTEGER REFERENCES notes,
    user_id INTEGER REFERENCES users,
    content TEXT,
    created_at TEXT
);
