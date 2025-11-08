import sqlite3

connection = sqlite3.connect("forum.db")

with open("schema.sql", "w") as f:
    f.write("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    fullname TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    topic_id INTEGER,
    user_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(topic_id) REFERENCES topics(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);
""")

with open("schema.sql") as f:
    connection.executescript(f.read())

connection.commit()
connection.close()
print("✅ Databasen forum.db har skapats!")
