# LinkedIn Job Scraper — Minimal Phase-based Project (From Scratch)

> A minimal, phase-driven repo to build an interactive manual-first LinkedIn job scraper (CDP attach + floating button), then evolve into ingestion, filtering, LLM enrichment, and a simple orchestrator. This repo is intentionally small and modular — no docker or heavy deployment scaffolding.

---

## Contents

1. Philosophy & phases
2. Fresh repo layout
3. Quick start (Phase 1)
4. File responsibilities
5. Running the manual scraper (how it works)
6. Phase roadmap & success criteria
7. Data schema (JSON)
8. Config & `.env`
9. Safety, legal & best practices
10. Next steps & suggestions

---

## 1) Philosophy & phases

We build iteratively:

- **Phase 1 — Manual CDP scraper (MVP)**: attach to an already-logged-in Chrome via CDP, inject a floating “Save jobs” button, user scrolls manually and clicks to save visible posts. Reliable, low-friction, human-in-the-loop to avoid login automation and many anti-bot triggers.

- **Phase 2 — Parsing / ingestion**: parse saved raw JSON/HTML into normalized records (title, company, skills, pay hints).

- **Phase 3 — Authenticity filtering & ranking**: implement heuristics (recruiter flag, connections, experience, engagement) and compute confidence & ranking.

- **Phase 4 — LLM enrichment & keyword generation**: use an LLM (OpenAI or local) to normalize titles, extract skills, and generate better search keywords.

- **Phase 5 — Orchestration**: wire phases into a simple orchestrator to run manual ingestion → parse → filter → store in a single command. Keep manual mode available.

---

## 2) Fresh repo layout

```
project-root/
├── config/
├── data/
│   ├── raw/
│   ├── processed/
│   └── outputs/
├── scripts/
│   ├── manual_linkedin_scraper.py
│   ├── parser.py
│   ├── filter.py
│   ├── store.py
│   ├── keywords.py
│   └── orchestrator.py
├── tests/
├── examples/
├── .env.example
├── requirements.txt
├── main.py
└── README.md
```

---

## 3) Quick start — Phase 1 (manual CDP scraper)

### Prereqs

- Python 3.10+
- Playwright (sync API) + playwright browsers installed OR you will attach to a Chrome launched with `--remote-debugging-port=9222`.
- Chrome/Chromium installed and logged into LinkedIn.

### Install

```bash
python -m venv .venv
source .venv/bin/activate     # Linux / macOS
# .venv\Scripts\activate      # Windows PowerShell

pip install -r requirements.txt
# If using Playwright with browsers:
playwright install
```

### Launch Chrome for CDP attach

Open Chrome manually and log into LinkedIn. Start Chrome with remote-debugging port:

- macOS:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
```

- Linux:

```bash
google-chrome --remote-debugging-port=9222
```

- Windows (PowerShell):

```powershell
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

### Run the manual scraper

```bash
python scripts/manual_linkedin_scraper.py
```

Then:

- Use Chrome to open LinkedIn search / feed / company page or any page with job posts.
- Scroll manually to load posts (human-like).
- Click the floating **Save jobs** button injected bottom-right to capture visible posts.
- The script appends to `data/raw/` (dedupes in-session).

---

## 4) File responsibilities

- `config/config.py` — central place for paths & thresholds (reads from env).
- `scripts/manual_linkedin_scraper.py` — CDP attach + injected button, append JSON snapshots. **Primary Phase 1 file** (based on your `manual_x_scraper.py`).
- `scripts/parser.py` — raw → structured: extract title, company, text, timestamp, metrics, skills (regex + heuristics).
- `scripts/filter.py` — compute authenticity flags and `confidence` (recruiter, connections, years exp, engagements).
- `scripts/store.py` — sort, display, export CSV/JSON to `data/outputs/`.
- `scripts/keywords.py` — optional LLM-backed keyword generator (Phase 4).
- `scripts/orchestrator.py` — small runner to chain parse→filter→store (manual trigger, not scheduled).
- `main.py` — small CLI wrapper if you want to run combined steps easily.

---

## 5) How the manual scraper works (internals)

- Connects to an existing Chrome via CDP using Playwright sync `connect_over_cdp`.
- Opens a new tab and injects a tiny JS snippet that adds a floating button. The button calls a Python function (via `page.expose_function`) which:

  - calls a local `extract_visible_posts(page)` routine (robust selectors + fallbacks),
  - performs in-memory dedupe for the session,
  - appends new records to `data/raw/<handle>_posts.json`.

- This hybrid approach reduces bot-like navigation (you scroll manually) and keeps scraping robust when the site layout changes, since only visible posts are read (and injected button can be updated quickly).

---

## 6) Data schema (per-record JSON)

```json
{
  "id": "linkedin_post_<id>",
  "url": "https://linkedin.com/.../posts/...",
  "scraped_at": "2025-09-02T08:00:00Z",
  "text": "Full post text ...",
  "author_name": "Jane Doe",
  "author_profile_url": "https://linkedin.com/in/janedoe",
  "likes": 120,
  "comments": 5,
  "is_recruiter": true,
  "connections": 4000,
  "years_of_experience": 6,
  "estimated_pay": 60000,
  "duration": "full-time",
  "domain_matches": ["backend", "python"],
  "authenticity_reason": ["is_recruiter"],
  "confidence": 85
}
```

---

## 7) Config & `.env`

Create `.env` from `.env.example` and **do not** commit secrets. Example `.env.example`:

```
OPENAI_API_KEY=
KEYWORDS_PATH=./data/keywords.json
JOB_POSTS_PATH=./data/raw/job_posts.json
MIN_CONNECTIONS=500
MIN_EXPERIENCE_YEARS=3
CDP_URL=http://127.0.0.1:9222
```

`config/config.py` should read `os.getenv()` values and provide sane defaults.

---

## 8) Safety, legal & best practices

- Scraping LinkedIn may violate LinkedIn’s Terms of Service. Using a **manual, CDP-logged-in browser** lowers automation risk but does not remove legal risk. Use responsibly and consult policies/legal counsel if needed.
- Don’t expose or publish PII.
- Keep scraping human-paced — do not automate continuous scraping without consent.
- Prefer official APIs for scale.

---

## 9) Phase roadmap & success criteria (short)

- **Phase 1**: manual scraper stable. Success: capture 50 unique posts, dedupe works, JSON format consistent.
- **Phase 2**: parser converts raw->structured with >80% accuracy on fixtures.
- **Phase 3**: filter produces reasonable `confidence` scores; store exports CSV/JSON.
- **Phase 4**: LLM enriches fields and generates keyword lists.
- **Phase 5**: orchestrator chains steps with a single command; manual mode preserved.

---

## 10) Next steps (I can do any of these)

- Implement `scripts/manual_linkedin_scraper.py` now (I can generate it in your `manual_x_scraper.py` style).
- Implement `scripts/parser.py` with unit tests (fixtures-based).
- Implement `scripts/filter.py` & `scripts/store.py`.
- Or, I can scaffold the code for all Phase 1 files immediately.
