import streamlit as st
import json

from ai_service import ask_gemini
from database import get_latest_student, get_connection


st.set_page_config(
    page_title="AI Tutor - STUBA",
    page_icon="🤖",
    layout="wide"
)


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
degree = student[3]
branch = student[4]
year = student[5]
semester = student[6]
daily_hours = student[7]
learning_style = student[8] or "Simple Explanation"
competitive_exam = student[9] or "None"


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🤖 AI Tutor")

st.write(
    "Learn difficult concepts with explanations "
    "adapted to your learning style and performance."
)

st.divider()


# --------------------------------------------------
# STUDENT CONTEXT
# --------------------------------------------------

with st.expander("👤 Your Learning Profile"):

    col1, col2, col3 = st.columns(3)

    with col1:

        st.write(
            f"**Student:** {student_name}"
        )

        st.write(
            f"**Degree:** {degree}"
        )

        st.write(
            f"**Branch:** {branch}"
        )

    with col2:

        st.write(
            f"**Year:** {year}"
        )

        st.write(
            f"**Semester:** {semester}"
        )

        st.write(
            f"**Daily Study Time:** "
            f"{daily_hours} hours"
        )

    with col3:

        st.write(
            f"**Learning Style:** "
            f"{learning_style}"
        )

        st.write(
            f"**Exam Preparation:** "
            f"{competitive_exam}"
        )


# --------------------------------------------------
# TOPIC INPUT
# --------------------------------------------------

st.subheader("📚 What do you want to learn?")


topic = st.text_input(
    "Enter a topic",
    placeholder="Example: DBMS Normalization"
)


col1, col2 = st.columns(2)


with col1:

    learning_mode = st.selectbox(
        "Learning Mode",
        [
            "Understand from Basics",
            "Exam Preparation",
            "Interview Preparation",
            "Quick Revision"
        ]
    )


with col2:

    difficulty = st.selectbox(
        "Difficulty",
        [
            "Beginner",
            "Intermediate",
            "Advanced"
        ]
    )


# --------------------------------------------------
# GET TOPIC PERFORMANCE
# --------------------------------------------------

topic_score = None


if topic.strip():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT AVG(percentage)
        FROM quiz_results
        WHERE student_id = ?
        AND LOWER(topic) = LOWER(?)
        """,
        (
            student_id,
            topic.strip()
        )
    )

    result = cursor.fetchone()

    connection.close()


    if result and result[0] is not None:

        topic_score = result[0]


# --------------------------------------------------
# ADAPTIVE STATUS
# --------------------------------------------------

if topic_score is None:

    adaptive_instruction = """
This topic has not been tested yet.

Start with a clear foundation.
Explain the topic step by step.
Use simple examples before advanced details.
"""

elif topic_score < 60:

    adaptive_instruction = f"""
The student previously scored only
{topic_score:.0f}% on this topic.

Treat this as a WEAK topic.

Re-teach the concept from the basics.
Use very simple explanations.
Identify common misconceptions.
Give extra examples.
Focus on the concepts most likely to
cause mistakes.
"""

elif topic_score < 80:

    adaptive_instruction = f"""
The student's previous accuracy is
{topic_score:.0f}%.

Treat this as an AVERAGE topic.

Give a clear explanation,
then provide examples and practice.
Focus especially on areas where
students commonly make mistakes.
"""

else:

    adaptive_instruction = f"""
The student's previous accuracy is
{topic_score:.0f}%.

Treat this as a STRONG topic.

Do not spend too much time on basic
definitions.

Move toward deeper understanding,
advanced examples, application,
and interview/exam-level questions.
"""


# --------------------------------------------------
# GENERATE LESSON
# --------------------------------------------------

if st.button(
    "✨ Teach Me",
    type="primary"
):

    if not topic.strip():

        st.error(
            "Please enter a topic first."
        )

        st.stop()


    tutor_prompt = f"""
You are STUBA, an AI academic tutor.

Student profile:

Name: {student_name}

Degree: {degree}

Branch: {branch}

Year: {year}

Semester: {semester}

Daily study time: {daily_hours} hours

Preferred learning style: {learning_style}

Exam preparation: {competitive_exam}


Learning request:

Topic: {topic}

Learning mode: {learning_mode}

Difficulty: {difficulty}


Adaptive learning information:

{adaptive_instruction}


Create a personalized lesson.

Follow this exact structure:

1. Simple Definition

2. Why This Topic Matters

3. Core Concepts

4. Easy Real-Life Example

5. Technical Example

6. Step-by-Step Explanation

7. Exam / Interview Points

8. Common Mistakes

9. Quick Revision

10. Three Practice Questions


Important rules:

