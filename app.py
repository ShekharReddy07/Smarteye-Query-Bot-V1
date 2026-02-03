# =================================================
# IMPORTS
# =================================================

import streamlit as st              # Streamlit UI framework
import pandas as pd                # Data handling (DataFrame)
from datetime import date           # Date selection & formatting

# Core application logic
from core.query_runner import handle_question

# Database helper functions
from core.db import (
    test_db_connection,
    get_employees_by_date_range,
    get_monthwise_attendance
)

# =================================================
# PAGE CONFIGURATION
# =================================================
# Sets browser tab title, icon, and layout
st.set_page_config(
    page_title="SmartEye Query Bot",
    page_icon="🤖",
    layout="wide"
)

# =================================================
# SESSION STATE INITIALIZATION
# =================================================
# Used to manage multi-page navigation
# Default page is "chat"
if "page" not in st.session_state:
    st.session_state.page = "chat"

# =================================================
# DATABASE CONNECTIVITY CHECK
# =================================================
# Ensures database is reachable before loading UI
try:
    test_db_connection("hastings")
    st.success("✅ Database connected successfully")
except Exception as e:
    # Stop app immediately if DB is down
    st.error("❌ Database connection failed")
    st.code(str(e))
    st.stop()

# =================================================
# SIDEBAR – NAVIGATION & MILL SELECTION
# =================================================
with st.sidebar:
    st.header("Navigation")

    # Switch to Smart Query Bot page
    if st.button("💬 Smart Query Bot"):
        st.session_state.page = "chat"

    # Switch to Month-wise Attendance page
    if st.button("📊 Show Month-wise Attendance"):
        st.session_state.page = "month_attendance"

    st.markdown("---")
    st.header("Mill Selection")

    # Mill selection dropdown
    mill = st.selectbox(
        "Select Mill",
        ["hastings", "gondalpara", "india"],
        index=0
    )

# =================================================
# PAGE 1 — SMART QUERY BOT (LLM-BASED)
# =================================================
if st.session_state.page == "chat":

    st.title("🤖 SmartEye Query Bot")
    st.caption("AI-powered attendance query assistant (SQL-safe & auditable)")

    # Help users understand safe queries
    st.markdown("**Safe Examples:**")
    st.markdown("- How many outsiders today?")
    st.markdown("- Show attendance of nz1073")
    st.markdown("- How many double duty workers today?")
    st.markdown("- How many overtime workers today?")
    st.markdown("- Show overtime in spinning department")

    # Chat-style input box
    question = st.chat_input("Ask SmartEye related question...")

    # -------------------------------------------------
    # Process user question
    # -------------------------------------------------
    if question:
        with st.spinner("Understanding question and processing..."):
            result = handle_question(question, mill)

        # -------------------------------------------------
        # CASE 1: SQL EXECUTED SUCCESSFULLY
        # -------------------------------------------------
        if isinstance(result, dict) and result.get("status") == "executed":
            st.success("✅ SQL executed successfully on database")

            # Show executed SQL for transparency / debugging
            with st.expander("🔍 Executed SQL (SSMS-ready)"):
                st.code(result["sql"], language="sql")

                if result["params"]:
                    st.markdown("**Parameters:**")
                    st.code(result["params"])

                st.markdown(f"**Rows returned:** {result['rows']}")

            # Display query result
            st.dataframe(
                result["data"],
                use_container_width=True
            )

        # -------------------------------------------------
        # CASE 2: SQL GENERATED BUT BLOCKED
        # -------------------------------------------------
        elif isinstance(result, dict) and result.get("status") == "generated":
            st.warning("⚠️ SQL was generated but execution was blocked by safety rules.")

            with st.expander("🧾 Generated SQL (NOT executed)"):
                st.code(result["sql"], language="sql")

                if result["params"]:
                    st.markdown("**Parameters:**")
                    st.code(result["params"])

        # -------------------------------------------------
        # CASE 3: UNSUPPORTED QUERY
        # -------------------------------------------------
        elif isinstance(result, dict) and result.get("unsupported"):
            st.warning(result["message"])

        # -------------------------------------------------
        # FALLBACK (should rarely occur)
        # -------------------------------------------------
        else:
            st.warning("Unable to process this query safely.")

# =================================================
# PAGE 2 — MONTH-WISE ATTENDANCE (NO LLM)
# =================================================
elif st.session_state.page == "month_attendance":

    st.title("📊 Month-wise Attendance Report")
    st.caption("Guided analytics – no LLM, fully safe & deterministic")

    # Two-column layout for date selection
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

    # Validate date range
    if start_date > end_date:
        st.error("Start date cannot be after end date")
        st.stop()

    # =================================================
    # FETCH EMPLOYEES FOR SELECTED PERIOD
    # =================================================
    with st.spinner("Fetching employees for selected period..."):
        employees = get_employees_by_date_range(
            mill,
            start_date.isoformat(),
            end_date.isoformat()
        )

    # If no employees found, stop page
    if not employees:
        st.warning("No employees found for selected date range.")
        st.stop()

    # Build display-friendly dropdown mapping
    employee_map = {
        f"{row['ECode']} - {row['EName']}": row["ECode"]
        for row in employees
    }

    # Employee selection dropdown
    selected_employee = st.selectbox(
        "Select Employee",
        options=list(employee_map.keys())
    )

    selected_ecode = employee_map[selected_employee]

    # =================================================
    # FETCH MONTH-WISE ATTENDANCE
    # =================================================
    if st.button("🔎 Show Month-wise Attendance"):
        with st.spinner("Calculating month-wise attendance..."):
            data = get_monthwise_attendance(
                mill,
                start_date.isoformat(),
                end_date.isoformat(),
                selected_ecode
            )

        if not data:
            st.warning("No attendance data found.")
            st.stop()

        # Convert result into DataFrame
        df = pd.DataFrame(data)

        # Convert month number → month name
        df["Month"] = df["mon"].apply(
            lambda x: date(1900, x, 1).strftime("%B")
        )

        # Rename columns for UI clarity
        df = df.rename(columns={
            "work_days": "Total Working Days",
            "attn_days": "Attendance Days"
        })

        st.success("✅ Month-wise attendance calculated")

        # Display final report
        st.dataframe(
            df[["Month", "Total Working Days", "Attendance Days"]],
            use_container_width=True
        )
