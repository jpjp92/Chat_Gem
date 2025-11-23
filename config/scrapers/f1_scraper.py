"""Simple bs4-based F1 drivers scraper.

Primary goal: return structured rows (header + data rows) for a given year.
No CSV writing here; storage/caching handled elsewhere.
"""
import os
import requests
from bs4 import BeautifulSoup
from datetime import datetime

USER_AGENT = os.getenv("CHAT_GEM_USER_AGENT", "Chat_GemBot/1.0")


def fetch_drivers(year: int, max_length: int = 5000, timeout: int = 15):
    url = f"https://www.formula1.com/en/results/{year}/drivers"
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Find first table
        table = soup.find("table")
        if not table:
            return {"success": False, "error": "Table not found on page", "year": year}

        rows = []
        for tr in table.find_all("tr"):
            cols = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
            if cols:
                rows.append(cols)

        if not rows:
            return {"success": False, "error": "No rows parsed from table", "year": year}

        meta = {
            "year": year,
            "fetched_at": datetime.utcnow().isoformat(),
            "method": "bs4",
            "source_url": url,
        }

        return {"success": True, "year": year, "rows": rows, "meta": meta}
    except Exception as e:
        return {"success": False, "error": str(e), "year": year}
