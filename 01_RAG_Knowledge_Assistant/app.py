import sys

from core import answer_query


def build_cli_output(result):
    lines = [f"Question: {result['query']}", "", "Suggested answer:"]
    for match in result["matches"]:
        lines.append(f"- {match['title']}: {match['content']}")
    lines.append("")
    lines.append("Why these documents:")
    lines.extend(f"- matched source: {source}" for source in result["sources"])
    return "\n".join(lines)


def main():
    query = " ".join(sys.argv[1:]).strip()
    if not query:
        query = "How can we reduce support backlog while keeping SLA performance under control?"
    result = answer_query(query)
    print(build_cli_output(result))


if __name__ == "__main__":
    main()
