"""Simple bs4-based F1 drivers scraper.

Primary goal: return structured rows (header + data rows) for a given year.
No CSV writing here; storage/caching handled elsewhere.
"""
import os
import requests
from bs4 import BeautifulSoup
import re
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

        # post-process driver names to be human-friendly
        def _clean_driver_name(raw: str) -> str:
            if not raw:
                return raw
            s = raw.strip()
            # Insert space between camelcase parts, e.g. MaxVerstappenVER -> Max Verstappen VER
            s = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', s)
            # normalize multiple spaces
            s = re.sub(r'\s+', ' ', s).strip()
            parts = [p for p in s.split(' ') if p]
            # drop trailing all-uppercase short codes like 'VER', 'HAM', 'PIA'
            if parts and re.fullmatch(r'[A-Z]{2,4}', parts[-1]):
                parts = parts[:-1]
            # Prefer simple 'First Last' form: keep first and last token
            if len(parts) == 0:
                return ''
            if len(parts) == 1:
                return parts[0]
            # join first and last (handles middle names gracefully)
            return f"{parts[0]} {parts[-1]}"

        # find driver column index from header row if present
        driver_idx = None
        if rows and any('driver' in (c or '').lower() for c in rows[0]):
            for i, c in enumerate(rows[0]):
                if 'driver' in (c or '').lower():
                    driver_idx = i
                    break

        if driver_idx is not None:
            for i in range(1, len(rows)):
                if len(rows[i]) > driver_idx:
                    rows[i][driver_idx] = _clean_driver_name(rows[i][driver_idx])

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
