import streamlit as st
import sqlite3
from database import get_latest_student


st.set_page_config(
    page_title="STUBA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
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
# CUSTOM CSS
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        font-size: 18px;
        color: #666;
        margin-bottom: 25px;
    }

    .dashboard-card {
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #ddd;
        background-color: #ffffff;
        min-height: 150px;
    }

    .card-title {
        font-size: 20px;
        font-weight: 600;
    }

    .card-text {
        color: #666;
    }

    .footer {
        text-align: center;
        color: #888;
        margin-top: 50px;
        padding: 20px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown(
        "# 🎓 STUBA"
    )

    st.caption(
        "Your Personal AI Learning Companion"
    )

    st.divider()

    st.markdown("### 🧭 Navigation")

    st.markdown(
        """
        **🏠 Dashboard**

        👤 My Profile

        📚 My Subjects

        📅 Study Planner

        🤖 AI Tutor

        📝 Practice & Quiz

        📊 Progress

        🎯 Focus Mode
        """
    )

    st.divider()

    st.info(
        "💡 Use the pages above to build your "
        "personalized learning journey."
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------

student = get_latest_student()


if student:

    student_name = student[1]

    st.markdown(
        f"""
        <div class="main-title">
        Welcome back, {student_name}! 👋
        </div>
        """,
        unsafe_allow_html=True
    )

else:

    st.markdown(
        """
        <div class="main-title">
        Welcome to STUBA 👋
        </div>
        """,
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="subtitle">
    Your AI-powered academic companion that adapts
    your learning based on your performance.
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# GET LIVE STATISTICS
# --------------------------------------------------

if student:

    student_id = student[0]

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

    quiz_count = cursor.fetchone()[0]


    # Average accuracy
    cursor.execute(
        """
        SELECT AVG(percentage)
        FROM quiz_results
        WHERE student_id = ?
        """,
        (student_id,)
    )

    average_score = cursor.fetchone()[0]


    # Completed sessions
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM study_sessions
        WHERE student_id = ?
        AND completed = 1
        """,
        (student_id,)
    )

    study_sessions = cursor.fetchone()[0]


    connection.close()

else:

    subject_count = 0
    quiz_count = 0
    average_score = None
    study_sessions = 0


# --------------------------------------------------
# LIVE DASHBOARD METRICS
# --------------------------------------------------

st.subheader("📊 Your Learning Overview")

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "📚 Subjects",
        subject_count
    )


with col2:

    st.metric(
        "📝 Quiz Attempts",
        quiz_count
    )


with col3:

    if average_score is not None:

        st.metric(
            "🎯 Quiz Accuracy",
            f"{average_score:.0f}%"
        )

    else:

        st.metric(
            "🎯 Quiz Accuracy",
            "—"
        )


with col4:

    st.metric(
        "⏱️ Study Sessions",
        study_sessions
    )


# --------------------------------------------------
# MAIN FEATURES
# --------------------------------------------------

st.divider()

st.subheader("🚀 What STUBA Can Do")


col1, col2, col3 = st.columns(3)


with col1:

    st.markdown(
        """
        <div class="dashboard-card">

        <div class="card-title">
        🧠 Personalized Learning
        </div>

        <p class="card-text">
        STUBA creates a study plan based on
        your subjects, available time, exams,
        and learning performance.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


with col2:

    st.markdown(
        """
        <div class="dashboard-card">

        <div class="card-title">
        🤖 AI Tutor
        </div>

        <p class="card-text">
        Learn difficult concepts through
        beginner explanations, examples,
        exam preparation, and revision.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


with col3:

    st.markdown(
        """
        <div class="dashboard-card">

        <div class="card-title">
        📈 Adaptive Progress
        </div>

        <p class="card-text">
        STUBA analyzes quiz performance
        and identifies topics that need
        more practice.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# GET RECOMMENDATION
# --------------------------------------------------

st.divider()

st.subheader("🤖 STUBA Recommendation")


if not student:

    st.info(
        "👤 Start by creating your profile."
    )


elif subject_count == 0:

    st.info(
        "📚 Add your subjects and syllabus "
        "so STUBA can create your study plan."
    )


elif quiz_count == 0:

    st.info(
        "🧠 Study a topic using AI Tutor and "
        "take your first quiz. STUBA will then "
        "start adapting your learning plan."
    )


elif average_score < 60:

    st.warning(
        "📚 Your recent quiz performance shows "
        "that some topics may need more revision. "
        "Check the Study Planner for high-priority topics."
    )


elif average_score < 80:

    st.info(
        "👍 You're making progress. Keep practicing "
        "your weaker topics and take another quiz."
    )


else:

    st.success(
        "💪 Excellent progress! You can move toward "
        "more advanced topics and harder practice."
    )


# --------------------------------------------------
# LEARNING LOOP
# --------------------------------------------------

st.divider()

st.subheader("🔄 Your STUBA Learning Loop")

st.markdown(
    """
    **📚 Syllabus**
    ↓
    **📅 Personalized Plan**
    ↓
    **🤖 AI Tutor**
    ↓
    **📝 Practice Quiz**
    ↓
    **📊 Performance Analysis**
    ↓
    **🧠 Weak Topic Detection**
    ↓
    **📅 Adaptive Plan Update**
    ↓
    **🔄 Repeat**
    """
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    """
    <div class="footer">
    🎓 STUBA — Student Buddy<br>
    AI-powered personalized learning companion
    </div>
    """,
    unsafe_allow_html=True
)