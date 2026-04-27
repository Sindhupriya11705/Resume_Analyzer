from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ScoreResult:
    score: int
    feedback: str
    suggestions: list[str]
    breakdown: dict[str, int]


def _clamp(v: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, v))


def score_submission(repo_url: str, documentation_url: str, tech_stack: list[str]) -> ScoreResult:
    """
    Baseline deterministic scoring (no external AI dependency).
    Swap with an LLM-based scorer later if desired.
    """
    code_quality = 30
    documentation = 10
    innovation = 10
    usefulness = 20
    complexity = 10

    if repo_url:
        code_quality += 10
        usefulness += 5
    if documentation_url:
        documentation += 15
    if len(tech_stack) >= 3:
        complexity += 10
    if any(t.lower() in {"kubernetes", "graphql", "websocket", "webrtc", "redis"} for t in tech_stack):
        complexity += 10
        innovation += 5

    breakdown = {
        "code_quality": _clamp(code_quality, 0, 40),
        "documentation": _clamp(documentation, 0, 25),
        "innovation": _clamp(innovation, 0, 20),
        "real_world_usefulness": _clamp(usefulness, 0, 25),
        "technology_complexity": _clamp(complexity, 0, 25),
    }

    score = _clamp(
        breakdown["code_quality"]
        + breakdown["documentation"]
        + breakdown["innovation"]
        + breakdown["real_world_usefulness"]
        + breakdown["technology_complexity"],
        0,
        100,
    )

    suggestions: list[str] = []
    if breakdown["documentation"] < 15:
        suggestions.append("Add a clear README with setup, screenshots, and API docs.")
    if breakdown["technology_complexity"] < 15 and tech_stack:
        suggestions.append("Add one advanced feature (realtime, caching, or CI/CD) to increase complexity.")
    if not repo_url:
        suggestions.append("Provide a public GitHub repository link for code review.")

    feedback = (
        "Solid start. Focus on documentation quality and showcasing real-world impact. "
        "Make sure your repo includes a demo, tests, and deployment instructions."
    )

    return ScoreResult(score=score, feedback=feedback, suggestions=suggestions, breakdown=breakdown)


def recommend_next_skills(skill_tags: list[str], recent_scores: list[int], tech_used: list[str]) -> list[str]:
    base = {s.lower() for s in skill_tags}
    recs: list[str] = []

    avg = sum(recent_scores) / max(1, len(recent_scores))
    if avg < 60:
        for s in ["problem solving", "testing", "debugging"]:
            if s not in base:
                recs.append(s)

    for s in ["system design", "databases", "authentication", "deployment"]:
        if s not in base:
            recs.append(s)

    if any(t.lower() in {"react", "next.js", "frontend"} for t in tech_used) and "performance" not in base:
        recs.append("frontend performance")
    if any(t.lower() in {"fastapi", "django", "backend"} for t in tech_used) and "api security" not in base:
        recs.append("api security")

    # cap
    seen: set[str] = set()
    out: list[str] = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out[:8]

