import streamlit as st
import json

from ai_service import ask_gemini
from database import get_latest_student, get_connection


st.set_page_config(
    page_title="Practice & Quiz - STUBA",
    page_icon="📝",
    layout="wide"
)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("📝 Practice & Quiz")

st.write(
    "Practice your actual syllabus with AI-generated "
    "questions and let STUBA track your performance."
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

branch = student[4]

year = student[5]


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
    ORDER BY subject_name
    """,
    (student_id,)
)


subjects = cursor.fetchall()


connection.close()


if not subjects:

    st.warning(
        "📚 You haven't added any subjects yet."
    )

    st.info(
        "Go to **My Subjects** and add your subjects "
        "and syllabus topics first."
    )

    st.stop()


# --------------------------------------------------
# SUBJECT SELECTION
# --------------------------------------------------

st.subheader("📚 Choose Your Practice Topic")


subject_names = [
    subject[1]
    for subject in subjects
]


selected_subject_name = st.selectbox(
    "Subject",
    subject_names
)


selected_subject = next(
    subject
    for subject in subjects
    if subject[1] == selected_subject_name
)


subject_difficulty = selected_subject[2]

subject_topics = selected_subject[3] or ""


topic_list = [

    topic.strip()

    for topic in subject_topics.split(",")

    if topic.strip()
]


if topic_list:

    selected_topic = st.selectbox(
        "Topic",
        topic_list
    )

else:

    selected_topic = selected_subject_name


# --------------------------------------------------
# QUIZ SETTINGS
# --------------------------------------------------

col1, col2 = st.columns(2)


with col1:

    difficulty = st.selectbox(
        "Question Difficulty",
        [
            "Basic",
            "Intermediate",
            "Advanced"
        ]
    )


with col2:

    question_count = st.selectbox(
        "Number of Questions",
        [
            5,
            10
        ]
    )


st.divider()


# --------------------------------------------------
# GENERATE QUIZ
# --------------------------------------------------

if st.button(
    "✨ Generate Quiz",
    type="primary"
):

    quiz_prompt = f"""
You are STUBA, an AI-powered academic tutor.

Student:

Branch: {branch}

Year: {year}

Subject: {selected_subject_name}

Topic: {selected_topic}

Question Difficulty: {difficulty}

Create exactly {question_count}
multiple-choice questions.

The questions must be relevant to the topic.

Return ONLY valid JSON.

Use exactly this structure:

[
    {{
        "question": "Question text",
        "options": [
            "Option A",
            "Option B",
            "Option C",
            "Option D"
        ],
        "answer": 0,
        "explanation": "Short explanation"
    }}
]

Rules:

- Exactly {question_count} questions.
- Exactly 4 options per question.
- Answer must be an integer from 0 to 3.
- Do not duplicate questions.
- Test understanding, not only memorization.
- Keep explanations concise.
"""


    with st.spinner(
        "🧠 STUBA is generating your quiz..."
    ):

        try:

            response = ask_gemini(
                quiz_prompt
            )


            response = (
                response
                .replace(
                    "```json",
                    ""
                )
                .replace(
                    "```",
                    ""
                )
                .strip()
            )


            quiz_data = json.loads(
                response
            )


            if not isinstance(
                quiz_data,
                list
            ):

                raise ValueError(
                    "Invalid quiz format."
                )


            if len(quiz_data) != question_count:

                raise ValueError(
                    "Incorrect number of questions."
                )


            # --------------------------------------------------
            # BASIC VALIDATION
            # --------------------------------------------------

            for question in quiz_data:

                if (
                    "question" not in question
                    or "options" not in question
                    or "answer" not in question
                    or "explanation" not in question
                ):

                    raise ValueError(
                        "Invalid question structure."
                    )


                if len(
                    question["options"]
                ) != 4:

                    raise ValueError(
                        "Each question needs 4 options."
                    )


                if question["answer"] not in [
                    0,
                    1,
                    2,
                    3
                ]:

                    raise ValueError(
                        "Invalid answer index."
                    )


            st.session_state[
                "practice_quiz"
            ] = quiz_data


            st.session_state[
                "practice_topic"
            ] = selected_topic


            st.session_state[
                "practice_submitted"
            ] = False


        except Exception:

            st.error(
                "⚠️ STUBA could not generate "
                "the quiz correctly."
            )

            st.caption(
                "Please click Generate Quiz again."
            )


# --------------------------------------------------
# DISPLAY QUIZ
# --------------------------------------------------

if "practice_quiz" in st.session_state:

    st.divider()

    st.subheader(
        "📝 Your Practice Quiz"
    )


    st.info(
        f"Topic: "
        f"{st.session_state['practice_topic']}"
    )


    quiz_data = st.session_state[
        "practice_quiz"
    ]


    user_answers = []


    for index, question in enumerate(
        quiz_data
    ):

        st.markdown(
            f"### Question {index + 1}"
        )


        st.write(
            question["question"]
        )


        selected_option = st.radio(
            "Select your answer:",
            question["options"],
            key=f"practice_question_{index}"
        )


        selected_index = (
            question["options"].index(
                selected_option
            )
        )


        user_answers.append(
            selected_index
        )


        st.divider()


    # --------------------------------------------------
    # SUBMIT
    # --------------------------------------------------

    if st.button(
        "📊 Submit Quiz",
        type="primary"
    ):

        score = 0


        for index, question in enumerate(
            quiz_data
        ):

            if (
                user_answers[index]
                == question["answer"]
            ):

                score += 1


        total = len(
            quiz_data
        )


        percentage = (
            score / total
        ) * 100


        # --------------------------------------------------
        # PERFORMANCE STATUS
        # --------------------------------------------------

        if percentage >= 80:

            status = "Strong 💪"

        elif percentage >= 60:

            status = "Average 👍"

        else:

            status = (
                "Needs Improvement 📚"
            )


        # --------------------------------------------------
        # SAVE RESULT
        # --------------------------------------------------

        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO quiz_results
            (
                student_id,
                topic,
                score,
                total_questions,
                percentage
            )

            VALUES (?, ?, ?, ?, ?)
            """,
            (
                student_id,
                st.session_state[
                    "practice_topic"
                ],
                score,
                total,
                percentage
            )
        )


        connection.commit()

        connection.close()


        st.session_state[
            "practice_submitted"
        ] = True


        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "🎯 Your Result"
        )


        col1, col2, col3 = st.columns(3)


        with col1:

            st.metric(
                "Score",
                f"{score}/{total}"
            )


        with col2:

            st.metric(
                "Accuracy",
                f"{percentage:.0f}%"
            )


        with col3:

            st.metric(
                "Level",
                status
            )


        if percentage >= 80:

            st.success(
                "🎉 Excellent! You have a strong "
                "understanding of this topic."
            )

        elif percentage >= 60:

            st.warning(
                "👍 Good start. Review the questions "
                "you missed and practice again."
            )

        else:

            st.error(
                "📚 This topic needs more practice. "
                "Review the concept before retrying."
            )


        # --------------------------------------------------
        # ANSWER REVIEW
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "📖 Answer Review"
        )


        for index, question in enumerate(
            quiz_data
        ):

            correct_index = question[
                "answer"
            ]


            correct_answer = question[
                "options"
            ][
                correct_index
            ]


            if (
                user_answers[index]
                == correct_index
            ):

                st.success(
                    f"Question {index + 1}: "
                    f"Correct ✅"
                )

            else:

                st.error(
                    f"Question {index + 1}: "
                    f"Correct answer → "
                    f"{correct_answer}"
                )


            st.caption(
                question["explanation"]
            )


        # --------------------------------------------------
        # NEXT ACTION
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "🤖 STUBA Recommendation"
        )


        if percentage < 60:

            st.warning(
                "Go to AI Tutor and relearn this topic, "
                "then use Focus Mode before taking another quiz."
            )

        elif percentage < 80:

            st.info(
                "Your foundation is developing. "
                "Review the incorrect questions and "
                "practice again."
            )

        else:

            st.success(
                "You are ready to move forward. "
                "Try an advanced quiz or continue "
                "to the next topic."
            )