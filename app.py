import streamlit as st
from core.query_runner import handle_question
from core.db import test_db_connection

# -------------------------------------------------
# Page configuration (MUST be first Streamlit call)
# -------------------------------------------------
st.set_page_config(
    page_title="SmartEye Query Bot",
    page_icon="🤖",
    layout="wide"
)

# -------------------------------------------------
# App startup indicator (for logs)
# -------------------------------------------------
print("APP STARTED")

# -------------------------------------------------
# Database connectivity check (HARD GATE)
# -------------------------------------------------
try:
    test_db_connection("hastings")
    st.success("✅ Database connected successfully")
except Exception as e:
    st.error("❌ Database connection failed")
    st.code(str(e))
    st.stop()

# -------------------------------------------------
# App Header
# -------------------------------------------------
st.title("🤖 SmartEye Query Bot")
st.caption("AI-powered attendance query assistant (SQL-safe & audit-ready)")

# -------------------------------------------------
# Sidebar controls
# -------------------------------------------------
with st.sidebar:
    st.header("Settings")

    mill = st.selectbox(
        "Select Mill",
        ["hastings", "gondalpara", "india"],
        index=0
    )

    st.markdown("---")
    st.markdown("**Safe Example Queries:**")
    st.markdown("- How many outsiders today")
    st.markdown("- Outsider man-days in weaving hessian")
    st.markdown("- How many double duty workers today")
    st.markdown("- How many overtime workers today")

# -------------------------------------------------
# User Input
# -------------------------------------------------
question = st.chat_input("Ask an attendance-related question...")

if question:
    with st.spinner("Analyzing question and executing SQL..."):
        result = handle_question(question, mill)

    # -------------------------
    # Unsupported / blocked
    # -------------------------
    if isinstance(result, dict) and result.get("unsupported"):
        st.warning(result["message"])

    # -------------------------
    # Successful execution
    # -------------------------
    elif isinstance(result, dict) and result.get("status") == "executed":

        st.success("✅ SQL executed successfully on database")

        # --- Executed SQL (SSMS visibility) ---
        with st.expander("🔍 Executed SQL (SSMS-ready)"):
            st.code(result["sql"], language="sql")
            if result["params"]:
                st.markdown("**Parameters:**")
                st.code(result["params"])
            st.markdown(f"**Rows returned:** {result['rows']}")

        # --- Result Data ---
        st.dataframe(result["data"], use_container_width=True)

    # -------------------------
    # Safety fallback
    # -------------------------
    else:
        st.warning("This query could not be processed safely.")
