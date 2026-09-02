
import os
import sqlite3
import uuid
import shutil

from datetime import datetime


DB_PATH = "data/memory.db"



def get_connection():

    os.makedirs(
        "data",
        exist_ok=True
    )

    conn = sqlite3.connect(
        DB_PATH,
        check_same_thread=False
    )

    return conn


def initialize_database():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS threads (

            thread_id TEXT PRIMARY KEY,

            title TEXT,

            dataset_path TEXT,

            dataset_name TEXT,

            created_at TEXT,

            updated_at TEXT

        )
        """
    )


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            thread_id TEXT,

            role TEXT,

            content TEXT,

            content_type TEXT DEFAULT 'text',

            created_at TEXT

        )
        """
    )


    cursor.execute(
        "PRAGMA table_info(messages)"
    )


    existing_columns = [

        column[1]

        for column in cursor.fetchall()

    ]


    if "content_type" not in existing_columns:


        cursor.execute(
            """
            ALTER TABLE messages
            ADD COLUMN content_type TEXT
            DEFAULT 'text'
            """
        )


    conn.commit()

    conn.close()



def create_thread(

    title="New Conversation"

):

    thread_id = str(

        uuid.uuid4()

    )


    now = datetime.now().isoformat()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO threads (

            thread_id,

            title,

            dataset_path,

            dataset_name,

            created_at,

            updated_at

        )

        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (

            thread_id,

            title,

            None,

            None,

            now,

            now

        )
    )


    conn.commit()

    conn.close()


    return thread_id


def get_threads():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            thread_id,

            title,

            dataset_name,

            created_at,

            updated_at

        FROM threads

        ORDER BY updated_at DESC
        """
    )


    rows = cursor.fetchall()


    conn.close()


    return rows


def get_thread(

    thread_id

):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            thread_id,

            title,

            dataset_path,

            dataset_name,

            created_at,

            updated_at

        FROM threads

        WHERE thread_id = ?
        """,
        (

            thread_id,

        )
    )


    row = cursor.fetchone()


    conn.close()


    return row



def update_thread_dataset(

    thread_id,

    dataset_path,

    dataset_name

):

    now = datetime.now().isoformat()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE threads

        SET

            dataset_path = ?,

            dataset_name = ?,

            updated_at = ?

        WHERE thread_id = ?
        """,
        (

            dataset_path,

            dataset_name,

            now,

            thread_id

        )
    )


    conn.commit()

    conn.close()


def update_thread_title(

    thread_id,

    title

):

    now = datetime.now().isoformat()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        UPDATE threads

        SET

            title = ?,

            updated_at = ?

        WHERE thread_id = ?
        """,
        (

            title,

            now,

            thread_id

        )
    )


    conn.commit()

    conn.close()



def save_message(

    thread_id,

    role,

    content,

    content_type="text"

):

    now = datetime.now().isoformat()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        INSERT INTO messages (

            thread_id,

            role,

            content,

            content_type,

            created_at

        )

        VALUES (?, ?, ?, ?, ?)
        """,
        (

            thread_id,

            role,

            str(content),

            content_type,

            now

        )
    )


    

    cursor.execute(
        """
        UPDATE threads

        SET updated_at = ?

        WHERE thread_id = ?
        """,
        (

            now,

            thread_id

        )
    )


    conn.commit()

    conn.close()


def get_messages(

    thread_id

):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            role,

            content,

            content_type,

            created_at

        FROM messages

        WHERE thread_id = ?

        ORDER BY id ASC
        """,
        (

            thread_id,

        )
    )


    rows = cursor.fetchall()


    conn.close()


    return rows



def delete_thread(

    thread_id

):

    conn = get_connection()

    cursor = conn.cursor()



    cursor.execute(
        """
        DELETE FROM messages

        WHERE thread_id = ?
        """,
        (

            thread_id,

        )
    )


    

    cursor.execute(
        """
        DELETE FROM threads

        WHERE thread_id = ?
        """,
        (

            thread_id,

        )
    )


    conn.commit()

    conn.close()



    upload_directory = os.path.join(

        "data",

        "uploads",

        thread_id

    )


    if os.path.exists(

        upload_directory

    ):

        try:

            shutil.rmtree(

                upload_directory

            )

        except Exception as e:

            print(

                f"Could not delete uploads: {e}"

            )


   

    visualization_directory = os.path.join(

        "data",

        "visualizations",

        thread_id

    )


    if os.path.exists(

        visualization_directory

    ):

        try:

            shutil.rmtree(

                visualization_directory

            )

        except Exception as e:

            print(

                f"Could not delete visualizations: {e}"

            )