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

# ============================================================
# 부정 키워드: F1 관련이지만 순위가 아닌 주제들
# ============================================================
NEGATIVE_KEYWORDS = [
    # 한국어
    r"\b룰\b", r"\b규칙\b", r"\b규정\b", r"\b레귤레이션\b",
    r"\b역사\b", r"\b히스토리\b",
    r"\b팀\b", r"\b엔진\b", r"\b서킷\b", r"\b트랙\b",
    r"\b뉴스\b", r"\b소식\b", r"\b하이라이트\b",
    r"\b설명\b", r"\b이란\b", r"\b뭐야\b", r"\b무엇\b",
    r"\b차량\b", r"\b머신\b", r"\b타이어\b",
    # English
    r"\brules?\b", r"\bregulations?\b",
    r"\bhistory\b", r"\bstory\b",
    r"\bteams?\b", r"\bengines?\b", r"\bcircuits?\b", r"\btracks?\b",
    r"\bnews\b", r"\bhighlights?\b",
    r"\bexplain\b", r"\bwhat is\b", r"\bwhat's\b",
    r"\bcars?\b", r"\bvehicles?\b", r"\btires?\b", r"\btyres?\b",
    # Español
    r"\breglas?\b", r"\breglamentos?\b",
    r"\bhistoria\b",
    r"\bequipos?\b", r"\bmotores?\b", r"\bcircuitos?\b", r"\bpistas?\b",
    r"\bnoticias?\b",
    r"\bexplicar\b", r"\bqué es\b",
    r"\bautos?\b", r"\bcoches?\b", r"\bneumáticos?\b",
]

# ============================================================
# 순위 관련 명시적 키워드를 포함한 패턴만 매칭
# ============================================================
INTENT_PATTERNS = {
    "ko": [
        # 명시적으로 "순위" 관련 키워드가 포함된 경우만
        r"\bF1\s*순위\b",
        r"\b현재\s*F1\s*순위\b",
        r"\b(F1|에프원)\s*(순위|랭킹|순위표|랭킹표)\b",
        r"\b(순위|랭킹)\s*(알려줘|보여줘|주세요|볼래|좀)\b.*\b(F1|에프원)\b",
        r"\b(F1|에프원)\s*(드라이버|선수)\s*순위\b",
        # "현재/지금/최신" + F1 + 순위 관련
        r"\b(지금|현재|최신)\s*(F1|에프원)\s*(순위|랭킹)\b",
    ],
    "en": [
        r"\b(f1|formula\s*1)\s*(driver\s*)?(standings|rankings|table|positions|leaderboard)\b",
        r"\b(current|latest)?\s*driver\s*standings\b",
        r"\b(show|tell|give)\s*(me)?\s*(the)?\s*(f1|formula\s*1)\s*(standings|rankings)\b",
    ],
    "es": [
        r"\b(f1|formula\s*1)\s*(clasificaci[oó]n|posiciones|tabla|ranking)\b",
        r"\b(clasificaci[oó]n|posiciones)\s*(de)?\s*(pilotos|f1|formula\s*1)\b",
        r"\b(muestra|dame|dime)\s*(la)?\s*(clasificaci[oó]n|tabla)\s*(de)?\s*f1\b",
    ],
}


def detect_f1_intent(text: str):
    """Detect F1 standings intent and language.

    Returns: dict {lang, intent, year, pattern}
    """
    text_lower = (text or "").lower()

    # 0) 부정 키워드 체크 - 순위가 아닌 다른 주제를 물어보는 경우
    for neg_kw in NEGATIVE_KEYWORDS:
        if re.search(neg_kw, text_lower):
            # 순위가 아닌 다른 주제이므로 즉시 None 반환
            return {"lang": None, "intent": None, "year": None, "pattern": None}

    # 1) Exact pattern check (quick confidence)
    # helper: robust year extraction (matches '2024', '2024년', '24년')
    def _extract_year(t: str):
        # match full 20xx optionally followed by '년'
        m = re.search(r"(20\d{2})(?=년|\b)", t)
        if m:
            return int(m.group(1))
        # match two-digit year with '년' suffix e.g. '24년' -> 2024
        m2 = re.search(r"\b(\d{2})년\b", t)
        if m2:
            yy = int(m2.group(1))
            return 2000 + yy
        # fallback to plain four-digit
        m3 = re.search(r"\b(20\d{2})\b", t)
        if m3:
            return int(m3.group(1))
        return None

    for lang, patterns in INTENT_PATTERNS.items():
        for p in patterns:
            if re.search(p, text_lower):
                year = _extract_year(text_lower)
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
    # F1 기본 키워드 (낮게 설정)
    "f1": 0.8,
    "f-1": 0.8,
    "에프원": 0.8,
    "formula 1": 1.0,
    # 순위 관련 명시적 키워드 (높게 설정)
    "순위": 1.2,
    "랭킹": 1.2,
    "standings": 1.2,
    "ranking": 1.2,
    "clasificación": 1.2,
    "posiciones": 1.2,
    "leaderboard": 1.0,
    "순위표": 1.2,
    # 보조 키워드 (낮게 설정)
    "driver": 0.3,
    "드라이버": 0.3,
    "알려줘": 0.2,
    "보여줘": 0.2,
    "show": 0.2,
    "현재": 0.3,
    "current": 0.3,
    "latest": 0.3,
    "최신": 0.3,
}

# 부정 키워드는 점수에서 차감
NEGATIVE_KW_WEIGHTS = {
    "룰": -2.0,
    "규칙": -2.0,
    "규정": -2.0,
    "rule": -2.0,
    "rules": -2.0,
    "regulation": -2.0,
    "역사": -1.5,
    "history": -1.5,
    "뉴스": -1.5,
    "news": -1.5,
    "설명": -1.0,
    "explain": -1.0,
    "팀": -1.0,
    "team": -0.8,
    "엔진": -1.0,
    "engine": -1.0,
}


def detect_f1_intent_scored(text: str, threshold: float = 2.2):
    """Score-based intent detection. Returns dict similar to detect_f1_intent.

    Threshold raised to 2.2 to require explicit ranking-related keywords.
    Negative keywords subtract from the score.
    """
    t = (text or "").lower()
    score = 0.0
    matched = []

    # presence of F1
    if re.search(r"\bf-?1\b|에프원|formula\s*1", t):
        # F1만으로는 낮은 점수
        if "formula 1" in t or "formula1" in t:
            score += 1.0
            matched.append('formula_1')
        else:
            score += 0.8
            matched.append('f1')

    # keyword weights
    for kw, w in KW_WEIGHTS.items():
        if kw in t:
            score += w
            matched.append(kw)

    # negative keyword penalties
    for neg_kw, penalty in NEGATIVE_KW_WEIGHTS.items():
        if neg_kw in t:
            score += penalty  # penalty는 음수
            matched.append(f'negative:{neg_kw}')

    # year extraction boosts confidence
    year = None
    m = re.search(r"(20\d{2})(?=년|\b)", t)
    if m:
        year = int(m.group(1))
    else:
        m2 = re.search(r"\b(\d{2})년\b", t)
        if m2:
            year = 2000 + int(m2.group(1))
        else:
            m3 = re.search(r"\b(20\d{2})\b", t)
            if m3:
                year = int(m3.group(1))
    if year:
        score += 0.5
        matched.append('year')

    intent = None
    if score >= threshold:
        intent = 'f1_rank'

    return {"lang": None, "intent": intent, "year": year, "score": score, "matched": matched}

