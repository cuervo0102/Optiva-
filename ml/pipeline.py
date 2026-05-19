import pickle
import re
import numpy as np
from pathlib import Path
from django.conf import settings

_DIR    = Path(settings.ML_MODELS_DIR)
_xgb    = pickle.load(open(_DIR / "model_tfidf_v2.pkl", "rb"))
_svd    = pickle.load(open(_DIR / "svd_model (2).pkl",      "rb"))
_scaler = pickle.load(open(_DIR / "scaler_tfidf.pkl",   "rb"))
_tfidf  = pickle.load(open(_DIR / "tfidf_model (1).pkl",    "rb"))

print("Modeles ML charges")

n_features = _scaler.n_features_in_
print(f"Scaler attend : {n_features} features")


def _get_features(text: str) -> np.ndarray:
    """Produit exactement le bon nombre de features"""
    X_tfidf = _tfidf.transform([text])
    X_svd   = _svd.transform(X_tfidf) 

    if n_features == 200:
        return X_svd

    sentences  = [s.strip() for s in text.replace('\n', '.').split('.') if s.strip()]
    total      = len(sentences)
    third      = max(1, total // 3)
    beginning  = ' '.join(sentences[:third]).lower()
    end        = ' '.join(sentences[2*third:]).lower()
    full       = text.lower()

    pos = np.array([[
        min(len(full.split()) / 500, 1.0),
        min(total / 50, 1.0),
        float('@' in full),
        float(any(p in full for p in ['06', '07', '05', '+212', '555'])),
        len(end.split()) / max(len(beginning.split()), 1),
    ]], dtype=np.float32)

    return np.hstack([X_svd, pos])


def predict(text: str) -> dict:
    X     = _get_features(text)
    X     = _scaler.transform(X)
    proba = float(_xgb.predict_proba(X)[0][1])
    return {
        "score":      round(proba, 4),
        "percent":    f"{proba*100:.1f}%",
        "interested": proba >= 0.65,
        "label":      "INTERESSE" if proba >= 0.65 else "PAS INTERESSE",
    }


def extract_contact(text: str) -> dict:

    emails = re.findall(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text
    )

    if not emails:
        clean = text.replace('\u2019', "'").replace('\u2018', "'")
        at_match = re.search(
            r"(?:it'?s|is|email\s+is)\s+([\w][\w.\-\s]{1,40}?)\s+at\s+([\w\.-]+\.[a-zA-Z]{2,})",
            clean, re.IGNORECASE
        )
        if at_match:
            local  = at_match.group(1).strip().replace(' ', '.')
            domain = at_match.group(2).strip()
            emails = [f"{local}@{domain}"]

    phones = re.findall(r'(\+?[\d][\d\s\-\.]{7,14})', text)
    phones_clean = [
        re.sub(r'[\s\-\.]', '', p).strip()
        for p in phones
        if len(re.sub(r'\D', '', p)) >= 8
    ]

    name = None
    for pattern in [
        r"my name is\s+([A-ZÀ-Ö][a-zA-Zà-ö]+(?:\s+[A-ZÀ-Ö][a-zA-Zà-ö]+)?)",
        r"(?:yes,?\s+)?my name(?:'s| is)\s+([A-ZÀ-Ö][a-zA-Zà-ö]+)",
        r"i(?:'m| am)\s+([A-ZÀ-Ö][a-zA-Zà-ö]+)",
    ]:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            break

    return {
        "email": emails[0]       if emails       else "",
        "phone": phones_clean[0] if phones_clean else "",
        "name":  name            if name         else "",
    }

def transcribe(audio_path: str) -> str:
    import subprocess
    import tempfile
    import os
    from faster_whisper import WhisperModel

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        subprocess.run([
            "ffmpeg", "-i", audio_path,
            "-ar", "16000",
            "-ac", "1",
            "-y", tmp_path
        ], capture_output=True, check=True)

        model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=settings.WHISPER_DEVICE,
            compute_type="int8"
        )
        segments, _ = model.transcribe(tmp_path, language="en")
        return " ".join(seg.text for seg in segments)

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def process_call(audio_path: str) -> dict:
    text    = transcribe(audio_path)
    result  = predict(text)
    contact = extract_contact(text) if result["interested"] else {}
    return {
        "transcript": text,
        "score":      result["score"],
        "percent":    result["percent"],
        "interested": result["interested"],
        "label":      result["label"],
        "email":      contact.get("email", ""),
        "phone":      contact.get("phone", ""),
        "name":       contact.get("name",  ""),
    }