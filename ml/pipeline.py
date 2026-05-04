import pickle
import re
from pathlib import Path
from django.conf import settings

_DIR = Path(settings.ML_MODELS_DIR)

_xgb    = pickle.load(open(_DIR / "model_tfidf_v2.pkl", "rb"))
_svd    = pickle.load(open(_DIR / "svd_model.pkl",      "rb"))
_scaler = pickle.load(open(_DIR / "scaler_tfidf.pkl",   "rb"))
_tfidf  = pickle.load(open(_DIR / "tfidf_model.pkl",    "rb"))

print("Modeles ML charges")


def predict(text: str) -> dict:
    X = _tfidf.transform([text])
    X = _svd.transform(X)
    X = _scaler.transform(X)
    proba = float(_xgb.predict_proba(X)[0][1])

    words      = text.lower().split()
    word_count = len(words)

    client_lines = []
    for line in text.split('.'):
        line = line.strip()
        if line.lower().startswith('commercial'):
            continue
        client_lines.append(line.lower())
    client_text = ' '.join(client_lines)

    REJECT = [
        'think about it', "i'll get back", 'maybe later',
        'not right now', 'not interested', 'no thanks',
        'too expensive', "can't afford", 'not a good fit',
        'already have', 'not what we need', 'dealbreaker',
        'not certified', 'not available', 'next year',
        'another provider', 'already signed',
        'let me think', 'check internally',
        'check a few things', 'have a better idea',
        'send me an email', 'internally first',
        'need to discuss', 'need to check',
        'get back to you', 'i will get back',
        "i'll have a better", 'by then',
    ]

    BUY_CLIENT = [
        "let's get started", "let's do it",
        'move forward', 'i want to sign',
        'ready to start', 'purchase now',
        'start today', 'start the trial',
        "let's begin", 'i want to buy',
        'we will take it', "we'll take it",
    ]

    BUY_FULL = [
        'send me the contract', 'when can we start',
        'sign up', 'send the contract', 'onboarding',
        'sign before',
    ]

    has_reject     = any(r in client_text for r in REJECT)
    has_buy_client = any(b in client_text for b in BUY_CLIENT)
    has_buy_full   = any(b in text.lower() for b in BUY_FULL)
    has_strong_buy = has_buy_client or (has_buy_full and not has_reject)

    if has_reject and not has_buy_client:
        proba = min(proba, 0.30)
    if has_strong_buy and not has_reject:
        proba = max(proba, 0.80)
    if word_count > 150 and not has_strong_buy:
        CLOSING = ["let's", 'i want to', 'ready to', "we'll take"]
        if not any(c in client_text for c in CLOSING):
            proba = min(proba, 0.40)
    if word_count < 20 and not has_strong_buy:
        proba = min(proba, 0.35)

    return {
        "score":      round(proba, 4),
        "percent":    f"{proba*100:.1f}%",
        "interested": proba >= 0.65,
        "label":      "INTERESSE" if proba >= 0.65 else "PAS INTERESSE",

    }


def extract_name(text):
    patterns = [
        r"i called\s+([A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Ö][a-zà-ö]+)?)",
        r"my name is \s+([A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Ö][a-zà-ö]+)?)",
        r"c'est\s+([A-ZÀ-Ö][a-zà-ö]+(?:\s+[A-ZÀ-Ö][a-zà-ö]+)?)\s+(?:à l'appareil|qui parle)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return None



def extract_contact(text: str) -> dict:
    emails = re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    phones = re.findall(r'(\+?[\d\s\-\.]{9,15})', text)
    phones_clean = [
        p.strip() for p in phones
        if len(re.sub(r'\D', '', p)) >= 9
    ]
    return {
        "email": emails[0] if emails else "",
        "phone": phones_clean[0] if phones_clean else "",
        "name":       extract_name(text),
    }





def transcribe(audio_path: str) -> str:
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(audio_path, language="en")
    return " ".join(seg.text for seg in segments)


def process_call(audio_path: str) -> dict:
    text    = transcribe(audio_path)
    result  = predict(text)
    contact = extract_contact(text) if result["interested"] else {}
    return {
        "transcript": text,
        **result,
        "email": contact.get("email", ""),
        "phone": contact.get("phone", ""),
    }