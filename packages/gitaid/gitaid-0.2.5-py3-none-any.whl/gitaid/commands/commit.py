import os
import subprocess
import openai
import sys
from openai import OpenAI

def get_staged_diff():
    result = subprocess.run(
        ["git", "diff", "--cached"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    if result.returncode != 0 or not result.stdout.strip():
        print("❌ No staged changes or error reading git diff.")
        sys.exit(1)
    return result.stdout

def generate_commit_message(diff, openai_key, model="gpt-3.5-turbo"):
    openai.api_key = openai_key

    system_prompt = (
        "You are an AI assistant that writes high-quality Git commit messages. "
        "Base the commit message on the actual functionality implemented, include meaningful features."
	"Summarize the intent early in concise but descriptive enough to understand what/why of the staged code changes."
        "Prefer imperative mood and keep under 70 characters unless detail is important."
	"But make sure to capture what the code change is about."
	"Include main changes only."
	"ignore changes that are generally not included in commit messages or changes that are not as important."
        "If multiple concerns, list as bullet points."
	"Follow standard commit message formats."
    )
    user_prompt = f"Here is a git diff of the staged changes:\n\n{diff}"
    client = OpenAI(api_key=openai_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=150,
        temperature=0.3
    )

    return response.choices[0].message.content.strip()

def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY is not set.")
        sys.exit(1)

    diff = get_staged_diff()
    commit_message = generate_commit_message(diff, openai_key)

    print("\n💬 Suggested commit message:\n")
    print(commit_message)
    print("\nDo you want to use this commit message? (y/n): ", end="")
    if input().lower() == 'y':
        subprocess.run(["git", "commit", "-m", commit_message])
        print("✅ Commit successful.")
    else:
        print("❌ Commit aborted.")

