# file: scripts/keywords.py

def get_default_keywords():
    """
    Hardcoded keywords for Phase 1 MVP.
    These can be expanded or replaced later.
    """
    return [
        "software",
        "developer",
        "engineer",
        "backend",
        "frontend",
        "python",
        "javascript",
        "react",
        "AI",
        "machine learning",
        "data scientist",
    ]


def get_keywords_from_user():
    """
    Prompt user for comma-separated keywords at runtime.
    Falls back to defaults if user presses enter.
    """
    raw = input("Enter keywords (comma separated, leave blank for defaults): ").strip()
    if not raw:
        return get_default_keywords()
    return [kw.strip() for kw in raw.split(",") if kw.strip()]


if __name__ == "__main__":
    kws = get_keywords_from_user()
    print("Active keywords:", kws)
