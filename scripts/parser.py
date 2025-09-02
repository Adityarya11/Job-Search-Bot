# file: scripts/parser.py
import json
import os
from datetime import datetime
from scripts.keywords import get_default_keywords

def load_raw_posts(path):
    """
    Load raw scraped posts from JSON or NDJSON.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No raw posts found at {path}")
    
    # NDJSON handling
    posts = []
    with open(path, "r", encoding="utf-8") as f:
        first_line = f.readline()
        f.seek(0)
        if first_line.strip().startswith("{") and not first_line.strip().endswith("]"):
            # NDJSON
            for line in f:
                line = line.strip()
                if line:
                    try:
                        posts.append(json.loads(line))
                    except:
                        continue
        else:
            # Regular JSON list
            posts = json.load(f)

    return posts


def normalize_post(post, keywords=None):
    """
    Normalize a raw post into a structured format.
    """
    if keywords is None:
        keywords = get_default_keywords()

    text = (
        post.get("text")
        or post.get("title")
        or ""
    ).lower()

    # Match keywords
    matched = [kw for kw in keywords if kw.lower() in text]

    return {
        "id": post.get("id"),
        "url": post.get("url"),
        "author": post.get("author") or post.get("company"),
        "title": post.get("title") or None,
        "company": post.get("company") or None,
        "location": post.get("location") or None,
        "text": post.get("text") or "",
        "likes": post.get("likes", 0),
        "comments": post.get("comments", 0),
        "scraped_at": post.get("scraped_at") or datetime.utcnow().isoformat() + "Z",
        "source": post.get("source", "linkedin"),
        "matched_keywords": matched,
    }


def parse_posts(input_path, output_path, keywords=None):
    """
    Read raw posts, normalize them, and save to JSON.
    """
    raw_posts = load_raw_posts(input_path)
    normalized = [normalize_post(p, keywords) for p in raw_posts]

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, ensure_ascii=False, indent=2)

    print(f"Parsed {len(normalized)} posts → {output_path}")
    return normalized


if __name__ == "__main__":
    INPUT_PATH = "./data/raw/linkedin_posts.json"   # or linkedin_auto.ndjson
    OUTPUT_PATH = "./data/processed/parsed_posts.json"
    parse_posts(INPUT_PATH, OUTPUT_PATH)



# OUTPUT SHALL BE 

# [
#   {
#     "id": "post_12345",
#     "url": "https://linkedin.com/jobs/view/12345",
#     "author": "Jane Doe",
#     "title": "Software Engineer",
#     "company": "TechCorp",
#     "location": "Bengaluru, India",
#     "text": "We are hiring Python developers for backend roles...",
#     "likes": 120,
#     "comments": 5,
#     "scraped_at": "2025-09-02T12:30:00Z",
#     "source": "linkedin_feed",
#     "matched_keywords": ["python", "developer"]
#   }
# ]


