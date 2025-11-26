import sqlite3
from datetime import datetime

DB_Path = "ideas.db"


def new_connection():
    connection = sqlite3.connect(DB_Path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ideas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            tags TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)

    # 检查是否已有用户，如果没有则插入默认用户
    cursor.execute("SELECT COUNT(*) FROM users;")
    count = cursor.fetchone()[0]
    
    if count == 0:
        cursor.execute("""
            INSERT INTO users (username, password)
            VALUES (?, ?);
        """, ("zyz", "123456"))

    connection.commit()
    connection.close()


def create_new_idea(title: str, category: str, description: str, tags: str):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO ideas (title, category, description, tags, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (title, category, description, tags, time_now, time_now))

    connection.commit()
    idea_id = cursor.lastrowid
    connection.close()
    return idea_id


def get_all_ideas():
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, category, description, tags, created_at, updated_at
        FROM ideas
        ORDER BY created_at DESC;
    """)
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def get_ideas_by_filter(category: str | None = None, search_text: str | None = None):
    connection = new_connection()
    cursor = connection.cursor()

    query = """
        SELECT id, title, category, description, tags, created_at, updated_at
        FROM ideas
        WHERE 1 = 1
    """
    parameters = []

    if category and category.lower() != "all":
        query += " AND category = ?"
        parameters.append(category)

    if search_text:
        query += " AND (title LIKE ? OR description LIKE ?)"
        like = f"%{search_text}%"
        parameters.extend([like, like])

    query += " ORDER BY created_at DESC;"

    cursor.execute(query, parameters)
    rows = cursor.fetchall()
    connection.close()
    return [dict(row) for row in rows]


def update_idea(idea_id: int, title: str, category: str, description: str, tags: str):
    time_now = datetime.now().isoformat(timespec="seconds")
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE ideas
        SET title = ?, category = ?, description = ?, tags = ?, updated_at = ?
        WHERE id = ?;
    """, (title, category, description, tags, time_now, idea_id))

    connection.commit()
    connection.close()


def delete_idea(idea_id: int):
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM ideas WHERE id = ?;", (idea_id,))

    connection.commit()
    connection.close()


def verify_user(username: str, password: str):
    
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id FROM users
        WHERE username = ? AND password = ?;
    """, (username, password))

    result = cursor.fetchone()
    connection.close()
    
    return result is not None

def delete_ideas_by_category(category: str):
    connection = new_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM ideas WHERE category = ?;", (category,))
    connection.commit()
    cnnection.close()

def reassign_ideas_category(old_category: str, new_category: str):
    connection = new_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE ideas 
        SET category = ?
        WHERE category = ?;
    """, (new_category, old_category))

    connection.commit()
    connection.close()
