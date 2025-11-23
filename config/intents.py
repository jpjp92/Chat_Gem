import re

# langdetect is optional in this environment; provide a lightweight fallback
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0
    _HAS_LANGDETECT = True
except Exception:
    _HAS_LANGDETECT = False


def _fallback_detect(text: str) -> str:
    """Very small fallback language detector: inspect characters/keywords."""
    t = (text or "").lower()
    if re.search(r'[가-힣]', t):
        return 'ko'
    if re.search(r'[ñáéíóúü¿¡]', t):
        return 'es'
    # simple english keyword check
    if any(w in t for w in ('the', 'show', 'what', 'who', 'when', 'driver', 'standings')):
        return 'en'
    return 'en'

if not _HAS_LANGDETECT:
    detect = _fallback_detect

INTENT_PATTERNS = {
    "ko": [
        r"\bF1\s*순위\b",
        r"\b현재\s*F1\s*순위\b",
        r"F1.*(순위|랭킹|순위표)",
        r"F-?1\b",
        r"에프원",
        r"F1.*(알려줘|보여줘|주세요|볼래|좀|알려줄)",
        r"(지금|현재|최신).{0,8}F1",
        r"(F1|에프원).{0,8}(순위|랭킹|순위표)",
    ],
    "en": [
        r"\b(f1|formula\s*1)\b.*\b(standings|rankings|table|positions)\b",
        r"\bdriver\s*standings\b",
    ],
    "es": [
        r"\b(f1|formula\s*1)\b.*\b(clasificaci[oó]n|posiciones|tabla)\b",
        r"\bclasificaci[oó]n\b",
    ],
}


def detect_f1_intent(text: str):
    """Detect F1 standings intent and language.

    Returns: dict {lang, intent, year, pattern}
    """
    text_lower = (text or "").lower()

    # 1) Exact pattern check (quick confidence)
    for lang, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                year_match = re.search(r"\b(20\d{2})\b", text_lower)
                year = int(year_match.group(1)) if year_match else None
                return {"lang": lang, "intent": "f1_rank", "year": year, "pattern": p}

    # 2) Scoring-based fallback (helpful for short / colloquial queries)
    scored = detect_f1_intent_scored(text_lower)
    if scored.get("intent"):
        return scored

    # 3) Language fallback
    try:
        lang_guess = detect(text or "en") if _HAS_LANGDETECT else _fallback_detect(text)
    except Exception:
        lang_guess = 'en'

    if lang_guess.startswith('ko'):
        lang = 'ko'
    elif lang_guess.startswith('es'):
        lang = 'es'
    elif lang_guess.startswith('en'):
        lang = 'en'
    else:
        lang = 'en'

    return {"lang": lang, "intent": None, "year": None, "pattern": None}


### Scoring-based detection
KW_WEIGHTS = {
    # high value keywords
    "f1": 1.0,
    "f-1": 1.0,
    "에프원": 1.0,
    # intent words
    "순위": 0.8,
    "랭킹": 0.8,
    "standings": 0.8,
    "clasificación": 0.8,
    "posiciones": 0.8,
    # action words
    "알려줘": 0.5,
    "보여줘": 0.5,
    "show": 0.5,
    "show me": 0.6,
}


def detect_f1_intent_scored(text: str, threshold: float = 1.8):
    """Score-based intent detection. Returns dict similar to detect_f1_intent.

    Threshold tuned to allow short queries like 'F1 순위' or 'F1순위 알려줘'.
    """
    t = (text or "").lower()
    score = 0.0
    matched = []

    # presence of F1
    if re.search(r"\bf-?1\b|에프원|f1", t):
        score += 1.0
        matched.append('f1')

    # keyword weights
    for kw, w in KW_WEIGHTS.items():
        if kw in t:
            score += w
            matched.append(kw)

    # year extraction boosts confidence
    year_match = re.search(r"\b(20\d{2})\b", t)
    year = int(year_match.group(1)) if year_match else None
    if year:
        score += 0.8
        matched.append('year')

    intent = None
    if score >= threshold:
        intent = 'f1_rank'

    return {"lang": None, "intent": intent, "year": year, "score": score, "matched": matched}
