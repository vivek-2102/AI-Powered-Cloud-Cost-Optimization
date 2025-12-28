import os
import json
from dotenv import load_dotenv  # type: ignore
from .llm_client_call import LLMClient
from .project_profile import generate_project_profile
from .mock_billing import generate_synthetic_billing
from .recommendations import generate_recommendations
from .export_report import export_report
from .utils import ARTIFACTS_DIR,save_description,read_json

load_dotenv()

LLM = LLMClient()
if not LLM.is_configured():
    print("Warning: HF_API_KEY not set. LLM-powered options (2-4) will fail. Set HF_API_KEY in .env or environment to enable them.")

# Artifact paths
PROJECT_DESC_PATH = os.path.join(ARTIFACTS_DIR, "project_description.txt")
PROJECT_PROFILE_PATH = os.path.join(ARTIFACTS_DIR, "project_profile.json")
BILLING_PATH = os.path.join(ARTIFACTS_DIR, "mock_billing.json")
RECOMMENDATIONS_PATH = os.path.join(ARTIFACTS_DIR, "recommendations.json")
REPORT_PATH = os.path.join(ARTIFACTS_DIR, "cost_optimization_report.json")


def prompt_input(prompt_text):
    try:
        return input(prompt_text)
    except KeyboardInterrupt:
        print("\nAborted by user.")
        raise



# function to display main menu and handle user choices
def main_menu():
    menu = """
AI Cloud Cost Optimizer - CLI

1) Enter project description
2) Generate project_profile.json (LLM)
3) Generate mock_billing.json (LLM)
4) Generate recommendations (LLM)
5) Export final report
6) Exit

Choose an option: """
    while True:
        choice = prompt_input(menu).strip()

        # -------- OPTION 1 --------
        if choice == "1":
            print("Paste your project description.")
            print("Press ENTER on an empty line to finish.\n")

            lines = []
            while True:
                line = prompt_input("")
                if line.strip() == "":
                    if lines:
                        break
                    print("Description cannot be empty.")
                    continue
                lines.append(line)

            desc = "\n".join(lines).strip()
            save_description(PROJECT_DESC_PATH,desc)

        # -------- OPTION 2 --------
        elif choice == "2":
            if not os.path.exists(PROJECT_DESC_PATH):
                print("Run option 1 first.")
                continue

            with open(PROJECT_DESC_PATH, "r", encoding="utf-8") as f:
                desc = f.read()

            try:
                generate_project_profile(
                    desc, LLM, save_path=PROJECT_PROFILE_PATH
                )
                print(f"Generated project_profile.json -> {PROJECT_PROFILE_PATH}")
            except Exception as e:
                print("Error generating project profile:", e)

        # -------- OPTION 3 --------
        elif choice == "3":
            profile = read_json(PROJECT_PROFILE_PATH)
            if not profile:
                print("Run option 2 first.")
                continue

            try:
                generate_synthetic_billing(
                    profile, LLM, save_path=BILLING_PATH
                )
                print(f"Generated synthetic_billing.json -> {BILLING_PATH}")
            except Exception as e:
                print("Error generating synthetic billing:", e)

        # -------- OPTION 4 --------
        elif choice == "4":
            profile = read_json(PROJECT_PROFILE_PATH)

            if not profile:
                print("Run option 2 first.")
                continue

            billing = read_json(BILLING_PATH)

            try:
                generate_recommendations(
                    profile,
                    LLM,
                    billing=billing,
                    save_path=RECOMMENDATIONS_PATH
                )
                print(f"Generated recommendations -> {RECOMMENDATIONS_PATH}")
            except Exception as e:
                print("Error generating recommendations:", e)


        # -------- OPTION 5 --------
        elif choice == "5":
            profile = read_json(PROJECT_PROFILE_PATH)
            billing = read_json(BILLING_PATH)
            recs = read_json(RECOMMENDATIONS_PATH)

            if not profile or not billing or not recs:
                print("Run options 2–4 first.")
                continue

            export_report(
                profile,
                billing,
                recs,
                save_path=REPORT_PATH
            )
            print(f"Exported final report -> {REPORT_PATH}")

        # -------- OPTION 6 --------
        elif choice == "6":
            print("Thank You For Using.")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main_menu()
