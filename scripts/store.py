# file: scripts/store.py
import json
import os
import pandas as pd

def load_filtered_posts(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"No filtered posts found at {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_to_csv(posts, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(posts)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"Saved {len(posts)} posts → {output_path}")


def save_to_excel(posts, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = pd.DataFrame(posts)
    df.to_excel(output_path, index=False, engine="openpyxl")
    print(f"Saved {len(posts)} posts → {output_path}")


def store_pipeline(input_path, csv_path=None, excel_path=None):
    posts = load_filtered_posts(input_path)
    
    if csv_path:
        save_to_csv(posts, csv_path)
    if excel_path:
        save_to_excel(posts, excel_path)
    
    return posts


if __name__ == "__main__":
    INPUT_PATH = "./data/processed/filtered_posts.json"
    CSV_PATH = "./data/final/filtered_posts.csv"
    XLSX_PATH = "./data/final/filtered_posts.xlsx"

    store_pipeline(INPUT_PATH, CSV_PATH, XLSX_PATH)
