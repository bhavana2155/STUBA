import streamlit as st
import sqlite3
import pandas as pd
from database import get_latest_student


st.set_page_config(
    page_title="Progress - STUBA",
    page_icon="📊",
    layout="wide"
)


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

def get_connection():

    return sqlite3.connect(
        "stuba.db",
        check_same_thread=False
    )


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📊 My Progress")

st.write(
    "STUBA analyzes your quiz performance and study "
    "activity to identify strong and weak areas."
)

st.divider()


# --------------------------------------------------
# GET STUDENT
# --------------------------------------------------

student = get_latest_student()


if student is None:

    st.warning(
        "⚠️ Please save your profile first."
    )

    st.stop()


student_id = student[0]

student_name = student[1]


# --------------------------------------------------
# FETCH BASIC STATISTICS
# --------------------------------------------------

connection = get_connection()

cursor = connection.cursor()


# Subjects

cursor.execute(
    """
    SELECT COUNT(*)
    FROM subjects
    WHERE student_id = ?
    """,
    (student_id,)
)

subject_count = cursor.fetchone()[0]


# Quiz attempts

cursor.execute(
    """
    SELECT COUNT(*)
    FROM quiz_results
    WHERE student_id = ?
    """,
    (student_id,)
)

quiz_attempts = cursor.fetchone()[0]


# Average score

cursor.execute(
    """
    SELECT AVG(percentage)
    FROM quiz_results
    WHERE student_id = ?
    """,
    (student_id,)
)

average_score = cursor.fetchone()[0]


# Completed study sessions

cursor.execute(
    """
    SELECT COUNT(*)
    FROM study_sessions
    WHERE student_id = ?
    AND completed = 1
    """,
    (student_id,)
)

completed_sessions = cursor.fetchone()[0]


# Total study time

cursor.execute(
    """
    SELECT COALESCE(
        SUM(duration_minutes),
        0
    )
    FROM study_sessions
    WHERE student_id = ?
    AND completed = 1
    """,
    (student_id,)
)

total_study_minutes = cursor.fetchone()[0]


connection.close()


# --------------------------------------------------
# TOP METRICS
# --------------------------------------------------

st.subheader("📈 Learning Overview")


col1, col2, col3, col4, col5 = st.columns(5)


with col1:

    st.metric(
        "📚 Subjects",
        subject_count
    )


with col2:

    st.metric(
        "📝 Quizzes",
        quiz_attempts
    )


with col3:

    if average_score is not None:

        st.metric(
            "🎯 Avg Accuracy",
            f"{average_score:.0f}%"
        )

    else:

        st.metric(
            "🎯 Avg Accuracy",
            "—"
        )


with col4:

    st.metric(
        "⏱️ Sessions",
        completed_sessions
    )


with col5:

    st.metric(
        "⌛ Study Time",
        f"{total_study_minutes} min"
    )


# --------------------------------------------------
# OVERALL PERFORMANCE
# --------------------------------------------------

st.divider()

st.subheader(
    "🧠 Overall Understanding"
)


if average_score is None:

    st.info(
        "Take your first AI Tutor quiz to start "
        "building your performance profile."
    )

else:

    st.progress(
        min(
            average_score / 100,
            1.0
        )
    )


    if average_score >= 80:

        st.success(
            f"💪 Strong performance — "
            f"{average_score:.0f}% average accuracy."
        )

    elif average_score >= 60:

        st.warning(
            f"👍 Average performance — "
            f"{average_score:.0f}% average accuracy."
        )

    else:

        st.error(
            f"📚 Needs improvement — "
            f"{average_score:.0f}% average accuracy."
        )


# --------------------------------------------------
# TOPIC PERFORMANCE
# --------------------------------------------------

st.divider()

st.subheader(
    "🎯 Topic Performance"
)


connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    SELECT
        topic,
        AVG(percentage) AS average_score,
        COUNT(*) AS attempts
    FROM quiz_results
    WHERE student_id = ?
    GROUP BY topic
    ORDER BY average_score ASC
    """,
    (student_id,)
)


topic_results = cursor.fetchall()


connection.close()


if not topic_results:

    st.info(
        "No topic performance available yet."
    )

else:

    for topic, score, attempts in topic_results:

        if score >= 80:

            status = "🟢 Strong"

        elif score >= 60:

            status = "🟡 Average"

        else:

            status = "🔴 Weak"


        with st.container(
            border=True
        ):

            col1, col2, col3, col4 = st.columns(4)


            with col1:

                st.markdown(
                    f"### 📘 {topic}"
                )


            with col2:

                st.write(
                    f"**Accuracy:** "
                    f"{score:.0f}%"
                )


            with col3:

                st.write(
                    f"**Attempts:** "
                    f"{attempts}"
                )


            with col4:

                st.write(
                    f"**Status:** "
                    f"{status}"
                )


# --------------------------------------------------
# PERFORMANCE CHART
# --------------------------------------------------

if topic_results:

    st.divider()

    st.subheader(
        "📊 Topic Accuracy"
    )


    chart_data = pd.DataFrame(
        {
            "Topic": [
                result[0]
                for result in topic_results
            ],

            "Accuracy": [
                result[1]
                for result in topic_results
            ]
        }
    )


    st.bar_chart(
        chart_data.set_index("Topic")
    )


# --------------------------------------------------
# QUIZ HISTORY
# --------------------------------------------------

st.divider()

st.subheader(
    "📝 Quiz History"
)


connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    SELECT
        topic,
        score,
        total_questions,
        percentage
    FROM quiz_results
    WHERE student_id = ?
    ORDER BY id DESC
    """,
    (student_id,)
)


quiz_results = cursor.fetchall()


connection.close()


if quiz_results:

    for result in quiz_results:

        topic = result[0]

        score = result[1]

        total = result[2]

        percentage = result[3]


        with st.container(
            border=True
        ):

            col1, col2, col3 = st.columns(3)


            with col1:

                st.write(
                    f"**📘 {topic}**"
                )


            with col2:

                st.write(
                    f"**Score:** "
                    f"{score}/{total}"
                )


            with col3:

                st.write(
                    f"**Accuracy:** "
                    f"{percentage:.0f}%"
                )


else:

    st.info(
        "No quiz attempts yet."
    )


# --------------------------------------------------
# STUDY SESSION HISTORY
# --------------------------------------------------

st.divider()

st.subheader(
    "⏱️ Study Session History"
)


connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    SELECT
        topic,
        duration_minutes,
        completed
    FROM study_sessions
    WHERE student_id = ?
    ORDER BY id DESC
    """,
    (student_id,)
)


sessions = cursor.fetchall()


connection.close()


if sessions:

    for session in sessions:

        topic = session[0]

        duration = session[1]

        completed = session[2]


        if completed == 1:

            status = "✅ Completed"

        else:

            status = "⏳ Incomplete"


        with st.container(
            border=True
        ):

            st.write(
                f"**{topic}** — "
                f"{duration} minutes — "
                f"{status}"
            )

else:

    st.info(
        "No study sessions recorded yet."
    )


# --------------------------------------------------
# ADAPTIVE RECOMMENDATION
# --------------------------------------------------

st.divider()

st.subheader(
    "🤖 STUBA's Adaptive Recommendation"
)


if average_score is None:

    st.info(
        "Start learning a topic and take a quiz. "
        "STUBA will analyze your performance."
    )


elif topic_results:

    weak_topics = [

        topic

        for topic, score, attempts
        in topic_results

        if score < 60
    ]


    average_topics = [

        topic

        for topic, score, attempts
        in topic_results

        if 60 <= score < 80
    ]


    strong_topics = [

        topic

        for topic, score, attempts
        in topic_results

        if score >= 80
    ]


    if weak_topics:

        st.warning(
            "🔴 STUBA recommends focusing on: "
            + ", ".join(weak_topics)
        )

        st.write(
            "These topics have accuracy below 60%. "
            "Review the lesson, use Focus Mode, "
            "and take another quiz."
        )


    elif average_topics:

        st.info(
            "🟡 STUBA recommends more practice on: "
            + ", ".join(average_topics)
        )

        st.write(
            "Your understanding is developing. "
            "Practice these topics before moving "
            "to more advanced concepts."
        )


    elif strong_topics:

        st.success(
            "🟢 Great work! Your tested topics "
            "are performing strongly."
        )

        st.write(
            "STUBA recommends moving toward "
            "harder questions and advanced topics."
        )


else:

    st.info(
        "Continue taking quizzes so STUBA can "
        "identify your strengths and weaknesses."
    )