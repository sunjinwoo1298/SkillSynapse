from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
from flashtext import KeywordProcessor
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from models import AnalyzeSkillsResponse, SkillMetrics
from utils.common import (
    YEAR_PATTERN,
    clamp,
    classify_base_time_days,
    compute_unlock_power,
)

EMBEDDING_MODEL = SentenceTransformer("all-MiniLM-L6-v2")

PROJECT_KEYWORDS = {"project", "capstone", "built", "developed", "implemented", "application"}
REAL_WORLD_KEYWORDS = {"intern", "internship", "client", "production", "deployed", "company", "freelance", "open-source"}
IMPACT_KEYWORDS = {"improved", "increased", "reduced", "optimized", "saved", "cut", "boosted", "accuracy", "latency"}
PROBLEM_SOLVING_KEYWORDS = {"solved", "problem", "debugged", "troubleshoot", "optimized", "scaled", "designed", "refactor"}
DEPTH_KEYWORDS = {"architecture", "design pattern", "internals", "distributed", "concurrency", "profiling", "optimization", "benchmark"}

SECTION_BUCKETS: dict[str, set[str]] = {
    "skills": {"skills", "technical skills", "tooling"},
    "projects": {"projects", "project", "capstone"},
    "experience": {"experience", "internship", "work", "employment"},
    "education": {"education", "coursework", "academic"},
}

TOOL_ECOSYSTEM_MAP: dict[str, set[str]] = {
    "python": {"numpy", "pandas", "django", "flask", "fastapi", "pytest", "scikit-learn"},
    "sql": {"postgresql", "mysql", "sqlite", "sql server", "oracle", "snowflake"},
    "machine learning": {"scikit-learn", "xgboost", "lightgbm", "mlflow", "feature engineering"},
    "deep learning": {"tensorflow", "pytorch", "keras", "cnn", "rnn", "transformer"},
    "tensorflow": {"keras", "tf.data", "tensorboard", "tpu"},
    "pandas": {"numpy", "matplotlib", "seaborn", "jupyter"},
    "data visualization": {"matplotlib", "seaborn", "plotly", "tableau", "power bi"},
    "spark": {"pyspark", "hadoop", "databricks", "kafka"},
    "big data": {"spark", "hadoop", "kafka", "hive", "airflow"},
}


def build_keyword_processor(required_skills: list[str]) -> KeywordProcessor:
    kp = KeywordProcessor(case_sensitive=False)
    for skill in required_skills:
        kp.add_keyword(skill, skill.lower())
    return kp


def get_context_window(text: str, start: int, end: int, radius: int = 80) -> str:
    left = max(0, start - radius)
    right = min(len(text), end + radius)
    return text[left:right]


def _contains_any(haystack: str, tokens: set[str]) -> bool:
    return any(token in haystack for token in tokens)


def detect_skills_with_evidence(text: str, required_skills: list[str]) -> dict[str, dict[str, float]]:
    normalized_text = text.lower()
    kp = build_keyword_processor(required_skills)
    matches = kp.extract_keywords(normalized_text, span_info=True)

    evidence: dict[str, dict[str, Any]] = {
        skill.lower(): {
            "mentions": 0,
            "latest_year": None,
            "project_usage": 0,
            "real_world": 0,
            "impact": 0,
            "problem_solving": 0,
            "depth": 0,
            "section_hits": set(),
        }
        for skill in required_skills
    }

    for found_skill, start, end in matches:
        item = evidence[found_skill]
        item["mentions"] += 1

        window = get_context_window(normalized_text, start, end)

        if _contains_any(window, PROJECT_KEYWORDS):
            item["project_usage"] = 1
        if _contains_any(window, REAL_WORLD_KEYWORDS):
            item["real_world"] = 1
        if _contains_any(window, IMPACT_KEYWORDS) and any(ch.isdigit() for ch in window):
            item["impact"] = 1
        if _contains_any(window, PROBLEM_SOLVING_KEYWORDS):
            item["problem_solving"] = 1
        if _contains_any(window, DEPTH_KEYWORDS):
            item["depth"] = 1

        for bucket, tokens in SECTION_BUCKETS.items():
            if _contains_any(window, tokens):
                item["section_hits"].add(bucket)

        years = [int(y) for y in YEAR_PATTERN.findall(window)]
        if years:
            latest = max(years)
            if item["latest_year"] is None or latest > item["latest_year"]:
                item["latest_year"] = latest

    scored: dict[str, dict[str, float]] = {}
    current_year = datetime.now().year

    for skill, item in evidence.items():
        mentions = int(item["mentions"])
        latest_year = item["latest_year"]

        explicit_mention = 1.0 if mentions > 0 else 0.0
        project_usage = float(item["project_usage"])
        real_world_application = float(item["real_world"])
        multiple_usage = 1.0 if mentions >= 2 else 0.0
        recent_usage = 1.0 if latest_year is not None and latest_year >= current_year - 2 else 0.0
        impact_evidence = float(item["impact"])

        ecosystem_tokens = TOOL_ECOSYSTEM_MAP.get(skill, set())
        tool_ecosystem = 1.0 if ecosystem_tokens and _contains_any(normalized_text, ecosystem_tokens) else 0.0

        problem_solving = float(item["problem_solving"])
        depth_indicator = float(item["depth"])
        consistency = 1.0 if len(item["section_hits"]) >= 2 else 0.0

        score_model = (
            explicit_mention
            + project_usage
            + real_world_application
            + multiple_usage
            + recent_usage
            + impact_evidence
            + tool_ecosystem
            + problem_solving
            + depth_indicator
            + consistency
        )

        mentions_norm = min(mentions / 4.0, 1.0)
        indicator_density = score_model / 10.0
        confidence = clamp(0.5 * indicator_density + 0.3 * mentions_norm + 0.2 * explicit_mention, 0.0, 1.0)

        scored[skill] = {
            "mentions": float(mentions),
            "recent_usage": float(recent_usage),
            "consistency": float(consistency),
            "score_model": float(score_model),
            "confidence": float(confidence),
        }

    return scored


