# file: main.py
import argparse
import os

from scripts.parser import parse_posts
from scripts.filter import filter_pipeline
from scripts.store import store_pipeline
from scripts.keywords import get_keywords_from_user, get_default_keywords


def run_pipeline(raw_path, parsed_path, filtered_path, csv_path, xlsx_path, use_user_keywords=False):
    # Step 1: choose keywords
    keywords = get_keywords_from_user() if use_user_keywords else get_default_keywords()
    print(f"\n[INFO] Using keywords: {keywords}\n")

    # Step 2: parse raw scraped posts
    parsed = parse_posts(raw_path, parsed_path, keywords=keywords)

    # Step 3: filter parsed posts
    filtered = filter_pipeline(parsed_path, filtered_path, min_likes=0, min_comments=0, require_keywords=True)

    # Step 4: store final results
    store_pipeline(filtered_path, csv_path=csv_path, excel_path=xlsx_path)

    print("\n[INFO] Pipeline finished successfully!\n")
    print(f"Raw → {raw_path}")
    print(f"Parsed → {parsed_path}")
    print(f"Filtered → {filtered_path}")
    print(f"CSV → {csv_path}")
    print(f"Excel → {xlsx_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LinkedIn Job Scraper MVP Pipeline")
    parser.add_argument("--raw", default="./data/raw/linkedin_posts.json", help="Path to raw scraped posts (JSON/NDJSON)")
    parser.add_argument("--parsed", default="./data/processed/parsed_posts.json", help="Path to save parsed posts")
    parser.add_argument("--filtered", default="./data/processed/filtered_posts.json", help="Path to save filtered posts")
    parser.add_argument("--csv", default="./data/final/filtered_posts.csv", help="Path to save CSV output")
    parser.add_argument("--xlsx", default="./data/final/filtered_posts.xlsx", help="Path to save Excel output")
    parser.add_argument("--ask", action="store_true", help="Ask for custom keywords instead of defaults")

    args = parser.parse_args()

    run_pipeline(
        raw_path=args.raw,
        parsed_path=args.parsed,
        filtered_path=args.filtered,
        csv_path=args.csv,
        xlsx_path=args.xlsx,
        use_user_keywords=args.ask,
    )
