import os
import time
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    # Retry connecting up to 10 times if Postgres is still initializing
    retries = 10
    while retries > 0:
        try:
            return psycopg.connect(DATABASE_URL, row_factory=dict_row)
        except psycopg.OperationalError:
            retries -= 1
            if retries == 0:
                raise
            time.sleep(1)


def init_db():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS tasks
                        (
                            id
                            SERIAL
                            PRIMARY
                            KEY,
                            title
                            TEXT
                            NOT
                            NULL,
                            done
                            BOOLEAN
                            DEFAULT
                            FALSE
                        );
                        """)
            cur.execute("SELECT COUNT(*) FROM tasks;")
            row = cur.fetchone()
            count = row["count"] if isinstance(row, dict) else row[0]

            if count == 0:
                cur.execute("""
                            INSERT INTO tasks (title, done)
                            VALUES ('Learn Docker basics', true),
                                   ('Connect Postgres to Python', false),
                                   ('Build full CRUD API', false);
                            """)
            conn.commit()


def get_all_tasks():
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id ASC;")
            return cur.fetchall()


def get_task_by_id(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
            return cur.fetchone()


def create_task(title: str, done: bool = False):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *;",
                (title, done)
            )
            task = cur.fetchone()
            conn.commit()
            return task


def update_task(task_id: int, title: str, done: bool):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *;",
                (title, done, task_id)
            )
            task = cur.fetchone()
            conn.commit()
            return task


def delete_task(task_id: int):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
            deleted = cur.fetchone()
            conn.commit()
            return deleted is not None