- Match the student's preferred learning style.
- Use simple language.
- Do not assume advanced knowledge.
- If the topic is programming, include code examples.
- If the topic is mathematical, show the steps.
- If the topic is theoretical, use examples and comparisons.
- If the student is weak in the topic, slow down and reinforce fundamentals.
- If the student is strong, provide deeper application.
- Keep the explanation useful for a college student.
"""


    with st.spinner(
        "🧠 STUBA is personalizing your lesson..."
    ):

        try:

            lesson = ask_gemini(
                tutor_prompt
            )

            st.session_state[
                "ai_tutor_lesson"
            ] = lesson

            st.session_state[
                "ai_tutor_topic"
            ] = topic.strip()

        except Exception:

            st.error(
                "⚠️ STUBA could not generate "
                "the lesson right now."
            )

            st.info(
                "Please try again in a few seconds."
            )


# --------------------------------------------------
# SHOW ADAPTIVE STATUS
# --------------------------------------------------

if topic_score is not None:

    st.divider()

    st.subheader(
        "📊 STUBA's Understanding of This Topic"
    )


    col1, col2 = st.columns(2)


    with col1:

        st.metric(
            "Previous Quiz Accuracy",
            f"{topic_score:.0f}%"
        )


    with col2:

        if topic_score < 60:

            st.error(
                "🔴 Weak Topic"
            )

        elif topic_score < 80:

            st.warning(
                "🟡 Developing"
            )

        else:

            st.success(
                "🟢 Strong Topic"
            )


# --------------------------------------------------
# SHOW LESSON
# --------------------------------------------------

if "ai_tutor_lesson" in st.session_state:

    st.divider()

    st.subheader(
        "📖 Your Personalized Lesson"
    )

    st.markdown(
        st.session_state[
            "ai_tutor_lesson"
        ]
    )


# --------------------------------------------------
# QUIZ GENERATION
# --------------------------------------------------

if (
    "ai_tutor_lesson"
    in st.session_state
):

    st.divider()

    st.subheader(
        "📝 Check Your Understanding"
    )


    if st.button(
        "🎯 Generate Personalized Quiz"
    ):

        quiz_topic = st.session_state[
            "ai_tutor_topic"
        ]


        quiz_prompt = f"""
You are STUBA.

Create exactly 5 multiple-choice questions
for the following topic:

Topic: {quiz_topic}

Student learning style:
{learning_style}

Previous topic performance:
{
    "Not tested"
    if topic_score is None
    else f"{topic_score:.0f}%"
}

Create questions that test understanding.

Return ONLY valid JSON.

Format:

[
  {{
    "question": "Question",
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

- Exactly 5 questions.
- Exactly 4 options per question.
- answer must be 0, 1, 2, or 3.
- Do not duplicate questions.
"""


        with st.spinner(
            "🧠 Creating your personalized quiz..."
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


                quiz = json.loads(
                    response
                )


                if not isinstance(
                    quiz,
                    list
                ):

                    raise ValueError(
                        "Invalid quiz."
                    )


                if len(quiz) != 5:

                    raise ValueError(
                        "Quiz must contain 5 questions."
                    )


                for question in quiz:

                    if (
                        "question"
                        not in question
                        or "options"
                        not in question
                        or "answer"
                        not in question
                        or "explanation"
                        not in question
                    ):

                        raise ValueError(
                            "Invalid question format."
                        )


                    if len(
                        question["options"]
                    ) != 4:

                        raise ValueError(
                            "Each question needs "
                            "4 options."
                        )


                    if question["answer"] not in [
                        0,
                        1,
                        2,
                        3
                    ]:

                        raise ValueError(
                            "Invalid answer."
                        )


                st.session_state[
                    "ai_quiz"
                ] = quiz

                st.session_state[
                    "ai_quiz_submitted"
                ] = False


            except Exception:

                st.error(
                    "⚠️ Could not create the quiz."
                )


# --------------------------------------------------
# DISPLAY QUIZ
# --------------------------------------------------

if "ai_quiz" in st.session_state:

    st.divider()

    st.subheader(
        "📝 Personalized Quiz"
    )


    quiz = st.session_state[
        "ai_quiz"
    ]


    answers = []


    for index, question in enumerate(
        quiz
    ):

        st.markdown(
            f"### Question {index + 1}"
        )


        st.write(
            question["question"]
        )


        selected = st.radio(
            "Choose an answer:",
            question["options"],
            key=f"ai_answer_{index}"
        )


        answers.append(
            question["options"].index(
                selected
            )
        )


    if st.button(
        "📊 Submit Personalized Quiz",
        type="primary"
    ):

        score = 0


        for index, question in enumerate(
            quiz
        ):

            if (
                answers[index]
                == question["answer"]
            ):

                score += 1


        total = len(quiz)


        percentage = (
            score / total
        ) * 100


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
                    "ai_tutor_topic"
                ],
                score,
                total,
                percentage
            )
        )


        connection.commit()

        connection.close()


        st.session_state[
            "ai_quiz_submitted"
        ] = True


        # --------------------------------------------------
        # RESULT
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "🎯 Quiz Result"
        )


        col1, col2 = st.columns(2)


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


        if percentage >= 80:

            st.success(
                "🟢 Strong understanding! "
                "STUBA can increase the difficulty."
            )

        elif percentage >= 60:

            st.warning(
                "🟡 You're getting there. "
                "A little more practice will help."
            )

        else:

            st.error(
                "🔴 This topic needs more revision. "
                "STUBA recommends relearning the basics."
            )


        # --------------------------------------------------
        # ANSWER REVIEW
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "📖 Review Your Answers"
        )


        for index, question in enumerate(
            quiz
        ):

            correct_index = question[
                "answer"
            ]

            correct_answer = question[
                "options"
            ][correct_index]


            if (
                answers[index]
                == correct_index
            ):

                st.success(
                    f"Question {index + 1}: "
                    "Correct ✅"
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
        # ADAPTIVE NEXT STEP
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "🔄 What Should You Do Next?"
        )


        if percentage < 60:

            st.warning(
                "📚 STUBA recommends reviewing "
                "this topic again using AI Tutor "
                "and then practicing in Focus Mode."
            )

        elif percentage < 80:

            st.info(
                "🧠 STUBA recommends another "
                "short practice session before "
                "moving to an advanced topic."
            )

        else:

            st.success(
                "🚀 STUBA recommends moving to "
                "a harder topic or advanced questions."
            )