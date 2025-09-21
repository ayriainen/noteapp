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
