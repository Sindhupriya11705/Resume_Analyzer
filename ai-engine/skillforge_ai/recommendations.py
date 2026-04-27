from __future__ import annotations


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

    seen: set[str] = set()
    out: list[str] = []
    for r in recs:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out[:8]

