import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_PATH = BASE_DIR / "knowledge_base.json"
SAMPLE_QUERIES_PATH = BASE_DIR / "sample_queries.json"

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "in", "is", "of", "on", "or", "the", "to", "we", "with", "what", "can",
    "should", "our", "while", "under", "into", "this", "that",
}

INTENT_KEYWORDS = {
    "support_operations": {"support", "backlog", "sla", "ticket", "tickets", "reopened"},
    "knowledge_enablement": {"knowledge", "faq", "onboarding", "training", "adoption"},
    "fraud_analytics": {"fraud", "risk", "transfer", "beneficiary", "transaction"},
    "ai_content_workflow": {"content", "brochure", "marketing", "draft", "workflow"},
}

INTENT_INTROS = {
    "support_operations": "The priority is to stabilize support operations while keeping response quality visible.",
    "knowledge_enablement": "The strongest lever is to improve structured knowledge access before adding more manual effort.",
    "fraud_analytics": "The most relevant answer is to keep risk detection interpretable and tied to concrete transaction signals.",
    "ai_content_workflow": "The workflow should start from validated business inputs and use AI to accelerate drafting rather than replace review.",
    "general": "The recommended approach is to combine structured business guidance with a small number of clearly grounded actions.",
}

ACTION_LIBRARY = {
    "support_operations": [
        "Track backlog, SLA breaches and reopened-ticket drivers in one weekly operations review.",
        "Escalate reopened tickets to senior support analysts to reduce repeated handling loops.",
        "Document the top recurring issues in a shared knowledge base to reduce avoidable demand.",
    ],
    "knowledge_enablement": [
        "Create a structured onboarding kit with FAQ, training sequence and support contacts.",
        "Turn repetitive support questions into reusable knowledge entries.",
        "Measure adoption and repetitive request reduction after each enablement update.",
    ],
    "fraud_analytics": [
        "Flag transactions combining high amount, new beneficiary and foreign transfer patterns.",
        "Keep risk rules readable for analysts so operational review remains explainable.",
        "Separate high-risk alerts from manual-review alerts to improve triage discipline.",
    ],
    "ai_content_workflow": [
        "Start from validated product facts, target pains and proof points before generating drafts.",
        "Use AI for first-pass structuring, then keep the final review business-led.",
        "Store approved prompts and editorial rules to make output quality repeatable.",
    ],
    "general": [
        "Clarify the business objective and expected output before automating the workflow.",
        "Use a small set of grounded source materials rather than broad generic context.",
        "Translate insights into a short action list that a business owner can immediately use.",
    ],
}

FOLLOW_UP_LIBRARY = {
    "support_operations": [
        "Which categories drive the largest share of backlog growth?",
        "Where are SLA breaches concentrated by team or priority level?",
    ],
    "knowledge_enablement": [
        "Which questions are repeated most often by new users?",
        "Which onboarding assets are missing or hard to find today?",
    ],
    "fraud_analytics": [
        "Which risk drivers explain the highest share of manual reviews?",
        "Which alerts should be escalated automatically versus analyst-reviewed?",
    ],
    "ai_content_workflow": [
        "Which product facts and proof points are already validated?",
        "Which approval steps should remain human-controlled?",
    ],
    "general": [
        "What business owner will use the output first?",
        "What would make the result immediately actionable?",
    ],
}


def tokenize(text):
    tokens = re.findall(r"[a-zA-Z]+", text.lower())
    return [token for token in tokens if token not in STOPWORDS]


def load_documents():
    return json.loads(DATA_PATH.read_text())


def load_sample_queries():
    return json.loads(SAMPLE_QUERIES_PATH.read_text())


def score_document(query_tokens, document):
    title_tokens = tokenize(document["title"])
    content_tokens = tokenize(document["content"])
    tag_tokens = [tag.lower() for tag in document["tags"]]
    overlap = sum(token in content_tokens for token in query_tokens)
    title_bonus = 2 * sum(token in title_tokens for token in query_tokens)
    tag_bonus = 3 * sum(token in tag_tokens for token in query_tokens)
    return overlap + title_bonus + tag_bonus


def retrieve(query, documents, top_k=3):
    query_tokens = tokenize(query)
    ranked = []
    for document in documents:
        scored = dict(document)
        scored["score"] = score_document(query_tokens, document)
        ranked.append(scored)
    ranked.sort(key=lambda doc: doc["score"], reverse=True)
    return ranked[:top_k]


def detect_intent(query_tokens, matches):
    counts = {intent: 0 for intent in INTENT_KEYWORDS}
    for intent, keywords in INTENT_KEYWORDS.items():
        counts[intent] += sum(token in keywords for token in query_tokens)
        for match in matches:
            counts[intent] += sum(tag.lower() in keywords for tag in match["tags"])
    best_intent, best_score = max(counts.items(), key=lambda item: item[1])
    if best_score == 0:
        return "general"
    return best_intent


def first_sentence(text):
    sentence = text.split(".")[0].strip()
    return sentence if sentence.endswith(".") else f"{sentence}."


def build_answer(matches, intent):
    intro = INTENT_INTROS[intent]
    evidence = " ".join(first_sentence(match["content"]) for match in matches[:2])
    return f"{intro} {evidence}".strip()


def build_confidence(matches):
    if not matches:
        return "low"
    score_total = sum(match["score"] for match in matches)
    if score_total >= 10:
        return "high"
    if score_total >= 5:
        return "medium"
    return "low"


def answer_query(query, top_k=3):
    documents = load_documents()
    matches = retrieve(query, documents, top_k=top_k)
    query_tokens = tokenize(query)
    intent = detect_intent(query_tokens, matches)
    return {
        "query": query,
        "intent": intent,
        "confidence": build_confidence(matches),
        "answer": build_answer(matches, intent),
        "recommended_actions": ACTION_LIBRARY[intent],
        "follow_up_questions": FOLLOW_UP_LIBRARY[intent],
        "sources": [match["title"] for match in matches],
        "matches": matches,
    }
