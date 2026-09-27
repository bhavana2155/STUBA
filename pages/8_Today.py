import streamlit as st
from datetime import date

from database import get_latest_student, get_connection


st.set_page_config(
    page_title="Today's Plan - STUBA",
    page_icon="📅",
    layout="wide"
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📅 Today's Study Plan")

st.write(
    "Your daily study checklist based on your "
    "subjects, available time, and learning progress."
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
daily_hours = student[7]


# --------------------------------------------------
# TODAY
# --------------------------------------------------

today = date.today().isoformat()

st.subheader(
    f"👋 Hi {student_name}!"
)

st.write(
    f"Here is your study workspace for "
    f"**{date.today().strftime('%d %B %Y')}**."
)

st.info(
    f"⏰ Your available study time: "
    f"**{daily_hours} hour(s) per day**"
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
    ORDER BY AVG(percentage) ASC
    """,
    (student_id,)
)

quiz_results = cursor.fetchall()

connection.close()


# --------------------------------------------------
# NO SUBJECTS
# --------------------------------------------------

if not subjects:

    st.warning(
        "📚 Your study plan is empty."
    )

    st.info(
        "Go to **My Subjects** and add your "
        "subjects and syllabus topics first."
    )

    st.stop()


# --------------------------------------------------
# CREATE TOPIC PRIORITY LIST
# --------------------------------------------------

topic_data = []


for subject in subjects:

    subject_name = subject[1]
    difficulty = subject[2]
    topics_text = subject[3] or ""

    topics = [
        topic.strip()
        for topic in topics_text.split(",")
        if topic.strip()
    ]

    for topic in topics:

        score = None

        for quiz_topic, quiz_score in quiz_results:

            if (
                quiz_topic
                and quiz_topic.lower().strip()
                == topic.lower().strip()
            ):

                score = quiz_score
                break


        # ----------------------------------------------
        # DETERMINE PRIORITY
        # ----------------------------------------------

        if score is None:

            priority = "High"
            priority_value = 3

        elif score < 60:

            priority = "High"
            priority_value = 3

        elif score < 80:

            priority = "Medium"
            priority_value = 2

        else:

            priority = "Low"
            priority_value = 1


        # ----------------------------------------------
        # ESTIMATE TIME
        # ----------------------------------------------

        if priority == "High":

            minutes = 30

        elif priority == "Medium":

            minutes = 25

        else:

            minutes = 20


        topic_data.append(
            {
                "subject": subject_name,
                "topic": topic,
                "difficulty": difficulty,
                "score": score,
                "priority": priority,
                "priority_value": priority_value,
                "minutes": minutes
            }
        )


# --------------------------------------------------
# SORT BY PRIORITY
# --------------------------------------------------

topic_data.sort(
    key=lambda item: item["priority_value"],
    reverse=True
)


# --------------------------------------------------
# LIMIT TO DAILY TIME
# --------------------------------------------------

available_minutes = daily_hours * 60

today_plan = []

used_minutes = 0


for item in topic_data:

    if used_minutes + item["minutes"] <= available_minutes:

        today_plan.append(item)

        used_minutes += item["minutes"]


# --------------------------------------------------
# IF NOTHING FITS
# --------------------------------------------------

if not today_plan and topic_data:

    today_plan.append(
        topic_data[0]
    )

    used_minutes = topic_data[0]["minutes"]


# --------------------------------------------------
# OVERVIEW
# --------------------------------------------------

st.divider()

st.subheader(
    "📊 Today's Overview"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "📚 Topics",
        len(today_plan)
    )


with col2:

    st.metric(
        "⏱️ Planned Time",
        f"{used_minutes} min"
    )


with col3:

    remaining = max(
        0,
        available_minutes - used_minutes
    )

    st.metric(
        "⌛ Free Time",
        f"{remaining} min"
    )


with col4:

    high_priority = sum(
        1
        for item in today_plan
        if item["priority"] == "High"
    )

    st.metric(
        "🔥 High Priority",
        high_priority
    )


# --------------------------------------------------
# PROGRESS TRACKING
# --------------------------------------------------

if "today_completed" not in st.session_state:

    st.session_state.today_completed = set()


completed_count = len(
    st.session_state.today_completed
)


if today_plan:

    progress = (
        completed_count
        / len(today_plan)
    )

else:

    progress = 0


st.divider()

st.subheader(
    "🎯 Today's Progress"
)

st.progress(
    min(progress, 1.0)
)

st.caption(
    f"{completed_count} of "
    f"{len(today_plan)} study tasks completed"
)


# --------------------------------------------------
# STUDY TASKS
# --------------------------------------------------

st.divider()

st.subheader(
    "📚 Your Study Checklist"
)


for index, item in enumerate(
    today_plan
):

    task_key = (
        f"{today}_{index}_"
        f"{item['subject']}_"
        f"{item['topic']}"
    )


    is_completed = (
        task_key
        in st.session_state.today_completed
    )


    with st.container(
        border=True
    ):

        col1, col2, col3 = st.columns(
            [0.1, 0.65, 0.25]
        )


        with col1:

            checked = st.checkbox(
                "Done",
                value=is_completed,
                key=f"check_{task_key}"
            )


        with col2:

            st.markdown(
                f"### 📘 {item['topic']}"
            )

            st.write(
                f"**Subject:** "
                f"{item['subject']}"
            )

            st.write(
                f"**Difficulty:** "
                f"{item['difficulty']}"
            )

            if item["score"] is None:

                st.caption(
                    "🧠 Not tested yet"
                )

            else:

                st.caption(
                    f"🎯 Current accuracy: "
                    f"{item['score']:.0f}%"
                )


        with col3:

            st.write(
                f"⏱️ **{item['minutes']} min**"
            )


            if item["priority"] == "High":

                st.error(
                    "🔥 High Priority"
                )

            elif item["priority"] == "Medium":

                st.warning(
                    "🟡 Medium Priority"
                )

            else:

                st.success(
                    "🟢 Low Priority"
                )


        if checked:

            st.session_state.today_completed.add(
                task_key
            )

        else:

            st.session_state.today_completed.discard(
                task_key
            )


# --------------------------------------------------
# REMINDER
# --------------------------------------------------

st.divider()

st.subheader(
    "🔔 Study Reminder"
)


reminder_time = st.time_input(
    "Choose your preferred study reminder time"
)


st.write(
    f"⏰ Reminder preference: "
    f"**{reminder_time.strftime('%I:%M %p')}**"
)


st.info(
    "💡 STUBA currently shows your reminder "
    "inside the app. Browser/phone push notifications "
    "can be added later using a notification service."
)


# --------------------------------------------------
# RECOMMENDATION
# --------------------------------------------------

st.divider()

st.subheader(
    "🤖 STUBA's Recommendation"
)


if not topic_data:

    st.info(
        "Add syllabus topics to start your personalized plan."
    )

elif high_priority > 0:

    high_topics = [
        item["topic"]
        for item in today_plan
        if item["priority"] == "High"
    ]

    st.warning(
        "🔥 Start with these high-priority topics: "
        + ", ".join(high_topics)
    )

    st.write(
        "STUBA prioritizes topics that are either "
        "not tested yet or have lower quiz performance."
    )

else:

    st.success(
        "🎉 Your tested topics are performing well. "
        "Use today's plan for revision and advanced practice."
    )


# --------------------------------------------------
# COMPLETION MESSAGE
# --------------------------------------------------

if (
    today_plan
    and completed_count == len(today_plan)
):

    st.divider()

    st.success(
        "🏆 Amazing! You completed today's "
        "study checklist."
    )

    st.balloons()