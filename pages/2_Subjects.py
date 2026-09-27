import streamlit as st
import sqlite3
from database import get_latest_student


st.set_page_config(
    page_title="My Subjects - STUBA",
    page_icon="📚",
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

st.title("📚 My Subjects")

st.write(
    "Add your subjects and syllabus topics. "
    "STUBA uses them to personalize your learning plan."
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


# --------------------------------------------------
# ADD SUBJECT
# --------------------------------------------------

st.subheader("➕ Add a Subject")


subject_name = st.text_input(
    "Subject Name",
    placeholder="Example: Database Management Systems"
)


exam_type = st.selectbox(
    "Exam Type",
    [
        "Semester Exam",
        "Midterm",
        "Competitive Exam",
        "Placement Preparation",
        "Other"
    ]
)


difficulty = st.select_slider(
    "Difficulty Level",
    options=[
        "Easy",
        "Medium",
        "Hard"
    ],
    value="Medium"
)


topics = st.text_area(
    "Syllabus Topics",
    placeholder=(
        "Enter topics separated by commas\n\n"
        "Example:\n"
        "ER Model, Relational Model, "
        "Normalization, SQL, Transactions"
    )
)


if st.button(
    "➕ Add Subject",
    type="primary"
):

    if not subject_name.strip():

        st.error(
            "Please enter the subject name."
        )

    elif not topics.strip():

        st.error(
            "Please enter at least one syllabus topic."
        )

    else:

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO subjects
            (
                student_id,
                subject_name,
                exam_type,
                difficulty,
                topics
            )

            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_id,
                subject_name.strip(),
                exam_type,
                difficulty,
                topics.strip()
            )
        )


        connection.commit()

        connection.close()


        st.success(
            f"✅ {subject_name} added successfully!"
        )

        st.rerun()


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


quiz_results = cursor.fetchall()


connection.close()


# --------------------------------------------------
# PERFORMANCE DICTIONARY
# --------------------------------------------------

performance = {}


for topic, score in quiz_results:

    if topic:

        performance[
            topic.lower().strip()
        ] = score


# --------------------------------------------------
# SUBJECT LIST
# --------------------------------------------------

st.divider()

st.subheader("📖 Your Subjects")


if not subjects:

    st.info(
        "No subjects added yet. "
        "Add your first subject above."
    )

else:

    for subject in subjects:

        subject_id = subject[0]

        name = subject[1]

        exam = subject[2]

        difficulty = subject[3]

        topic_text = subject[4] or ""


        topic_list = [

            topic.strip()

            for topic in topic_text.split(",")

            if topic.strip()
        ]


        # --------------------------------------------------
        # CALCULATE SUBJECT PERFORMANCE
        # --------------------------------------------------

        tested_scores = []


        for topic in topic_list:

            score = performance.get(
                topic.lower().strip()
            )


            if score is not None:

                tested_scores.append(
                    score
                )


        if tested_scores:

            subject_average = (
                sum(tested_scores)
                / len(tested_scores)
            )

        else:

            subject_average = None


        # --------------------------------------------------
        # SUBJECT CARD
        # --------------------------------------------------

        with st.container(
            border=True
        ):

            st.markdown(
                f"## 📘 {name}"
            )


            col1, col2, col3 = st.columns(3)


            with col1:

                st.write(
                    f"**Exam:** {exam}"
                )


            with col2:

                st.write(
                    f"**Difficulty:** "
                    f"{difficulty}"
                )


            with col3:

                st.write(
                    f"**Topics:** "
                    f"{len(topic_list)}"
                )


            # --------------------------------------------------
            # SUBJECT PERFORMANCE
            # --------------------------------------------------

            if subject_average is None:

                st.info(
                    "🧠 No quiz performance yet."
                )

            else:

                st.write(
                    f"**Subject Accuracy:** "
                    f"{subject_average:.0f}%"
                )


                st.progress(
                    min(
                        subject_average / 100,
                        1.0
                    )
                )


                if subject_average >= 80:

                    st.success(
                        "🟢 Strong"
                    )

                elif subject_average >= 60:

                    st.warning(
                        "🟡 Average"
                    )

                else:

                    st.error(
                        "🔴 Needs Improvement"
                    )


            # --------------------------------------------------
            # SYLLABUS
            # --------------------------------------------------

            st.write(
                "**📚 Syllabus Topics:**"
            )


            if topic_list:

                for topic in topic_list:

                    score = performance.get(
                        topic.lower().strip()
                    )


                    if score is None:

                        status = (
                            "⚪ Not Tested"
                        )

                    elif score >= 80:

                        status = (
                            f"🟢 Strong "
                            f"({score:.0f}%)"
                        )

                    elif score >= 60:

                        status = (
                            f"🟡 Average "
                            f"({score:.0f}%)"
                        )

                    else:

                        status = (
                            f"🔴 Weak "
                            f"({score:.0f}%)"
                        )


                    st.write(
                        f"• **{topic}** — {status}"
                    )


            else:

                st.info(
                    "No syllabus topics added."
                )


            # --------------------------------------------------
            # DELETE
            # --------------------------------------------------

            if st.button(
                "🗑️ Delete Subject",
                key=f"delete_subject_{subject_id}"
            ):

                connection = get_connection()

                cursor = connection.cursor()


                cursor.execute(
                    """
                    DELETE FROM subjects

                    WHERE id = ?

                    AND student_id = ?
                    """,
                    (
                        subject_id,
                        student_id
                    )
                )


                connection.commit()

                connection.close()


                st.success(
                    "Subject deleted successfully."
                )

                st.rerun()


# --------------------------------------------------
# STUBA TIP
# --------------------------------------------------

st.divider()

st.subheader(
    "🤖 STUBA Tip"
)


if not subjects:

    st.info(
        "Add your subjects and syllabus first. "
        "Then STUBA can build your personalized plan."
    )

elif not quiz_results:

    st.info(
        "Take an AI Tutor quiz after studying. "
        "Your topic performance will appear here."
    )

else:

    weak_topics = [

        topic

        for topic, score in quiz_results

        if score < 60
    ]


    if weak_topics:

        st.warning(
            "STUBA detected topics that may need "
            "more attention: "
            + ", ".join(weak_topics)
        )

    else:

        st.success(
            "🎉 No major weak topics detected yet. "
            "Keep practicing to maintain your progress."
        )