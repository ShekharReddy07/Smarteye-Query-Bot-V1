# =================================================
# IMPORTS
# =================================================

import streamlit as st
import pandas as pd
import requests
from datetime import date

# =================================================
# BACKEND API CONFIGURATION
# =================================================

BACKEND_API_URL = "https://northbound-allie-silvery.ngrok-free.dev"


# =================================================
# PAGE CONFIGURATION
# =================================================

st.set_page_config(
    page_title="SmartEye Query Bot",
    page_icon="🤖",
    layout="wide"
)

# =================================================
# SESSION STATE INITIALIZATION
# =================================================

if "page" not in st.session_state:
    st.session_state.page = "chat"

# =================================================
# SIDEBAR – NAVIGATION & MILL SELECTION
# =================================================

with st.sidebar:
    st.header("Navigation")

    if st.button("💬 Smart Query Bot"):
        st.session_state.page = "chat"

    if st.button("📊 Show Month-wise Attendance"):
        st.session_state.page = "month_attendance"

    st.markdown("---")
    st.header("Mill Selection")

    mill = st.selectbox(
        "Select Mill",
        ["SHJM", "SGJM", "MIJM"],
        index=0
    )

# =================================================
# PAGE 1 — SMART QUERY BOT (LLM-BASED)
# =================================================

if st.session_state.page == "chat":

    st.title("🤖 SmartEye Query Bot")
    st.caption("AI-powered attendance query assistant (SQL-safe & auditable)")

    st.markdown("**Safe Examples:**")
    st.markdown("- How many outsiders today?")
    st.markdown("- Show attendance of nz1073 between 10/01/2025 to 31/12/2025")
    st.markdown("- How many double duty workers today?")
    st.markdown("- How many overtime workers today?")
    st.markdown("- Show overtime between 10/12/2025 to 31/12/2025")

    question = st.chat_input("Ask SmartEye related question...")

    if question:
        with st.spinner("Sending request to backend..."):
            response = requests.post(
                f"{BACKEND_API_URL}/query",
                json={
                    "question": question,
                    "mill": mill
                },
                timeout=60
            )

        # -------------------------------
        # HTTP-level error handling
        # -------------------------------
        if response.status_code != 200:
            st.error("Backend error occurred")
            st.code(response.text)
            st.stop()

        result = response.json()

        # -------------------------------
        # CASE 1: SQL EXECUTED
        # -------------------------------
        if result.get("status") == "executed":
            st.success("SQL executed successfully")

            with st.expander("Executed SQL (SSMS-ready)"):
                st.code(result["sql"], language="sql")

                if result.get("params"):
                    st.markdown("Parameters:")
                    st.code(result["params"])

                st.markdown(f"Rows returned: {result['rows']}")

            df = pd.DataFrame(result["data"])
            st.dataframe(df, use_container_width=True)

        # -------------------------------
        # CASE 2: SQL GENERATED BUT BLOCKED
        # -------------------------------
        elif result.get("status") == "generated":
            st.warning("SQL was generated but execution was blocked by safety rules.")

            with st.expander("Generated SQL (NOT executed)"):
                st.code(result["sql"], language="sql")

                if result.get("params"):
                    st.markdown("Parameters:")
                    st.code(result["params"])

        # -------------------------------
        # CASE 3: UNSUPPORTED QUERY
        # -------------------------------
        elif result.get("unsupported"):
            st.warning(result.get("message", "Query not supported"))

        else:
            st.warning("Unexpected response from backend")

# =================================================
# PAGE 2 — MONTH-WISE ATTENDANCE (NO LLM)
# =================================================

elif st.session_state.page == "month_attendance":

    st.title("Month-wise Attendance Report")
    st.caption("Guided analytics – backend-driven, no LLM")

    col1, col2 = st.columns(2)

    with col1:
        start_date = st.date_input(
            "From Date",
            value=date(2025, 1, 1)
        )

    with col2:
        end_date = st.date_input(
            "To Date",
            value=date(2025, 12, 31)
        )

    if start_date > end_date:
        st.error("Start date cannot be after end date")
        st.stop()

    # =================================================
    # FETCH EMPLOYEES
    # =================================================

    with st.spinner("Fetching employees..."):
        response = requests.post(
            f"{BACKEND_API_URL}/employees",
            json={
                "mill": mill,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            timeout=30
        )

    if response.status_code != 200:
        st.error("Backend error while fetching employees")
        st.code(response.text)
        st.stop()

    employees = response.json()

    if not employees:
        st.warning("No employees found for selected date range.")
        st.stop()

    employee_map = {
        f"{row['ECode']} - {row['EName']}": row["ECode"]
        for row in employees
    }

    selected_employee = st.selectbox(
        "Select Employee",
        options=list(employee_map.keys())
    )

    selected_ecode = employee_map[selected_employee]

    # =================================================
    # FETCH MONTH-WISE ATTENDANCE
    # =================================================

    if st.button("Show Month-wise Attendance"):
        with st.spinner("Calculating attendance..."):
            response = requests.post(
                f"{BACKEND_API_URL}/monthwise-attendance",
                json={
                    "mill": mill,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "ecode": selected_ecode
                },
                timeout=30
            )

        if response.status_code != 200:
            st.error("Backend error while fetching attendance")
            st.code(response.text)
            st.stop()

        data = response.json()

        if not data:
            st.warning("No attendance data found.")
            st.stop()

        df = pd.DataFrame(data)

        df["Month"] = df["mon"].apply(
            lambda x: date(1900, x, 1).strftime("%B")
        )

        df = df.rename(columns={
            "work_days": "Total Working Days",
            "attn_days": "Attendance Days"
        })

        st.success("Month-wise attendance calculated")

        st.dataframe(
            df[["Month", "Total Working Days", "Attendance Days"]],
            use_container_width=True
        )
