import sqlite3

DB_FILE = "tasks.db"


def get_db_connection():
    """Returns a connection object with Row factory enabled for dict-like access."""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row  # Enables accessing columns by name
    return conn


def init_db():
    """Creates table and seeds 3 initial tasks ONLY if the database is brand new."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Create table if missing
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS tasks
                   (
                       id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       title
                       TEXT
                       NOT
                       NULL,
                       done
                       BOOLEAN
                       NOT
                       NULL
                       DEFAULT
                       0
                   )
                   """)

    # 2. Check existing row count to avoid duplicate seeds on restart
    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    # 3. Seed initial tasks only when count is 0
    if count == 0:
        initial_tasks = [
            ("Buy groceries", 0),
            ("Finish Week 3 Assignment", 0),
            ("Review SQLite docs", 1)
        ]
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            initial_tasks
        )
        print("Database seeded with 3 default tasks.")

    conn.commit()
    conn.close()