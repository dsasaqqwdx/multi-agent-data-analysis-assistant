# import sqlite3
# import uuid
# import os
# from datetime import datetime


# DB_PATH = "data/memory.db"


# def get_connection():
#     os.makedirs("data", exist_ok=True)

#     conn = sqlite3.connect(
#         DB_PATH,
#         check_same_thread=False
#     )

#     return conn


# def initialize_database():
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS threads (
#             thread_id TEXT PRIMARY KEY,
#             title TEXT,
#             dataset_path TEXT,
#             dataset_name TEXT,
#             created_at TEXT,
#             updated_at TEXT
#         )
#     """)

#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS messages (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             thread_id TEXT,
#             role TEXT,
#             content TEXT,
#             created_at TEXT
#         )
#     """)

#     conn.commit()
#     conn.close()


# def create_thread(
#     title="New Conversation"
# ):
#     thread_id = str(uuid.uuid4())

#     now = datetime.now().isoformat()

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         INSERT INTO threads (
#             thread_id,
#             title,
#             dataset_path,
#             dataset_name,
#             created_at,
#             updated_at
#         )
#         VALUES (?, ?, ?, ?, ?, ?)
#     """, (
#         thread_id,
#         title,
#         None,
#         None,
#         now,
#         now
#     ))

#     conn.commit()
#     conn.close()

#     return thread_id


# def get_threads():
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT
#             thread_id,
#             title,
#             dataset_name,
#             created_at,
#             updated_at
#         FROM threads
#         ORDER BY updated_at DESC
#     """)

#     rows = cursor.fetchall()

#     conn.close()

#     return rows


# def get_thread(thread_id):
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT
#             thread_id,
#             title,
#             dataset_path,
#             dataset_name,
#             created_at,
#             updated_at
#         FROM threads
#         WHERE thread_id = ?
#     """, (thread_id,))

#     row = cursor.fetchone()

#     conn.close()

#     return row


# def update_thread_dataset(
#     thread_id,
#     dataset_path,
#     dataset_name
# ):
#     now = datetime.now().isoformat()

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         UPDATE threads
#         SET
#             dataset_path = ?,
#             dataset_name = ?,
#             updated_at = ?
#         WHERE thread_id = ?
#     """, (
#         dataset_path,
#         dataset_name,
#         now,
#         thread_id
#     ))

#     conn.commit()
#     conn.close()


# def update_thread_title(
#     thread_id,
#     title
# ):
#     now = datetime.now().isoformat()

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         UPDATE threads
#         SET
#             title = ?,
#             updated_at = ?
#         WHERE thread_id = ?
#     """, (
#         title,
#         now,
#         thread_id
#     ))

#     conn.commit()
#     conn.close()


# def save_message(
#     thread_id,
#     role,
#     content
# ):
#     now = datetime.now().isoformat()

#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         INSERT INTO messages (
#             thread_id,
#             role,
#             content,
#             created_at
#         )
#         VALUES (?, ?, ?, ?)
#     """, (
#         thread_id,
#         role,
#         str(content),
#         now
#     ))

#     cursor.execute("""
#         UPDATE threads
#         SET updated_at = ?
#         WHERE thread_id = ?
#     """, (
#         now,
#         thread_id
#     ))

#     conn.commit()
#     conn.close()


# def get_messages(
#     thread_id
# ):
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         SELECT
#             role,
#             content,
#             created_at
#         FROM messages
#         WHERE thread_id = ?
#         ORDER BY id ASC
#     """, (thread_id,))

#     rows = cursor.fetchall()

#     conn.close()

#     return rows


# def delete_thread(
#     thread_id
# ):
#     conn = get_connection()
#     cursor = conn.cursor()

#     cursor.execute("""
#         DELETE FROM messages
#         WHERE thread_id = ?
#     """, (thread_id,))

#     cursor.execute("""
#         DELETE FROM threads
#         WHERE thread_id = ?
#     """, (thread_id,))

#     conn.commit()
#     conn.close()

import sqlite3
import uuid
import os

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


    # ==========================================
    # CONVERSATION THREADS
    # ==========================================

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


    # ==========================================
    # MESSAGES INSIDE THREAD
    # ==========================================

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            thread_id TEXT,

            role TEXT,

            content TEXT,

            created_at TEXT

        )
        """
    )


    conn.commit()

    conn.close()


# ==========================================
# CREATE THREAD
# ==========================================

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


# ==========================================
# GET ALL THREADS
# ==========================================

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


# ==========================================
# GET SINGLE THREAD
# ==========================================

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


# ==========================================
# UPDATE DATASET
# ==========================================

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


# ==========================================
# UPDATE THREAD TITLE
# ==========================================

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


# ==========================================
# SAVE MESSAGE
# ==========================================

def save_message(

    thread_id,

    role,

    content

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

            created_at

        )

        VALUES (?, ?, ?, ?)
        """,
        (
            thread_id,
            role,
            str(content),
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


# ==========================================
# GET THREAD MESSAGES
# ==========================================

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


# ==========================================
# DELETE THREAD
# ==========================================

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