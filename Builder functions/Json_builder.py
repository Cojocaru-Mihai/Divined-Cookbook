import requests
import re
import time
import json
from collections import defaultdict

API_URL = "https://en.wikibooks.org/w/api.php"

HEADERS = {
    "User-Agent": "Nostradamus-Binder/1.0 (NoDoxxingToday@example.com)"
}


def fetch_with_retries(params, retries=3, backoff=2):
    for attempt in range(retries):
        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            return resp.json()
        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"₍^. .^₎⟆ Request failed (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                print("₍^. .^₎⟆ Giving up on request")
                return None


def get_all_titles():
    titles = []
    gcmcontinue = None
    while True:
        params = {
            "action": "query",
            "generator": "categorymembers",
            "gcmtitle": "Category:Recipes",
            "gcmlimit": "max",
            "format": "json",
        }
        if gcmcontinue:
            params["gcmcontinue"] = gcmcontinue

        data = fetch_with_retries(params)
        if not data:
            break

        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            titles.append(page["title"])

        if "continue" in data:
            gcmcontinue = data["continue"]["gcmcontinue"]
        else:
            break

        time.sleep(0.1)
    return titles


def get_page_content(title, retries=3, backoff=2):
    params = {
        "action": "query",
        "prop": "revisions",
        "rvprop": "content",
        "rvslots": "main",
        "format": "json",
        "titles": title
    }

    for attempt in range(retries):
        try:
            resp = requests.get(API_URL, params=params, headers=HEADERS, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                revs = page.get("revisions")
                if revs:
                    return revs[0]["slots"]["main"]["*"]
            return ""

        except (requests.exceptions.RequestException, ValueError) as e:
            print(f"₍^. .^₎⟆️ Error fetching {title} (attempt {attempt+1}/{retries}): {e}")
            if attempt < retries - 1:
                time.sleep(backoff * (attempt + 1))
            else:
                print(f"₍^. .^₎⟆ Giving up on {title}")
                return ""


def extract_metadata(text):
    metadata = {}
    patterns = {
        "difficulty": r"\|\s*difficulty\s*=\s*([^|\n]+)",
        "time": r"\|\s*time\s*=\s*([^|\n]+)",
        "origin": r"\|\s*origin\s*=\s*([^|\n]+)",
        "type": r"\|\s*course\s*=\s*([^|\n]+)"
    }
    for key, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            metadata[key] = m.group(1).strip()
    return metadata


def build_categories():
    titles = get_all_titles()
    print(f"Found {len(titles)} recipes")

    categories = {
        "difficulty": defaultdict(list),
        "time": defaultdict(list),
        "origin": defaultdict(list),
        "type": defaultdict(list),
    }

    for idx, title in enumerate(titles, start=1):
        print(f"[{idx}/{len(titles)}] Processing {title}...")
        text = get_page_content(title)
        if not text:
            continue

        meta = extract_metadata(text)

        if "difficulty" in meta:
            categories["difficulty"][meta["difficulty"].lower()].append(title)
        else:
            categories["difficulty"]["unknown"].append(title)

        if "time" in meta:
            categories["time"][meta["time"].lower()].append(title)

        if "origin" in meta:
            categories["origin"][meta["origin"].strip().lower()].append(title)

        if "type" in meta:
            categories["type"][meta["type"].lower()].append(title)

        time.sleep(0.1)

    return categories


def save_to_file(categories, filename="recipes.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(categories, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    cats = build_categories()
    save_to_file(cats)
    print("₍^. .^₎⟆ Saved results to recipes.json")
