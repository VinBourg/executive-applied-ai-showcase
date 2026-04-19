import json
import re
from pathlib import Path

DATA_PATH = Path(__file__).with_name("knowledge_base.json")
STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "of", "on", "or", "the", "to", "we", "with", "what", "can"
}


def tokenize(text):
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def load_documents():
    return json.loads(DATA_PATH.read_text())


def score_document(query_tokens, document):
    title_tokens = tokenize(document["title"])
    content_tokens = tokenize(document["content"])
    tag_tokens = [tag.lower() for tag in document["tags"]]
    overlap = sum(token in content_tokens for token in query_tokens)
    title_bonus = 2 * sum(token in title_tokens for token in query_tokens)
    tag_bonus = 3 * sum(token in tag_tokens for token in query_tokens)
    return overlap + title_bonus + tag_bonus


def retrieve(query, documents, top_k=2):
    query_tokens = tokenize(query)
    ranked = sorted(
        documents,
        key=lambda doc: score_document(query_tokens, doc),
        reverse=True,
    )
    return ranked[:top_k]


def answer_query(query, top_k=2):
    documents = load_documents()
    matches = retrieve(query, documents, top_k=top_k)
    answer_lines = []
    for match in matches:
        answer_lines.append(f"{match['title']}: {match['content']}")
    return {
        "query": query,
        "answer": "\n".join(answer_lines),
        "sources": [match["title"] for match in matches],
        "matches": matches,
    }
