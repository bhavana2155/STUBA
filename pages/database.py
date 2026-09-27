import sqlite3


def get_connection():

    connection = sqlite3.connect(
        "stuba.db",
        check_same_thread=False
    )

    return connection


def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

    # Student information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,

            college TEXT,

            degree TEXT,

            branch TEXT,

            year TEXT,

            semester TEXT,

            daily_study_hours INTEGER

        )
    """)

    # Subjects
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER,

            subject_name TEXT NOT NULL,

            exam_type TEXT,

            difficulty TEXT,

            topics TEXT,

            FOREIGN KEY(student_id)
                REFERENCES students(id)

        )
    """)

    # Quiz results
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_results (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER,

            topic TEXT,

            score INTEGER,

            total_questions INTEGER,

            percentage REAL,

            FOREIGN KEY(student_id)
                REFERENCES students(id)

        )
    """)

    # Study sessions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER,

            topic TEXT,

            duration_minutes INTEGER,

            completed INTEGER,

            FOREIGN KEY(student_id)
                REFERENCES students(id)

        )
    """)

    connection.commit()

    connection.close()


def create_student(
    name,
    college,
    degree,
    branch,
    year,
    semester,
    daily_study_hours
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO students
        (
            name,
            college,
            degree,
            branch,
            year,
            semester,
            daily_study_hours
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        college,
        degree,
        branch,
        year,
        semester,
        daily_study_hours
    ))

    student_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return student_id