# file: scripts/filter.py
import json
import os

def load_parsed_posts(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No parsed posts found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_posts(posts, min_likes=0, min_comments=0, require_keywords=True):
    """
    Apply simple filters to remove irrelevant posts.
    """
    filtered = []
    for p in posts:
        # Skip if no keywords matched (if required)
        if require_keywords and not p.get("matched_keywords"):
            continue

        # Engagement thresholds
        if p.get("likes", 0) < min_likes:
            continue
        if p.get("comments", 0) < min_comments:
            continue

        # Skip posts with almost no content
        if not (p.get("title") or p.get("text")):
            continue

        filtered.append(p)
    return filtered


def save_filtered_posts(posts, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(posts)} filtered posts → {output_path}")


def filter_pipeline(input_path, output_path, **kwargs):
    posts = load_parsed_posts(input_path)
    filtered = filter_posts(posts, **kwargs)
    save_filtered_posts(filtered, output_path)
    return filtered


if __name__ == "__main__":
    INPUT_PATH = "./data/processed/parsed_posts.json"
    OUTPUT_PATH = "./data/processed/filtered_posts.json"

    # MVP rules: require keywords, but allow even low engagement
    filter_pipeline(INPUT_PATH, OUTPUT_PATH, min_likes=0, min_comments=0, require_keywords=True)
