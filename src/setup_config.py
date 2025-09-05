# FILE: src/setup_config.py
# Purpose:
#   Interactively collect your settings and write them to config.yaml.
#   - If config.yaml exists, we ask before overwriting.
#   - Prompts accept comma-separated lists for titles/keywords/links.
# Why YAML:
#   Human-friendly, supports comments, great for configs.
# How to run:
#   python .\src\setup_config.py

from pathlib import Path
import sys
import yaml  # provided by PyYAML

ROOT = Path(__file__).resolve().parents[1]
CFG_PATH = ROOT / "config.yaml"

def ask(prompt: str, default: str = "") -> str:
    """
    Ask a question with an optional default (shown in [brackets]).
    Empty input returns the default.
    """
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val or default

def ask_list(prompt: str, default_items: list[str]) -> list[str]:
    """
    Ask for a comma-separated list. Trims spaces. Empty → default list.
    """
    default_str = ", ".join(default_items)
    raw = input(f"{prompt} [{default_str}]: ").strip()
    if not raw:
        return default_items
    return [item.strip() for item in raw.split(",") if item.strip()]

def build_config() -> dict:
    print("\n=== jobbot • interactive config setup ===\n")

    # --- user profile ---
    full_name = ask("Your full name", "Your Name")
    email = ask("Your email (for outreach)", "your_email@domain.com")
    phone = ask("Phone (optional)", "123-456-7890")
    portfolio_links = ask_list("Portfolio links (comma-separated)", [
        "https://github.com/yourhandle",
        "https://linkedin.com/in/yourhandle"
    ])

    # --- storage locations (relative paths are OK) ---
    excel_path = ask("Excel log path", "data/applications.xlsx")
    screenshots_dir = ask("Screenshots folder", "proof/")

    # --- search preferences ---
    base_titles = ask_list("Base job titles", ["python developer"])
    include_keywords = ask_list("Must-have keywords", ["Python", "Django", "Flask", "AWS", "SQL"])
    exclude_keywords = ask_list("Exclude keywords", [])
    recency = ask("Posting recency in minutes", "60")
    try:
        posting_recency_minutes = int(recency)
    except ValueError:
        print("  ! Not a number; using 60")
        posting_recency_minutes = 60

    # --- scheduler ---
    run_every_minutes = ask("Run every N minutes", "15")
    try:
        run_every_minutes = int(run_every_minutes)
    except ValueError:
        print("  ! Not a number; using 15")
        run_every_minutes = 15

    cfg = {
        "user_profile": {
            "full_name": full_name,
            "email": email,
            "phone": phone,
            "resume_master_path": "data/master_resume.docx",
            "cover_letter_template_path": "data/cover_letter_template.docx",
            "portfolio_links": portfolio_links,
        },
        "storage": {
            "excel_path": excel_path,
            "screenshots_dir": screenshots_dir,
            "sheets": ["jobs_raw", "apply_queue", "applications", "emails"],
        },
        "search": {
            "base_titles": base_titles,
            "auto_expand_titles": True,
            "expansion_map": {
                "python developer": [
                    "full stack python developer",
                    "python backend developer",
                    "django developer",
                    "flask developer",
                    "fastapi developer",
                    "software engineer (python)",
                ]
            },
            "include_keywords": include_keywords,
            "exclude_keywords": exclude_keywords,
            "posting_recency_minutes": posting_recency_minutes,
        },
        "scheduler": {
            "run_every_minutes": run_every_minutes,
            "max_apps_per_run": None,
        },
        "platforms": {
            "enabled": ["Dice"],
            "per_platform": {
                "Dice": {
                    "method": "Playwright",
                    "filters": {
                        "date_posted": "Past 24 hours",
                        "remote": True,
                        "location": "United States",
                    },
                    "visible_browser": True,
                }
            },
        },
        "email_outreach": {
            "enabled": True,
            "smtp_provider": "gmail",
            "from_address": email,
            "app_password_env": "GMAIL_APP_PASSWORD",
            "subject_template": "Experienced {role} • {top_skills} • Available Immediately",
            "body_template_path": "data/cold_email_template.txt",
            "attach_tailored_resume": True,
        },
    }
    return cfg

def main() -> int:
    if CFG_PATH.exists():
        ans = input(f"\nconfig.yaml already exists at {CFG_PATH}. Overwrite? (y/N): ").strip().lower()
        if ans != "y":
            print("Keeping existing config.yaml. No changes made.")
            return 0

    cfg = build_config()
    CFG_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Write YAML safely; default_flow_style=False → block format (nice & readable)
    with CFG_PATH.open("w", encoding="utf-8") as f:
        yaml.safe_dump(cfg, f, sort_keys=False, allow_unicode=True)

    print(f"\nWrote config.yaml → {CFG_PATH}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
