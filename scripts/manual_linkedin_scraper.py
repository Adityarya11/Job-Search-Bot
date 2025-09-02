
# file: scripts/manual_linkedin_scraper.py
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import time
import platform
import sys
import os

# Cross-platform hotkeys
if platform.system() == "Windows":
    import msvcrt
else:
    import select

# CDP connection (Chrome must be launched with --remote-debugging-port=9222)
CDP_URL = os.getenv("CDP_URL", "http://127.0.0.1:9222")
TARGET_URL = "https://www.linkedin.com/feed/"   # default; user can navigate anywhere after attach
OUTPUT_JSON = "./data/raw/linkedin_posts.json"

# ---------- Helpers ----------
def extract_visible_posts(page):
    """Scrape visible LinkedIn posts (best-effort)."""
    results = []
    posts = page.query_selector_all("div.feed-shared-update-v2, div.feed-shared-update")
    for post in posts:
        try:
            # URL (if job post link present)
            link = post.query_selector("a[href*='/jobs/view/']")
            url = link.get_attribute("href").split("?")[0] if link else None

            # Author
            author_el = post.query_selector("span.feed-shared-actor__name") or post.query_selector("span.update-components-actor__name")
            author = author_el.inner_text().strip() if author_el else "Unknown"

            # Text snippet
            text_el = post.query_selector("div.update-components-text, div.feed-shared-update-v2__description")
            text = text_el.inner_text().strip() if text_el else "No text"

            # Likes & comments (rough, may vary by UI version)
            likes = 0
            comments = 0
            try:
                likes_el = post.query_selector("span.social-details-social-counts__reactions-count")
                if likes_el:
                    likes_text = likes_el.inner_text().replace(",", "")
                    likes = int(likes_text) if likes_text.isdigit() else 0
            except:
                pass
            try:
                comments_el = post.query_selector("span.social-details-social-counts__comments")
                if comments_el:
                    comments_text = comments_el.inner_text().split()[0].replace(",", "")
                    comments = int(comments_text) if comments_text.isdigit() else 0
            except:
                pass

            results.append({
                "id": url or f"post_{hash(text)}",
                "url": url,
                "author": author,
                "text": text,
                "likes": likes,
                "comments": comments,
                "scraped_at": datetime.utcnow().isoformat() + "Z"
            })
        except Exception:
            continue
    return results

def append_json(path, records):
    """Append records into a JSON array file."""
    if not records:
        return 0
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, list):
                data = []
    except FileNotFoundError:
        data = []
    data.extend(records)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return len(records)

# ---------- Main ----------
def main():
    with sync_playwright() as p:
        # Attach to existing Chrome
        browser = p.chromium.connect_over_cdp(CDP_URL)
        contexts = browser.contexts
        if not contexts:
            raise RuntimeError("No contexts found. Did you start Chrome with --remote-debugging-port=9222?")
        context = contexts[0]

        page = context.new_page()
        page.goto(TARGET_URL, wait_until="domcontentloaded")
        page.wait_for_timeout(5000)  # let user session load

        seen = set()

        def scrape_now():
            batch = extract_visible_posts(page)
            new_records = []
            for item in batch:
                key = item.get("id") or item.get("url") or item.get("text")
                if not key or key in seen:
                    continue
                seen.add(key)
                new_records.append(item)
            saved = append_json(OUTPUT_JSON, new_records)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved {saved} new posts. Total seen: {len(seen)}")

        page.expose_function("pyScrape", scrape_now)

        # Inject floating "Save jobs" button
        page.add_init_script(r"""
            (function() {
              function addBtn(){
                if (document.getElementById('pw-save-posts-btn')) return;
                const btn = document.createElement('button');
                btn.id = 'pw-save-posts-btn';
                btn.textContent = 'Save jobs';
                Object.assign(btn.style, {
                  position: 'fixed',
                  bottom: '16px',
                  right: '16px',
                  zIndex: 2147483647,
                  padding: '10px 14px',
                  fontSize: '14px',
                  borderRadius: '6px',
                  border: '1px solid rgba(0,0,0,0.2)',
                  background: '#fff',
                  cursor: 'pointer'
                });
                btn.addEventListener('click', () => {
                  if (window.pyScrape) window.pyScrape();
                });
                document.documentElement.appendChild(btn);
              }
              try { addBtn(); } catch(e) {}
              window.addEventListener('DOMContentLoaded', addBtn);
            })();
        """)
        page.reload(wait_until="domcontentloaded")

        print("\nLinkedIn manual scraper ready!")
        print(" - Use Chrome to scroll/feed yourself.")
        print(" - Click the 'Save jobs' button (bottom-right) to save visible posts.")
        print(" - Or press 's' in terminal to save, 'q' to quit.\n")

        running = True
        while running:
            if platform.system() == "Windows":
                if msvcrt.kbhit():
                    ch = msvcrt.getch().decode().lower()
                    if ch == "s":
                        scrape_now()
                    elif ch == "q":
                        running = False
            else:
                dr, _, _ = select.select([sys.stdin], [], [], 0.1)
                if dr:
                    ch = sys.stdin.read(1).lower()
                    if ch == "s":
                        scrape_now()
                    elif ch == "q":
                        running = False
            page.wait_for_timeout(100)

        print("Detaching. Chrome remains open.")

if __name__ == "__main__":
    main()
