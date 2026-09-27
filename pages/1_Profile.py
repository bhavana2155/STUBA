import streamlit as st
from database import create_student, get_latest_student


st.set_page_config(
    page_title="My Profile - STUBA",
    page_icon="👤",
    layout="wide"
)


st.title("👤 My Profile")

st.write(
    "Tell STUBA about yourself so it can personalize "
    "your learning experience."
)

st.divider()


# --------------------------------------------------
# PERSONAL INFORMATION
# --------------------------------------------------

st.subheader("👩‍🎓 Personal Information")

name = st.text_input(
    "Full Name",
    placeholder="Enter your name"
)

college = st.text_input(
    "College / University",
    placeholder="Enter your college name"
)


# --------------------------------------------------
# ACADEMIC INFORMATION
# --------------------------------------------------

st.subheader("🎓 Academic Information")

col1, col2, col3 = st.columns(3)


with col1:

    degree = st.selectbox(
        "Degree",
        [
            "B.Tech",
            "B.E",
            "M.Tech",
            "MCA",
            "Other"
        ]
    )


with col2:

    branch = st.text_input(
        "Branch",
        placeholder="Example: Information Technology"
    )


with col3:

    year = st.selectbox(
        "Current Year",
        [
            "1st Year",
            "2nd Year",
            "3rd Year",
            "4th Year"
        ]
    )


semester = st.selectbox(
    "Current Semester",
    [
        "1st Semester",
        "2nd Semester",
        "3rd Semester",
        "4th Semester",
        "5th Semester",
        "6th Semester",
        "7th Semester",
        "8th Semester"
    ]
)


# --------------------------------------------------
# STUDY AVAILABILITY
# --------------------------------------------------

st.subheader("⏰ Study Availability")

daily_study_hours = st.slider(
    "How many hours can you study per day?",
    min_value=1,
    max_value=12,
    value=3
)


# --------------------------------------------------
# EXAM PREPARATION
# --------------------------------------------------

st.subheader("🎯 Exam Preparation")

competitive_exam = st.multiselect(
    "Which exams are you preparing for?",
    [
        "GATE",
        "Placement Tests",
        "Coding Assessments",
        "Competitive Exams",
        "None"
    ]
)


# --------------------------------------------------
# LEARNING PREFERENCE
# --------------------------------------------------

st.subheader("🧠 Learning Preference")

learning_style = st.selectbox(
    "How do you prefer to learn?",
    [
        "Simple Explanation",
        "Examples First",
        "Visual / Mind Maps",
        "Practice Questions",
        "Exam-Oriented"
    ]
)


st.divider()


# --------------------------------------------------
# SAVE PROFILE
# --------------------------------------------------

if st.button(
    "💾 Save My Profile",
    type="primary"
):

    if not name.strip():

        st.error(
            "Please enter your name."
        )

    elif not college.strip():

        st.error(
            "Please enter your college."
        )

    elif not branch.strip():

        st.error(
            "Please enter your branch."
        )

    else:

        # Convert selected exams into one database string

        if competitive_exam:

            exam_text = ", ".join(
                competitive_exam
            )

        else:

            exam_text = "None"


        # Save everything permanently

        student_id = create_student(
            name.strip(),
            college.strip(),
            degree,
            branch.strip(),
            year,
            semester,
            daily_study_hours,
            learning_style,
            exam_text
        )


        st.session_state[
            "student_id"
        ] = student_id


        st.success(
            "✅ Profile saved successfully!"
        )


        st.info(
            f"Your STUBA Student ID is: {student_id}"
        )


        st.write(
            f"**Learning Style:** "
            f"{learning_style}"
        )


        st.write(
            f"**Exam Preparation:** "
            f"{exam_text}"
        )


# --------------------------------------------------
# CURRENT SAVED PROFILE
# --------------------------------------------------

st.divider()

st.subheader("📋 Current Saved Profile")

student = get_latest_student()


if student:

    col1, col2 = st.columns(2)


    with col1:

        st.write(
            f"**Name:** {student[1]}"
        )

        st.write(
            f"**College:** {student[2]}"
        )

        st.write(
            f"**Degree:** {student[3]}"
        )

        st.write(
            f"**Branch:** {student[4]}"
        )

        st.write(
            f"**Learning Style:** "
            f"{student[8] or 'Not specified'}"
        )


    with col2:

        st.write(
            f"**Year:** {student[5]}"
        )

        st.write(
            f"**Semester:** {student[6]}"
        )

        st.write(
            f"**Daily Study Time:** "
            f"{student[7]} hours"
        )

        st.write(
            f"**Exam Preparation:** "
            f"{student[9] or 'None'}"
        )


else:

    st.info(
        "No profile saved yet."
    )