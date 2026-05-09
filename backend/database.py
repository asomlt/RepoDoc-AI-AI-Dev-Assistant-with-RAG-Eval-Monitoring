import sqlite3
import os

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DB_PATH = os.path.join(
    BASE_DIR,
    "repo_history.db"
)

conn = sqlite3.connect(
    DB_PATH,
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS repo_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_name TEXT,
        summary TEXT
    )
    """
)

conn.commit()


def save_history(repo_name, summary):

    cursor.execute(

        """
        INSERT INTO repo_history
        (repo_name, summary)
        VALUES (?, ?)
        """,

        (repo_name, summary)

    )

    conn.commit()


def get_history():

    cursor.execute(

        """
        SELECT repo_name, summary
        FROM repo_history
        ORDER BY id DESC
        """

    )

    rows = cursor.fetchall()

    history = []

    for row in rows:

        history.append({

            "repo_name": row[0],

            "summary": row[1]

        })

    return history