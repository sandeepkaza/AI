import streamlit as st
import datetime
import os
import json
from utils import output_file

from research_workflow import run_research_sync
from utils import ensure_env_vars

# ---------------------------------------------------------------------------
# Streamlit UI
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Portfolio Research Assistant", page_icon="📈", layout="centered"
)
st.title("📈 Portfolio Research Assistant")

# Input area
user_question = st.text_area(
    "Enter your investment question:",
    placeholder="e.g. How would the planned interest rate reduction affect my holdings in GOOGL?",
    height=120,
)

risk_levels = ["Low", "Medium", "High"]
selected_risk = st.selectbox("Select your risk awareness level:", risk_levels, index=1)

# Container for results
result_container = st.empty()

if st.button("Run Research"):
    if not user_question.strip():
        st.warning("Please enter a question before running the research.")
    else:
        try:
            ensure_env_vars(["OPENAI_API_KEY", "FRED_API_KEY"])
        except EnvironmentError as e:
            st.error(str(e))
            st.stop()

        today_str = datetime.date.today().strftime("%B %d, %Y")
        full_question = (
            f"Today is {today_str}. Risk awareness: {selected_risk}. "
            f"{user_question.strip()}"
        )

        with st.spinner(
            "Running multi-agent research — this may take a few minutes..."
        ):
            try:
                report_path, raw_output = run_research_sync(full_question)
            except Exception as e:
                st.error(f"❌ Error while running research: {e}")
                st.stop()

        st.success("Research completed!")

        # Show raw output (truncated) and download link if available
        pdf_path = None
        # Try to infer PDF path from agent output JSON
        try:
            data = json.loads(raw_output) if isinstance(raw_output, str) else {}
            if isinstance(data, dict) and "pdf_file" in data:
                pdf_path_candidate = output_file(data["pdf_file"])
                if pdf_path_candidate.exists():
                    pdf_path = str(pdf_path_candidate)
        except Exception:
            pass

        if report_path and os.path.isfile(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                report_content = f.read()
            st.markdown("### Investment report Preview")
            st.markdown(
                report_content[:3000] + ("\n..." if len(report_content) > 3000 else "")
            )
            st.download_button(
                label="Download full report",
                data=report_content,
                file_name=os.path.basename(report_path),
                mime="text/markdown",
            )
        else:
            st.info("No report file was returned by the agent workflow.")

        if pdf_path:
            with open(pdf_path, "rb") as fpdf:
                st.download_button(
                    label="Download PDF report",
                    data=fpdf.read(),
                    file_name=os.path.basename(pdf_path),
                    mime="application/pdf",
                )

        # Optionally display the raw JSON / string returned
        with st.expander("Show raw agent output"):
            st.write(raw_output)