def build_similarity_maps(required_skills: list[str], detected_skills: list[str]) -> tuple[dict[str, float], dict[str, str | None]]:
    req_vectors = EMBEDDING_MODEL.encode(required_skills, convert_to_numpy=True, normalize_embeddings=True)

    if not detected_skills:
        return {s.lower(): 0.0 for s in required_skills}, {s.lower(): None for s in required_skills}

    det_vectors = EMBEDDING_MODEL.encode(detected_skills, convert_to_numpy=True, normalize_embeddings=True)
    sim_matrix = cosine_similarity(req_vectors, det_vectors)

    sim_map: dict[str, float] = {}
    closest_map: dict[str, str | None] = {}
    for i, req in enumerate(required_skills):
        row = sim_matrix[i]
        j = int(np.argmax(row))
        sim_map[req.lower()] = float(row[j])
        closest_map[req.lower()] = detected_skills[j].lower()
    return sim_map, closest_map


def finalize_metrics(
    required_skills: list[str],
    evidence: dict[str, dict[str, float]],
    user_feedback: dict[str, float],
    sim_map: dict[str, float],
    closest_map: dict[str, str | None],
) -> AnalyzeSkillsResponse:
    all_skills: dict[str, SkillMetrics] = {}
    needs_feedback: list[str] = []

    has_feedback = bool(user_feedback)

    for skill in required_skills:
        key = skill.lower()
        item = evidence.get(
            key,
            {
                "score_model": 0.0,
                "confidence": 0.0,
                "mentions": 0.0,
                "recent_usage": 0.0,
                "consistency": 0.0,
            },
        )

        score_model = float(item["score_model"])
        confidence = float(item["confidence"])
        mentions = float(item.get("mentions", 0.0))
        recent_usage = float(item.get("recent_usage", 0.0))
        consistency = float(item.get("consistency", 0.0))
        sim = clamp(sim_map.get(key, 0.0), 0.0, 1.0)

        if key in user_feedback:
            score = 0.6 * score_model + 0.4 * user_feedback[key]
            confidence = 0.9
        else:
            # Robust no-feedback score: blend rubric evidence with mention strength and semantic support.
            rubric_norm = clamp(score_model / 10.0, 0.0, 1.0)
            mention_strength = min(mentions / 3.0, 1.0)
            explicit_mention = 1.0 if mentions > 0.0 else 0.0

            # If skill is not explicitly mentioned, semantic similarity should not dominate.
            semantic_support = sim if explicit_mention > 0 else min(sim, 0.55)

            evidence_strength = (
                0.55 * rubric_norm
                + 0.25 * mention_strength
                + 0.10 * consistency
                + 0.10 * recent_usage
            )

            score = 10.0 * (0.80 * evidence_strength + 0.20 * semantic_support)

            # Prevent high scores for skills inferred only via semantic proximity.
            if explicit_mention == 0.0:
                score = min(score, 4.0)

            # Stabilize strong evidence cases against underestimation.
            if mentions >= 3.0 and score_model >= 6.0:
                score = max(score, 6.0)

            # Recalibrate confidence in no-feedback mode using robustness signals.
            confidence = clamp(
                0.45 * confidence
                + 0.25 * mention_strength
                + 0.20 * explicit_mention
                + 0.10 * consistency,
                0.0,
                1.0,
            )

            if explicit_mention == 0.0:
                confidence = min(confidence, 0.45)

            if confidence < 0.65 and 2.0 <= score <= 7.0:
                needs_feedback.append(skill)

        closest_skill = closest_map.get(key)
        related_score = float(evidence.get(closest_skill or "", {}).get("score_model", 0.0))

        difficulty_raw = 10.0 * (1.0 - sim) - 0.3 * related_score
        difficulty = int(round(clamp(difficulty_raw, 1.0, 10.0)))

        base_time = classify_base_time_days(skill)
        time_days = base_time * (1.0 - sim) + base_time * 0.3
        time_days_int = max(1, int(round(time_days)))

        unlock_power = compute_unlock_power(skill)

        metric = SkillMetrics(
            score=round(clamp(score, 0.0, 10.0), 2),
            confidence=round(clamp(confidence, 0.0, 1.0), 3),
            difficulty=difficulty,
            time=time_days_int,
            unlock_power=unlock_power,
        )
        all_skills[skill] = metric

    skill_gaps: dict[str, dict[str, Any]] = {}
    avg_score = sum(metric.score for metric in all_skills.values()) / len(all_skills) if all_skills else 0.0

    for skill, metric in all_skills.items():
        if metric.score < avg_score:
            skill_gaps[skill] = {
                "difficulty": metric.difficulty,
                "time": metric.time,
                "unlock_power": metric.unlock_power,
            }

    return AnalyzeSkillsResponse(
        needs_feedback=needs_feedback if not has_feedback else [],
        all_skills=all_skills,
        skill_gaps=skill_gaps,
    )
