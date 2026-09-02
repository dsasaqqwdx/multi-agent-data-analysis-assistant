import sqlite3
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



def initialize_long_term_memory():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS long_term_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory_key TEXT UNIQUE,

            memory_value TEXT,

            category TEXT,

            created_at TEXT,

            updated_at TEXT

        )
        """
    )


    conn.commit()

    conn.close()



def save_memory(

    memory_key,

    memory_value,

    category="general"

):

    now = datetime.now().isoformat()


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT id

        FROM long_term_memory

        WHERE memory_key = ?
        """,
        (
            memory_key,
        )
    )


    existing_memory = cursor.fetchone()


    if existing_memory:

        cursor.execute(
            """
            UPDATE long_term_memory

            SET

                memory_value = ?,

                category = ?,

                updated_at = ?

            WHERE memory_key = ?
            """,
            (
                memory_value,
                category,
                now,
                memory_key
            )
        )

    else:

        cursor.execute(
            """
            INSERT INTO long_term_memory (

                memory_key,

                memory_value,

                category,

                created_at,

                updated_at

            )

            VALUES (?, ?, ?, ?, ?)
            """,
            (
                memory_key,
                memory_value,
                category,
                now,
                now
            )
        )


    conn.commit()

    conn.close()


def get_memory(
    memory_key
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            memory_value

        FROM long_term_memory

        WHERE memory_key = ?
        """,
        (
            memory_key,
        )
    )


    row = cursor.fetchone()


    conn.close()


    if row:

        return row[0]


    return None



def get_all_memories():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT

            memory_key,

            memory_value,

            category

        FROM long_term_memory

        ORDER BY updated_at DESC
        """
    )


    rows = cursor.fetchall()


    conn.close()


    return rows



def search_memory(
    query
):

    conn = get_connection()

    cursor = conn.cursor()


    query_lower = query.lower()


    cursor.execute(
        """
        SELECT

            memory_key,

            memory_value,

            category

        FROM long_term_memory
        """
    )


    rows = cursor.fetchall()


    conn.close()


    relevant_memories = []


    for key, value, category in rows:

        searchable_text = (

            f"{key} "

            f"{value} "

            f"{category}"

        ).lower()


        if any(

            word in searchable_text

            for word in query_lower.split()

            if len(word) > 2

        ):

            relevant_memories.append(
                {
                    "key": key,
                    "value": value,
                    "category": category
                }
            )


    return relevant_memories




def delete_memory(
    memory_key
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        DELETE FROM long_term_memory

        WHERE memory_key = ?
        """,
        (
            memory_key,
        )
    )



    conn.commit()

    conn.close()
import re



def extract_and_save_memory(
    text
):

    text_lower = text.lower()


    patterns = [

        r"my name is ([A-Za-z ]+)",

        r"i am ([A-Za-z ]+)",

        r"i'm ([A-Za-z ]+)",

        r"call me ([A-Za-z ]+)",

    ]


    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )


        if match:

            name = match.group(1).strip()


            # Remove common endings
            name = name.split(
                "."
            )[0]


            name = name.split(
                ","
            )[0]


            # Avoid very long extraction
            if len(name) < 50:

                save_memory(

                    memory_key="user_name",

                    memory_value=name,

                    category="personal"

                )


                return {
                    "saved": True,
                    "key": "user_name",
                    "value": name
                }


    return {
        "saved": False
    }