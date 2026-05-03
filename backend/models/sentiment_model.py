from __future__ import annotations

import re
import hashlib
import logging
from functools import lru_cache

import requests
import numpy as np

from ..config import DUMMY_SEED, NEWS_API_KEY, NEWS_API_URL

print("NEWS_API_KEY_LOADED:", bool(NEWS_API_KEY), "length:", len(NEWS_API_KEY))

logger = logging.getLogger(__name__)

DEFAULT_HEADLINES_LIMIT = 5
REQUEST_TIMEOUT = 5
MAX_TEXT_LENGTH = 512

POSITIVE_WORDS = {"bullish", "surge", "rally", "growth", "profit"}
NEGATIVE_WORDS = {"bearish", "crash", "plunge", "loss", "sell"}

WORD_PATTERN = re.compile(r"\b[a-z]+\b")

SYMBOL_NAMES = {
    "AAPL": "Apple",
    "TSLA": "Tesla",
    "MSFT": "Microsoft",
    "GOOGL": "Google",
    "AMZN": "Amazon",
    "NVDA": "NVIDIA",
    "META": "Meta",
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
}


@lru_cache(maxsize=128)
def _fetch_live_headlines(symbol: str, limit: int = DEFAULT_HEADLINES_LIMIT):
    if not NEWS_API_KEY:
        return [], {
            "status": "error",
            "totalResults": 0,
            "message": "NEWS_API_KEY missing",
        }

    company = SYMBOL_NAMES.get(symbol.upper(), symbol.upper())

    params = {
        "q": f"{company} stock",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": limit,
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(
            NEWS_API_URL,
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

        data = response.json()

        debug = {
            "status": data.get("status"),
            "totalResults": data.get("totalResults", 0),
            "message": data.get("message"),
        }

        articles = data.get("articles", [])

        headlines = []
        for item in articles:
            title = str(item.get("title", "")).strip()
            if title:
                headlines.append(title)

        return headlines[:limit], debug

    except Exception as e:
        return [], {
            "status": "error",
            "totalResults": 0,
            "message": str(e),
        }


_PIPE = None


def _get_model():
    global _PIPE

    if _PIPE is None:
        from transformers import pipeline

        _PIPE = pipeline("sentiment-analysis", device=-1)

    return _PIPE


def _transform(text: str):
    model = _get_model()
    result = model(text[:MAX_TEXT_LENGTH])[0]

    label = result["label"].lower()
    score = float(result["score"])

    if "pos" in label:
        return {
            "positive": score,
            "neutral": 1 - score,
            "negative": 0.0,
        }

    if "neg" in label:
        return {
            "positive": 0.0,
            "neutral": 1 - score,
            "negative": score,
        }

    return {
        "positive": 0.3,
        "neutral": 0.4,
        "negative": 0.3,
    }


def _lexicon_sentiment(text: str):
    words = set(WORD_PATTERN.findall(text.lower()))

    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    total = pos + neg

    if total == 0:
        return {
            "positive": 0.2,
            "neutral": 0.6,
            "negative": 0.2,
        }

    p_pos = pos / total
    p_neg = neg / total
    p_neu = 1.0 - abs(p_pos - p_neg)

    probs = np.array([p_pos, p_neu, p_neg], dtype=float)
    probs = np.clip(probs, 0.05, 0.95)
    probs /= probs.sum()

    return {
        "positive": float(probs[0]),
        "neutral": float(probs[1]),
        "negative": float(probs[2]),
    }


def _seed_sentiment(symbol: str):
    digest = int(hashlib.md5(symbol.upper().encode()).hexdigest(), 16)
    rng = np.random.default_rng((digest + DUMMY_SEED) % (2**32))
    vals = rng.dirichlet([2, 2, 2])

    return {
        "positive": float(vals[0]),
        "neutral": float(vals[1]),
        "negative": float(vals[2]),
    }


def analyze(symbol: str, text: str | None = None):
    symbol = symbol.upper().strip()

    news_debug = None
    headlines_used = 0

    if text:
        try:
            probs = _transform(text)
            model_used = "distilbert_text"
            headlines_used = 1
        except Exception as e:
            probs = _lexicon_sentiment(text)
            model_used = "lexicon_text"
            news_debug = {
                "status": "text_fallback",
                "totalResults": 0,
                "message": str(e),
            }

    else:
        headlines, news_debug = _fetch_live_headlines(symbol)

        if headlines:
            scores = []

            for headline in headlines:
                try:
                    scores.append(_transform(headline))
                except Exception:
                    scores.append(_lexicon_sentiment(headline))

            probs = {
                "positive": float(np.mean([s["positive"] for s in scores])),
                "neutral": float(np.mean([s["neutral"] for s in scores])),
                "negative": float(np.mean([s["negative"] for s in scores])),
            }

            model_used = "live_news_distilbert"
            headlines_used = len(headlines)

        else:
            probs = _seed_sentiment(symbol)
            model_used = "seed"
            headlines_used = 0

    label = max(probs, key=probs.get)

    return {
        "symbol": symbol,
        "label": label,
        "positive": round(float(probs["positive"]), 4),
        "neutral": round(float(probs["neutral"]), 4),
        "negative": round(float(probs["negative"]), 4),
        "headlines_used": headlines_used,
        "model_used": model_used,
        "news_debug": news_debug,
    }