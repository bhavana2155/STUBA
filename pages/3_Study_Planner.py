import streamlit as st
import sqlite3
from datetime import date, timedelta
from database import get_latest_student


st.set_page_config(
    page_title="Study Planner - STUBA",
    page_icon="📅",
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

st.title("📅 Study Planner")

st.write(
    "STUBA creates a personalized and adaptive study "
    "plan using your syllabus, available time, "
    "exam date, difficulty, and quiz performance."
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

student_daily_hours = student[7] or 3

learning_style = student[8] or "Simple Explanation"

competitive_exam = student[9] or "None"


# --------------------------------------------------
# STUDENT PREFERENCES
# --------------------------------------------------

st.subheader("👤 Your Learning Preferences")

col1, col2, col3 = st.columns(3)


with col1:

    st.metric(
        "⏰ Daily Study Time",
        f"{student_daily_hours} hrs"
    )


with col2:

    st.metric(
        "🧠 Learning Style",
        learning_style
    )


with col3:

    st.metric(
        "🎯 Exam Goal",
        competitive_exam
    )


st.divider()


# --------------------------------------------------
# EXAM DETAILS
# --------------------------------------------------

st.subheader("🎯 Exam Details")

col1, col2 = st.columns(2)


with col1:

    exam_name = st.text_input(
        "Exam Name",
        placeholder="Example: Semester Exams"
    )


with col2:

    exam_date = st.date_input(
        "Exam Date",
        min_value=date.today()
    )


days_remaining = (
    exam_date - date.today()
).days


if days_remaining == 0:

    st.error(
        "🚨 Your exam is today!"
    )

elif days_remaining <= 7:

    st.warning(
        f"⏰ Only {days_remaining} days remaining!"
    )

elif days_remaining <= 30:

    st.warning(
        f"📅 {days_remaining} days remaining."
    )

else:

    st.success(
        f"📅 {days_remaining} days remaining."
    )


# --------------------------------------------------
# STUDY TIME
# --------------------------------------------------

st.subheader("⏰ Available Study Time")

daily_hours = st.number_input(
    "Hours available for studying per day",
    min_value=1,
    max_value=12,
    value=int(student_daily_hours),
    step=1
)


# --------------------------------------------------
# LOAD SUBJECTS
# --------------------------------------------------

connection = get_connection()

cursor = connection.cursor()


cursor.execute(
    """
    SELECT
        id,
        subject_name,
        exam_type,
        difficulty,
        topics
    FROM subjects
    WHERE student_id = ?
    ORDER BY id DESC
    """,
    (student_id,)
)

subjects = cursor.fetchall()


# --------------------------------------------------
# LOAD QUIZ PERFORMANCE
# --------------------------------------------------

cursor.execute(
    """
    SELECT
        topic,
        AVG(percentage)
    FROM quiz_results
    WHERE student_id = ?
    GROUP BY topic
    """
)

quiz_performance = cursor.fetchall()


connection.close()


# --------------------------------------------------
# CREATE PERFORMANCE DICTIONARY
# --------------------------------------------------

performance = {}


for topic, score in quiz_performance:

    if topic:

        performance[
            topic.lower().strip()
        ] = score


# --------------------------------------------------
# CHECK SUBJECTS
# --------------------------------------------------

if not subjects:

    st.warning(
        "📚 You haven't added any subjects yet."
    )

    st.info(
        "Go to **My Subjects** and add your subjects "
        "before creating a study plan."
    )

    st.stop()


# --------------------------------------------------
# SELECT SUBJECTS
# --------------------------------------------------

st.divider()

st.subheader("📚 Select Subjects")

selected_subjects = []


for subject in subjects:

    subject_id = subject[0]

    subject_name = subject[1]

    difficulty = subject[3]


    selected = st.checkbox(
        f"{subject_name} — {difficulty}",
        key=f"planner_subject_{subject_id}"
    )


    if selected:

        selected_subjects.append(
            subject
        )


# --------------------------------------------------
# GENERATE PLAN
# --------------------------------------------------

st.divider()


if st.button(
    "✨ Generate Adaptive Study Plan",
    type="primary"
):

    if not exam_name.strip():

        st.warning(
            "Please enter your exam name."
        )

    elif not selected_subjects:

        st.warning(
            "Please select at least one subject."
        )

    else:

        difficulty_weights = {

            "Easy": 1,

            "Medium": 2,

            "Hard": 3
        }


        plan_data = []


        # --------------------------------------------------
        # ANALYZE EACH SUBJECT
        # --------------------------------------------------

        for subject in selected_subjects:

            subject_name = subject[1]

            difficulty = subject[3]

            topics = subject[4] or ""


            topic_list = [

                topic.strip()

                for topic in topics.split(",")

                if topic.strip()
            ]


            if not topic_list:

                topic_list = [
                    subject_name
                ]


            # --------------------------------------------------
            # FIND TOPIC PERFORMANCE
            # --------------------------------------------------

            weak_topics = []

            moderate_topics = []

            strong_topics = []


            for topic in topic_list:

                score = performance.get(
                    topic.lower().strip()
                )


                if score is None:

                    continue


                if score < 60:

                    weak_topics.append(
                        (topic, score)
                    )

                elif score < 80:

                    moderate_topics.append(
                        (topic, score)
                    )

                else:

                    strong_topics.append(
                        (topic, score)
                    )


            # --------------------------------------------------
            # PRIORITY DECISION
            # --------------------------------------------------

            if weak_topics:

                priority = "High 🔴"


                recommended_topic = min(
                    weak_topics,
                    key=lambda item: item[1]
                )[0]


                weakest_score = min(
                    weak_topics,
                    key=lambda item: item[1]
                )[1]


                reason = (
                    f"Quiz score is only "
                    f"{weakest_score:.0f}%. "
                    f"Revision is recommended."
                )


                base_weight = 5


            elif moderate_topics:

                priority = "Medium 🟡"


                recommended_topic = moderate_topics[0][0]


                score = moderate_topics[0][1]


                reason = (
                    f"Quiz performance is "
                    f"{score:.0f}%. "
                    f"More practice can improve mastery."
                )


                base_weight = 3


            elif strong_topics:

                priority = "Normal 🟢"


                recommended_topic = strong_topics[0][0]


                reason = (
                    "Good quiz performance. "
                    "Continue practicing or move to harder concepts."
                )


                base_weight = difficulty_weights.get(
                    difficulty,
                    1
                )


            else:

                priority = "Normal 🟢"


                recommended_topic = topic_list[0]


                reason = (
                    "This topic has not been tested yet."
                )


                base_weight = difficulty_weights.get(
                    difficulty,
                    1
                )


            # --------------------------------------------------
            # LEARNING METHOD
            # --------------------------------------------------

            if learning_style == "Simple Explanation":

                method = (
                    "Start with a simple explanation "
                    "and an everyday example."
                )


            elif learning_style == "Examples First":

                method = (
                    "Start with examples, then learn "
                    "the underlying concept."
                )


            elif learning_style == "Visual / Mind Maps":

                method = (
                    "Create a mind map and connect "
                    "the important concepts."
                )


            elif learning_style == "Practice Questions":

                method = (
                    "Learn the basics and immediately "
                    "practice questions."
                )


            else:

                method = (
                    "Focus on definitions, key points, "
                    "and frequently tested concepts."
                )


            # --------------------------------------------------
            # EXAM-AWARE METHOD
            # --------------------------------------------------

            if days_remaining <= 7:

                exam_strategy = (
                    "Prioritize revision, active recall, "
                    "and timed practice."
                )

            elif days_remaining <= 30:

                exam_strategy = (
                    "Balance concept learning with "
                    "regular practice."
                )

            else:

                exam_strategy = (
                    "Build strong fundamentals before "
                    "moving to advanced topics."
                )


            plan_data.append(
                {
                    "subject": subject_name,

                    "difficulty": difficulty,

                    "topic": recommended_topic,

                    "priority": priority,

                    "reason": reason,

                    "method": method,

                    "exam_strategy": exam_strategy,

                    "weight": base_weight
                }
            )


        # --------------------------------------------------
        # ALLOCATE TIME
        # --------------------------------------------------

        total_weight = sum(
            item["weight"]
            for item in plan_data
        )


        total_minutes = (
            daily_hours * 60
        )


        for item in plan_data:

            allocated_minutes = round(

                total_minutes

                * item["weight"]

                / total_weight
            )


            item["minutes"] = max(
                15,
                allocated_minutes
            )


        # --------------------------------------------------
        # SAVE PLAN
        # --------------------------------------------------

        st.session_state[
            "adaptive_plan"
        ] = plan_data


        st.session_state[
            "planner_exam_name"
        ] = exam_name


# --------------------------------------------------
# DISPLAY PLAN
# --------------------------------------------------

if "adaptive_plan" in st.session_state:

    st.divider()

    st.subheader(
        "🧠 STUBA's Adaptive Study Plan"
    )


    st.success(
        f"Plan created for: "
        f"**{st.session_state['planner_exam_name']}**"
    )


    st.write(
        "STUBA analyzed your learning preference, "
        "available study time, exam deadline, "
        "subject difficulty, and quiz performance."
    )


    # --------------------------------------------------
    # PLAN CARDS
    # --------------------------------------------------

    for index, item in enumerate(
        st.session_state["adaptive_plan"]
    ):

        with st.container(
            border=True
        ):

            st.markdown(
                f"### {index + 1}. 📘 "
                f"{item['subject']}"
            )


            col1, col2 = st.columns(2)


            with col1:

                st.write(
                    f"**Recommended Topic:** "
                    f"{item['topic']}"
                )

                st.write(
                    f"**Difficulty:** "
                    f"{item['difficulty']}"
                )

                st.write(
                    f"**Priority:** "
                    f"{item['priority']}"
                )


            with col2:

                st.write(
                    f"**Study Time:** "
                    f"{item['minutes']} minutes"
                )

                st.write(
                    f"**Learning Method:** "
                    f"{item['method']}"
                )


            st.caption(
                f"🤖 Why: {item['reason']}"
            )


            st.caption(
                f"🎯 Exam Strategy: "
                f"{item['exam_strategy']}"
            )


    # --------------------------------------------------
    # SUMMARY
    # --------------------------------------------------

    total_planned = sum(
        item["minutes"]
        for item in st.session_state[
            "adaptive_plan"
        ]
    )


    high_priority = [

        item

        for item in st.session_state[
            "adaptive_plan"
        ]

        if "High" in item["priority"]
    ]


    st.divider()

    col1, col2, col3, col4 = st.columns(4)


    with col1:

        st.metric(
            "📚 Subjects",
            len(
                st.session_state[
                    "adaptive_plan"
                ]
            )
        )


    with col2:

        st.metric(
            "⏱️ Planned Time",
            f"{total_planned} min"
        )


    with col3:

        st.metric(
            "📅 Days Remaining",
            days_remaining
        )


    with col4:

        st.metric(
            "🔴 High Priority",
            len(high_priority)
        )


    # --------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "🤖 STUBA Recommendation"
    )


    if high_priority:

        st.warning(
            "STUBA detected weak areas. "
            "Start with the high-priority topics, "
            "then take another quiz to measure improvement."
        )

    else:

        st.success(
            "No major weak areas were detected. "
            "Continue learning and use quizzes "
            "to maintain your progress."
        )