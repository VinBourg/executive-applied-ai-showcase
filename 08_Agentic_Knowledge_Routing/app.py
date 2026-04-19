import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
INPUT_PATH = BASE_DIR / "task_briefs.json"


def load_tasks():
    return json.loads(INPUT_PATH.read_text())


def build_plan(task):
    request = task["request"].lower()
    steps = ["Clarify objective and expected business output"]
    tools = []

    if "backlog" in request or "support" in request:
        steps.extend([
            "Retrieve operational KPI sources",
            "Check backlog, SLA and reopened-ticket drivers",
            "Synthesize management reading and action points",
        ])
        tools.extend(["kpi_reporter", "knowledge_base", "memo_writer"])

    if "fraud" in request or "transfer" in request:
        steps.extend([
            "Retrieve fraud monitoring notes and historical patterns",
            "Extract interpretable risk drivers",
            "Draft analyst-facing summary",
        ])
        tools.extend(["fraud_patterns", "risk_scorer", "summary_writer"])

    if not tools:
        steps.extend([
            "Retrieve relevant business context",
            "Draft concise answer",
        ])
        tools.extend(["knowledge_base", "summary_writer"])

    return {
        "request": task["request"],
        "context": task["context"],
        "steps": steps,
        "tools": tools,
        "execution_style": "planner -> retriever -> analyzer -> synthesizer",
    }


def main():
    tasks = load_tasks()
    print("Agentic knowledge routing demo")
    print("=" * 29)
    for index, task in enumerate(tasks, start=1):
        plan = build_plan(task)
        print(f"Task {index}: {plan['request']}")
        print(f"  Context: {plan['context']}")
        print(f"  Execution style: {plan['execution_style']}")
        print(f"  Tools: {', '.join(plan['tools'])}")
        print("  Steps:")
        for step in plan["steps"]:
            print(f"    - {step}")
        print()


if __name__ == "__main__":
    main()
