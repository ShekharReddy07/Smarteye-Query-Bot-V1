import streamlit as st
from core.query_runner import handle_question
from core.db import test_db_connection

print("APP STARTED")


# -----------------------------
# Database connectivity check
# -----------------------------
try:
    test_db_connection("hastings")
    st.success("✅ Database connected successfully")
except Exception as e:
    st.error("❌ Database connection failed")
    st.code(str(e))
    st.stop()




st.set_page_config(
    page_title="SmartEye Query Bot",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 SmartEye Query Bot")
st.caption("AI-powered attendance query assistant")

# -------------------------------
# Auto schema sync at startup
# -------------------------------



# Sidebar controls
with st.sidebar:
    st.header("Settings")
    mill = st.selectbox(
        "Select Mill",
        ["hastings", "gondalpara", "shaktigarh"],
        index=0
    )
    st.markdown("---")
    st.markdown("**Examples:**")
    st.markdown("- How many double duty workers today?")
    st.markdown("- Show outsiders in weaving")
    st.markdown("- Absent employees today")

# Chat input
question = st.chat_input("Ask attendance-related question...")

if question:
    with st.spinner("Analyzing question..."):
        result = handle_question(question, mill)

    if isinstance(result, dict) and result.get("status") != "ok":
        st.warning(result["message"])

    elif isinstance(result, dict) and result.get("status") == "ok":
        st.success(f"Result: {len(result['data'])} rows")

        # --- Show SQL (Read-only) ---
        with st.expander("🔍 View Executed SQL (SSMS)"):
            st.code(result["sql"], language="sql")

            if result["params"]:
                st.markdown("**Parameters:**")
                st.code(result["params"])

        # --- Show Data ---
        st.dataframe(result["data"], use_container_width=True)

