from __future__ import annotations

import math
import re
from collections import deque

WHITESPACE_PATTERN = re.compile(r"\s+")
YEAR_PATTERN = re.compile(r"\b(20\d{2})\b")
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
PAREN_PATTERN = re.compile(r"[()]")

NEAR_STRONG = ("project", "built", "developed")
NEAR_WEAK = ("internship", "experience")

UNLOCK_GRAPH: dict[str, list[str]] = {
    "python programming": ["data preprocessing", "feature engineering", "pytorch", "tensorflow", "version control git"],
    "linear algebra": ["machine learning fundamentals", "deep learning", "optimization techniques", "mathematical modeling"],
    "probability theory": ["statistics", "machine learning fundamentals", "model evaluation and validation"],
    "statistics": ["machine learning fundamentals", "model evaluation and validation", "experiment design"],
    "data structures and algorithms": ["optimization techniques", "distributed computing"],
    "data preprocessing": ["feature engineering", "model evaluation and validation"],
    "feature engineering": ["machine learning fundamentals", "model evaluation and validation"],
    "machine learning fundamentals": ["deep learning", "hyperparameter tuning", "model evaluation and validation", "experiment design"],
    "deep learning": ["pytorch", "tensorflow", "distributed computing"],
    "optimization techniques": ["hyperparameter tuning", "distributed computing"],
    "research paper reading": ["scientific writing", "experiment design"],
    "scientific writing": ["experiment design"],
    "experiment design": ["model evaluation and validation", "hyperparameter tuning"],
    "version control git": ["distributed computing"],
    "mathematical modeling": ["machine learning fundamentals", "deep learning"],
    # Keep prior generic paths.
    "docker": ["kubernetes", "ci/cd"],
    "ml": ["deep learning", "nlp"],
    "python": ["numpy", "pandas", "machine learning fundamentals"],
}

SKILL_ALIASES: dict[str, str] = {
    "python": "python programming",
    "python programming": "python programming",
    "machine learning": "machine learning fundamentals",
    "ml": "machine learning fundamentals",
    "version control": "version control git",
    "version control git": "version control git",
    "git": "version control git",
    "tensorflow": "tensorflow",
    "pytorch": "pytorch",
    "dsa": "data structures and algorithms",
}


def normalize_skill_key(skill: str) -> str:
    s = PAREN_PATTERN.sub(" ", skill.lower())
    s = NON_ALNUM_PATTERN.sub(" ", s)
    return WHITESPACE_PATTERN.sub(" ", s).strip()


def _build_normalized_graph(graph: dict[str, list[str]]) -> dict[str, list[str]]:
    normalized: dict[str, list[str]] = {}
    for key, neighbors in graph.items():
        nk = normalize_skill_key(key)
        normalized[nk] = [normalize_skill_key(n) for n in neighbors]
    return normalized


NORMALIZED_UNLOCK_GRAPH = _build_normalized_graph(UNLOCK_GRAPH)


def _resolve_skill_key(skill: str, graph: dict[str, list[str]]) -> str:
    raw = normalize_skill_key(skill)

    alias = SKILL_ALIASES.get(raw)
    if alias:
        resolved = normalize_skill_key(alias)
        if resolved in graph:
            return resolved

    if raw in graph:
        return raw

    # Fuzzy fallback: choose graph key with strongest token overlap.
    raw_tokens = set(raw.split())
    best_key = raw
    best_overlap = 0.0

    for candidate in graph:
        cand_tokens = set(candidate.split())
        if not cand_tokens:
            continue
        overlap = len(raw_tokens & cand_tokens) / len(raw_tokens | cand_tokens)
        if overlap > best_overlap:
            best_overlap = overlap
            best_key = candidate

    return best_key if best_overlap >= 0.4 else raw


def normalize_text(text: str) -> str:
    return WHITESPACE_PATTERN.sub(" ", text.lower()).strip()


def clamp(value: float, lo: float, hi: float) -> float:
    return max(lo, min(value, hi))


def classify_base_time_days(skill: str) -> float:
    s = skill.lower()
    if any(token in s for token in ["language", "programming", "system design"]):
        return 75.0
    if any(token in s for token in ["framework", "tool", "cloud"]):
        return 30.0
    if any(token in s for token in ["library", "api"]):
        return 9.0
    return 30.0


def format_time(days: float) -> str:
    d = max(1, int(round(days)))
    if d <= 7:
        return f"{d} days"
    if d <= 30:
        weeks = max(1, int(round(d / 7)))
        return f"{weeks} weeks"

    months = d / 30.0
    lo = max(1, int(math.floor(months)))
    hi = max(lo + 1, int(math.ceil(months)))
    return f"{lo}-{hi} months"


def compute_unlock_power(skill: str, graph: dict[str, list[str]] | None = None) -> int:
    graph = graph or NORMALIZED_UNLOCK_GRAPH
    start = _resolve_skill_key(skill, graph)

    if start not in graph:
        return 0

    visited: set[str] = set()
    queue = deque([start])

    while queue:
        current = queue.popleft()
        for nxt in graph.get(current, []):
            nxt_l = nxt.lower()
            if nxt_l not in visited:
                visited.add(nxt_l)
                queue.append(nxt_l)

    return len(visited)
