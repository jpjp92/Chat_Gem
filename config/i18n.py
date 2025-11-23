"""Localization helpers for F1 display headers and messages."""
from typing import List

# Basic header localization map (site headers are usually English abbreviations)
HEADER_MAP = {
    "Pos.": {"ko": "순위", "en": "Pos.", "es": "Pos."},
    "Position": {"ko": "순위", "en": "Pos.", "es": "Pos."},
    "Driver": {"ko": "드라이버", "en": "Driver", "es": "Piloto"},
    "Nationality": {"ko": "국적", "en": "Nationality", "es": "Nacionalidad"},
    "Team": {"ko": "팀", "en": "Team", "es": "Equipo"},
    "Pts.": {"ko": "포인트", "en": "Pts.", "es": "Pts."},
    "Points": {"ko": "포인트", "en": "Points", "es": "Puntos"},
}


def localize_headers(headers: List[str], lang: str = "en") -> List[str]:
    """Map raw headers to localized labels when possible.

    If a header isn't found in the map, return it unchanged.
    """
    localized = []
    for h in headers:
        if h in HEADER_MAP:
            localized.append(HEADER_MAP[h].get(lang, h))
        else:
            # try simple normalization: capitalize words, handle abbreviations
            localized.append(h)
    return localized
