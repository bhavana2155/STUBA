import streamlit as st
import time
from database import get_latest_student, get_connection


st.set_page_config(
    page_title="Focus Mode - STUBA",
    page_icon="🎯",
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


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.title("🎯 Focus Mode")

st.write(
    "Study one topic without distractions and let "
    "STUBA track your learning session."
)

st.divider()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "focus_running" not in st.session_state:

    st.session_state.focus_running = False


if "focus_completed" not in st.session_state:

    st.session_state.focus_completed = False


if "focus_start_time" not in st.session_state:

    st.session_state.focus_start_time = None


if "focus_duration" not in st.session_state:

    st.session_state.focus_duration = 25


if "focus_goal" not in st.session_state:

    st.session_state.focus_goal = ""


if "focus_saved" not in st.session_state:

    st.session_state.focus_saved = False


# --------------------------------------------------
# STUDY GOAL
# --------------------------------------------------

if not st.session_state.focus_running:

    st.subheader("📚 What are you going to study?")

    goal = st.text_input(
        "Study Topic",
        placeholder="Example: DBMS Normalization"
    )


    duration = st.selectbox(
        "⏱️ Focus Duration",
        [
            15,
            25,
            30,
            45,
            60,
            90
        ],
        index=1,
        format_func=lambda x: f"{x} minutes"
    )


    st.divider()


    # --------------------------------------------------
    # START SESSION
    # --------------------------------------------------

    if st.button(
        "🚀 Start Focus Session",
        type="primary"
    ):

        if not goal.strip():

            st.warning(
                "Please enter your study topic first."
            )

        else:

            st.session_state.focus_running = True

            st.session_state.focus_completed = False

            st.session_state.focus_saved = False

            st.session_state.focus_start_time = time.time()

            st.session_state.focus_duration = duration

            st.session_state.focus_goal = goal.strip()

            st.rerun()


# --------------------------------------------------
# RUNNING SESSION
# --------------------------------------------------

if st.session_state.focus_running:

    st.subheader(
        "🔥 Focus Session Running"
    )


    elapsed = (
        time.time()
        - st.session_state.focus_start_time
    )


    total_seconds = (
        st.session_state.focus_duration
        * 60
    )


    remaining = max(
        0,
        total_seconds - elapsed
    )


    # --------------------------------------------------
    # TIME DISPLAY
    # --------------------------------------------------

    minutes = int(
        remaining // 60
    )


    seconds = int(
        remaining % 60
    )


    st.markdown(
        f"""
        <div style="
            text-align:center;
            padding:35px;
            border-radius:20px;
            border:2px solid #ddd;
            margin:25px 0;
        ">

            <div style="
                font-size:70px;
                font-weight:bold;
            ">
                {minutes:02d}:{seconds:02d}
            </div>

            <div style="
                font-size:22px;
                margin-top:10px;
            ">
                🎯 {st.session_state.focus_goal}
            </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # --------------------------------------------------
    # PROGRESS BAR
    # --------------------------------------------------

    progress = min(
        elapsed / total_seconds,
        1.0
    )


    st.progress(
        progress
    )


    st.caption(
        f"Studying: "
        f"{st.session_state.focus_goal}"
    )


    # --------------------------------------------------
    # SESSION COMPLETE
    # --------------------------------------------------

    if remaining <= 0:

        st.session_state.focus_running = False

        st.session_state.focus_completed = True


        if not st.session_state.focus_saved:

            connection = get_connection()

            cursor = connection.cursor()


            cursor.execute(
                """
                INSERT INTO study_sessions
                (
                    student_id,
                    topic,
                    duration_minutes,
                    completed
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    student_id,
                    st.session_state.focus_goal,
                    st.session_state.focus_duration,
                    1
                )
            )


            connection.commit()

            connection.close()


            st.session_state.focus_saved = True


        st.success(
            "🎉 Focus session completed!"
        )

        st.balloons()


    else:

        # Refresh timer every second

        time.sleep(1)

        st.rerun()


# --------------------------------------------------
# FINISH SESSION EARLY
# --------------------------------------------------

if (
    st.session_state.focus_running
    and not st.session_state.focus_completed
):

    st.divider()


    if st.button(
        "✅ Finish Session Early"
    ):

        elapsed_minutes = int(
            (
                time.time()
                - st.session_state.focus_start_time
            ) / 60
        )


        # At least one minute is recorded
        actual_minutes = max(
            1,
            elapsed_minutes
        )


        connection = get_connection()

        cursor = connection.cursor()


        cursor.execute(
            """
            INSERT INTO study_sessions
            (
                student_id,
                topic,
                duration_minutes,
                completed
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                student_id,
                st.session_state.focus_goal,
                actual_minutes,
                1
            )
        )


        connection.commit()

        connection.close()


        st.session_state.focus_running = False

        st.session_state.focus_completed = True

        st.session_state.focus_saved = True


        st.success(
            f"✅ Session saved: "
            f"{actual_minutes} minute(s) studied."
        )


        st.rerun()


# --------------------------------------------------
# SESSION COMPLETED
# --------------------------------------------------

if st.session_state.focus_completed:

    st.divider()

    st.subheader(
        "🏆 Great Work!"
    )


    st.success(
        "Your study session has been recorded "
        "in STUBA Progress."
    )


    st.write(
        f"**Topic:** "
        f"{st.session_state.focus_goal}"
    )


    st.write(
        f"**Planned Duration:** "
        f"{st.session_state.focus_duration} minutes"
    )


    st.info(
        "💡 Now take a quiz in AI Tutor to check "
        "whether your understanding improved."
    )


    if st.button(
        "🔄 Start Another Session"
    ):

        st.session_state.focus_running = False

        st.session_state.focus_completed = False

        st.session_state.focus_start_time = None

        st.session_state.focus_goal = ""

        st.session_state.focus_saved = False

        st.rerun()


# --------------------------------------------------
# FOCUS TIPS
# --------------------------------------------------

if not st.session_state.focus_running:

    st.divider()

    st.subheader(
        "💡 Focus Tips"
    )


    st.write(
        "📱 Keep unnecessary tabs and notifications closed."
    )

    st.write(
        "🎯 Focus on one topic during each session."
    )

    st.write(
        "🧠 After studying, take a quiz in AI Tutor."
    )

    st.write(
        "📊 Check Progress to see whether your "
        "performance improves."
    )