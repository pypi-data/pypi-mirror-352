import os
import sys
import subprocess
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

def explain_diff(diff, openai_key, model="gpt-4"):
    client = OpenAI(api_key=openai_key)
    system_prompt = (
        "You are a skilled programmer helping to explain code changes.\n\n"
        "Given a Git diff, provide a clear and concise explanation of the staged changes in bullet points.\n"
        "- Summarize each distinct change as a separate section labeled 'Change 1', 'Change 2', etc.\n"
        "- Focus only on the code changes, without speculating on impact unless it is obvious from the diff.\n"
        "- Use professional language suitable for code review.\n"
        "- Avoid redundancy and keep explanations factual.\n"
        "- If changes are related, group them logically under the same change section.\n"
        "- Keep the explanation brief and to the point."
    )
    user_prompt = f"Please explain the following Git diff:\n\n{diff}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def main():
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("❌ OPENAI_API_KEY is not set.")
        sys.exit(1)

    diff = get_staged_diff()
    explanation = explain_diff(diff, openai_key)
    print("\n🧠 Explanation of staged changes:\n")
    print(explanation)