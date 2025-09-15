import streamlit as st
import datetime
import os
import json
from dotenv import load_dotenv
from utils import output_file

from research_workflow import run_research_sync
from utils import ensure_env_vars

# ---------------------------------------------------------------------------
# Environment and Streamlit UI
# ---------------------------------------------------------------------------

# Load local .env if present (no effect in containerized/managed envs)
load_dotenv(override=False)

st.set_page_config(
    page_title="Portfolio Research Assistant", page_icon="📈", layout="centered"
)

# Inject custom favicon with light/dark support and set dark theme based on OS
st.markdown(
        """
        <script>
            (function () {
                try {
                    var head = document.getElementsByTagName('head')[0];
                    var favicon = document.getElementById('favicon');
                    if (!favicon) {
                        favicon = document.createElement('link');
                        favicon.id = 'favicon';
                        favicon.rel = 'shortcut icon';
                        head.appendChild(favicon);
                    }

                    var lightIcon = "data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cg clip-path='url(%23clip0_459_932)'%3E%3Cpath d='M11.4327 1.00388C9.64526 0.919753 8.14218 2.21231 7.88574 3.91533C7.87559 3.99436 7.86035 4.07085 7.84766 4.14733C7.44904 6.26845 5.59303 7.87459 3.3638 7.87459C2.5691 7.87459 1.82263 7.67064 1.17265 7.31372C1.09394 7.27038 1 7.32647 1 7.4157V7.87204V14.7479H7.84512V9.59291C7.84512 8.64452 8.61189 7.87459 9.5564 7.87459H11.2677C13.2049 7.87459 14.7639 6.2608 14.6877 4.29774C14.6191 2.53099 13.1922 1.08802 11.4327 1.00388Z' fill='black'/%3E%3C/g%3E%3Cdefs%3E%3CclipPath id='clip0_459_932'%3E%3Crect width='14' height='14' fill='white' transform='translate(1 1)'/%3E%3C/clipPath%3E%3C/defs%3E%3C/svg%3E%0A";
                    var darkIcon =  "data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cg clip-path='url(%23clip0_459_963)'%3E%3Cpath d='M11.4327 1.00388C9.64526 0.919753 8.14218 2.21231 7.88574 3.91533C7.87559 3.99436 7.86035 4.07085 7.84766 4.14733C7.44904 6.26845 5.59303 7.87459 3.3638 7.87459C2.5691 7.87459 1.82263 7.67064 1.17265 7.31372C1.09394 7.27038 1 7.32647 1 7.4157V7.87204V14.7479H7.84512V9.59291C7.84512 8.64452 8.61189 7.87459 9.5564 7.87459H11.2677C13.2049 7.87459 14.7639 6.2608 14.6877 4.29774C14.6191 2.53099 13.1922 1.08802 11.4327 1.00388Z' fill='white'/%3E%3C/g%3E%3Cdefs%3E%3CclipPath id='clip0_459_963'%3E%3Crect width='14' height='14' fill='white' transform='translate(1 1)'/%3E%3C/clipPath%3E%3C/defs%3E%3C/svg%3E%0A";

                    function applyTheme() {
                        var prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
                        if (prefersDark) {
                            document.documentElement.setAttribute('data-theme', 'dark');
                            favicon.setAttribute('href', darkIcon);
                        } else {
                            document.documentElement.removeAttribute('data-theme');
                            favicon.setAttribute('href', lightIcon);
                        }
                    }

                    applyTheme();
                    try {
                        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', applyTheme);
                    } catch (e) {}
                } catch (e) {}
            })();
        </script>
        """,
        unsafe_allow_html=True,
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
