import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "product_brief.json"
BROCHURE_PATH = BASE_DIR / "brochure_draft.md"
PROMPT_PATH = BASE_DIR / "llm_prompt.txt"


def load_brief():
    return json.loads(INPUT_PATH.read_text())


def build_brochure(brief):
    proof_points = "\n".join(f"- {point}" for point in brief["proof_points"])
    return f"""# {brief['product_name']}

## Who it is for
{brief['target_audience'].capitalize()}

## Business challenge
{brief['problem'].capitalize()}.

## Solution
{brief['solution'].capitalize()}.

## Why it matters
{proof_points}
"""


def build_prompt(brief):
    return f"""You are writing an executive brochure.
Product: {brief['product_name']}
Audience: {brief['target_audience']}
Problem: {brief['problem']}
Solution: {brief['solution']}
Proof points: {', '.join(brief['proof_points'])}
Task: write a concise, premium brochure draft in a professional tone.
"""


def main():
    brief = load_brief()
    brochure = build_brochure(brief)
    prompt = build_prompt(brief)
    BROCHURE_PATH.write_text(brochure)
    PROMPT_PATH.write_text(prompt)
    print(brochure)
    print(f"Generated: {BROCHURE_PATH.name}, {PROMPT_PATH.name}")


if __name__ == "__main__":
    main()
