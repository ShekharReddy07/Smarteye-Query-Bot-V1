import streamlit as st
from core.query_runner import handle_question
from core.db import test_db_connection

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="SmartEye Query Bot",
    page_icon="🤖",
    layout="wide"
)

print("APP STARTED")

# -------------------------------------------------
# Database connectivity check
# -------------------------------------------------
try:
    test_db_connection("hastings")
    st.success("✅ Database connected successfully")
except Exception as e:
    st.error("❌ Database connection failed")
    st.code(str(e))
    st.stop()

# -------------------------------------------------
# Header
# -------------------------------------------------
st.title("🤖 SmartEye Query Bot")
st.caption("AI-powered attendance query assistant (SQL-safe & auditable)")

# -------------------------------------------------
# Sidebar
# -------------------------------------------------
with st.sidebar:
    st.header("Settings")

    mill = st.selectbox(
        "Select Mill",
        ["hastings", "gondalpara", "india"],
        index=0
    )

    st.markdown("---")
    st.markdown("**Safe Examples:**")
    st.markdown("- How many outsiders today")
    st.markdown("- Outsider man-days in weaving hessian")
    st.markdown("- How many double duty workers today")
    st.markdown("- How many overtime workers today")
    st.markdown("- Show me outsider (SQL preview only)")

# -------------------------------------------------
# User Input
# -------------------------------------------------
question = st.chat_input("Ask an attendance-related question...")

if question:
    with st.spinner("Understanding question and processing..."):
        result = handle_question(question, mill)

    # 🟢 SQL EXECUTED
    if isinstance(result, dict) and result.get("status") == "executed":

        st.success("✅ SQL executed successfully on database")

        with st.expander("🔍 Executed SQL (SSMS-ready)"):
            st.code(result["sql"], language="sql")
            if result["params"]:
                st.markdown("**Parameters:**")
                st.code(result["params"])
            st.markdown(f"**Rows returned:** {result['rows']}")

        st.dataframe(result["data"], use_container_width=True)

    # 🟡 SQL GENERATED BUT BLOCKED
    elif isinstance(result, dict) and result.get("status") == "generated":

        st.warning("⚠️ SQL was generated but execution was blocked by safety rules.")

        with st.expander("🧾 Generated SQL (NOT executed)"):
            st.code(result["sql"], language="sql")
            if result["params"]:
                st.markdown("**Parameters:**")
                st.code(result["params"])

    # 🔴 UNSUPPORTED
    elif isinstance(result, dict) and result.get("unsupported"):
        st.warning(result["message"])

    else:
        st.warning("Unable to process this query safely.")
