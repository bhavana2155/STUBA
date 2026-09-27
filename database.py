import sqlite3


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_connection():

    connection = sqlite3.connect(
        "stuba.db",
        check_same_thread=False
    )

    return connection


# ==================================================
# CREATE TABLES
# ==================================================

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()


    # --------------------------------------------------
    # STUDENTS
    # --------------------------------------------------

    cursor.execute(
        """
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
        """
    )


    # --------------------------------------------------
    # MIGRATE STUDENTS TABLE
    # --------------------------------------------------

    cursor.execute(
        "PRAGMA table_info(students)"
    )

    existing_columns = [
        column[1]
        for column in cursor.fetchall()
    ]


    if "learning_style" not in existing_columns:

        cursor.execute(
            """
            ALTER TABLE students
            ADD COLUMN learning_style TEXT
            """
        )


    if "competitive_exam" not in existing_columns:

        cursor.execute(
            """
            ALTER TABLE students
            ADD COLUMN competitive_exam TEXT
            """
        )


    # --------------------------------------------------
    # SUBJECTS
    # --------------------------------------------------

    cursor.execute(
        """
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
        """
    )


    # --------------------------------------------------
    # QUIZ RESULTS
    # --------------------------------------------------

    cursor.execute(
        """
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
        """
    )


    # --------------------------------------------------
    # STUDY SESSIONS
    # --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS study_sessions (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER,

            topic TEXT,

            duration_minutes INTEGER,

            completed INTEGER,

            FOREIGN KEY(student_id)
                REFERENCES students(id)

        )
        """
    )


    # --------------------------------------------------
    # STUDY PLANS
    # --------------------------------------------------

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS study_plans (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            student_id INTEGER,

            exam_name TEXT,

            exam_date TEXT,

            subject_name TEXT,

            topic TEXT,

            priority TEXT,

            difficulty TEXT,

            minutes INTEGER,

            learning_method TEXT,

            reason TEXT,

            exam_strategy TEXT,

            plan_date TEXT,

            completed INTEGER DEFAULT 0,

            created_at TIMESTAMP
                DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(student_id)
                REFERENCES students(id)

        )
        """
    )


    connection.commit()

    connection.close()


# ==================================================
# CREATE STUDENT
# ==================================================

def create_student(
    name,
    college,
    degree,
    branch,
    year,
    semester,
    daily_study_hours,
    learning_style="Simple Explanation",
    competitive_exam=""
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        INSERT INTO students
        (
            name,
            college,
            degree,
            branch,
            year,
            semester,
            daily_study_hours,
            learning_style,
            competitive_exam
        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            name,
            college,
            degree,
            branch,
            year,
            semester,
            daily_study_hours,
            learning_style,
            competitive_exam
        )
    )


    student_id = cursor.lastrowid


    connection.commit()

    connection.close()


    return student_id


# ==================================================
# GET LATEST STUDENT
# ==================================================

def get_latest_student():

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        SELECT *
        FROM students

        ORDER BY id DESC

        LIMIT 1
        """
    )


    student = cursor.fetchone()


    connection.close()


    return student


# ==================================================
# UPDATE STUDENT PROFILE
# ==================================================

def update_student_profile(
    student_id,
    name,
    college,
    degree,
    branch,
    year,
    semester,
    daily_study_hours,
    learning_style,
    competitive_exam
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE students

        SET

            name = ?,

            college = ?,

            degree = ?,

            branch = ?,

            year = ?,

            semester = ?,

            daily_study_hours = ?,

            learning_style = ?,

            competitive_exam = ?

        WHERE id = ?
        """,
        (
            name,
            college,
            degree,
            branch,
            year,
            semester,
            daily_study_hours,
            learning_style,
            competitive_exam,
            student_id
        )
    )


    connection.commit()

    connection.close()


# ==================================================
# SAVE STUDY PLAN
# ==================================================

def save_study_plan(
    student_id,
    exam_name,
    exam_date,
    plan_data
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    # --------------------------------------------------
    # REMOVE OLD PLAN FOR SAME EXAM
    # --------------------------------------------------

    cursor.execute(
        """
        DELETE FROM study_plans

        WHERE student_id = ?

        AND exam_name = ?

        AND exam_date = ?
        """,
        (
            student_id,
            exam_name,
            str(exam_date)
        )
    )


    # --------------------------------------------------
    # INSERT NEW PLAN
    # --------------------------------------------------

    for item in plan_data:

        cursor.execute(
            """
            INSERT INTO study_plans
            (
                student_id,
                exam_name,
                exam_date,
                subject_name,
                topic,
                priority,
                difficulty,
                minutes,
                learning_method,
                reason,
                exam_strategy,
                plan_date,
                completed
            )

            VALUES (
                ?, ?, ?, ?, ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?
            )
            """,
            (
                student_id,

                exam_name,

                str(exam_date),

                item.get(
                    "subject",
                    ""
                ),

                item.get(
                    "topic",
                    ""
                ),

                item.get(
                    "priority",
                    ""
                ),

                item.get(
                    "difficulty",
                    ""
                ),

                item.get(
                    "minutes",
                    0
                ),

                item.get(
                    "learning_method",
                    ""
                ),

                item.get(
                    "reason",
                    ""
                ),

                item.get(
                    "exam_strategy",
                    ""
                ),

                str(
                    item.get(
                        "plan_date",
                        ""
                    )
                ),

                0
            )
        )


    connection.commit()

    connection.close()


# ==================================================
# GET SAVED STUDY PLAN
# ==================================================

def get_saved_study_plan(
    student_id,
    exam_name=None
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    if exam_name:

        cursor.execute(
            """
            SELECT
                id,
                exam_name,
                exam_date,
                subject_name,
                topic,
                priority,
                difficulty,
                minutes,
                learning_method,
                reason,
                exam_strategy,
                plan_date,
                completed
            FROM study_plans

            WHERE student_id = ?

            AND exam_name = ?

            ORDER BY id
            """,
            (
                student_id,
                exam_name
            )
        )

    else:

        cursor.execute(
            """
            SELECT
                id,
                exam_name,
                exam_date,
                subject_name,
                topic,
                priority,
                difficulty,
                minutes,
                learning_method,
                reason,
                exam_strategy,
                plan_date,
                completed
            FROM study_plans

            WHERE student_id = ?

            ORDER BY id DESC
            """,
            (
                student_id,
            )
        )


    plans = cursor.fetchall()


    connection.close()


    return plans


# ==================================================
# MARK STUDY PLAN TASK COMPLETE
# ==================================================

def update_study_plan_completion(
    plan_id,
    completed
):

    create_tables()


    connection = get_connection()

    cursor = connection.cursor()


    cursor.execute(
        """
        UPDATE study_plans

        SET completed = ?

        WHERE id = ?
        """,
        (
            completed,
            plan_id
        )
    )


    connection.commit()

    connection.close()