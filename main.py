import asyncio
import datetime
import argparse

from research_workflow import run_research_async
from utils import ensure_env_vars

# Validate required environment variables once at startup
try:
    ensure_env_vars(["OPENAI_API_KEY", "FRED_API_KEY"])
except EnvironmentError as e:
    print(str(e))
else:
    print("All required API keys are set.")


async def run_workflow():
    # Ensure at least the OpenAI key is present before proceeding
    ensure_env_vars(["OPENAI_API_KEY"])

    parser = argparse.ArgumentParser(description="Run portfolio research workflow")
    parser.add_argument("--question", type=str, help="Investment question to research")
    parser.add_argument(
        "--risk",
        type=str,
        choices=["Low", "Medium", "High"],
        default="Medium",
        help="Risk awareness level to incorporate in the prompt",
    )
    args = parser.parse_args()

    if args.question:
        user_question = args.question
    else:
        user_question = input("Enter your investment question: ").strip()
        if not user_question:
            print("Question is required.")
            return

    today_str = datetime.date.today().strftime("%B %d, %Y")
    question = f"Today is {today_str}. Risk awareness: {args.risk}. {user_question}"

    print("Running multi-agent workflow...\n")

    try:
        report_path, final_output = await asyncio.wait_for(
            run_research_async(question), timeout=1200
        )
    except asyncio.TimeoutError:
        print("\n❌ Workflow timed out after 20 minutes.")
        return

    print(
        f"Workflow Completed Response from Agent: {final_output}, investment report created: {report_path if report_path else '[unknown]'}"
    )


if __name__ == "__main__":
    asyncio.run(run_workflow())
