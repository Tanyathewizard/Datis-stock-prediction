from __future__ import annotations

import re
import socket
import hashlib
import logging
from functools import lru_cache

import requests
import numpy as np
import yfinance as yf

# =========================
# SOCKET TIMEOUT
# =========================

socket.setdefaulttimeout(20)

from ..config import (
    DUMMY_SEED,
    NEWS_API_KEY,
    NEWS_API_URL,
)

print(
    "NEWS_API_KEY_LOADED:",
    bool(NEWS_API_KEY),
    "length:",
    len(NEWS_API_KEY),
)

logger = logging.getLogger(__name__)

# =========================
# CONFIG
# =========================

DEFAULT_HEADLINES_LIMIT = 5
REQUEST_TIMEOUT = 5
MAX_TEXT_LENGTH = 512

POSITIVE_WORDS = {
    "bullish",
    "surge",
    "rally",
    "growth",
    "profit",
    "beat",
    "strong",
    "buy",
}

NEGATIVE_WORDS = {
    "bearish",
    "crash",
    "plunge",
    "loss",
    "sell",
    "weak",
    "downgrade",
}

WORD_PATTERN = re.compile(r"\b[a-z]+\b")

# =========================
# INDIAN STOCK LIST
# =========================

INDIAN_STOCKS = {
    "RELIANCE",
    "TCS",
    "INFY",
    "HDFCBANK",
    "ICICIBANK",
    "SBIN",
    "ITC",
    "LT",
    "WIPRO",
    "BHARTIARTL",
    "AXISBANK",
    "KOTAKBANK",
    "HCLTECH",
    "MARUTI",
    "ASIANPAINT",
    "BAJFINANCE",
    "ADANIENT",
    "SUNPHARMA",
    "ULTRACEMCO",
    "TITAN",
}


# =========================
# NORMALIZE TICKER
# =========================

def _normalize_ticker(symbol: str) -> str:

    symbol = symbol.upper().strip()

    if symbol in INDIAN_STOCKS:
        return f"{symbol}.NS"

    return symbol


# =========================
# AUTO COMPANY NAME FETCH
# =========================

@lru_cache(maxsize=256)
def _get_company_name(symbol: str) -> str:
    """
    Dynamically fetch company name
    from Yahoo Finance
    """

    try:

        ticker = _normalize_ticker(symbol)

        stock = yf.Ticker(ticker)

        info = stock.info

        company = (
            info.get("longName")
            or info.get("shortName")
            or symbol
        )

        print(f"[Company] {symbol} -> {company}")

        return str(company)

    except Exception as e:

        logger.warning(
            f"Company fetch failed for {symbol}: {e}"
        )

        return symbol


# =========================
# NEWS FETCHER
# =========================

@lru_cache(maxsize=128)
def _fetch_live_headlines(
    symbol: str,
    limit: int = DEFAULT_HEADLINES_LIMIT
):

    if not NEWS_API_KEY:

        return [], {
            "status": "error",
            "totalResults": 0,
            "message": "NEWS_API_KEY missing",
        }

    company = _get_company_name(symbol)

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

            title = str(
                item.get("title", "")
            ).strip()

            if title:
                headlines.append(title)

        print(
            f"[NewsAPI] {symbol} -> {len(headlines)} headlines"
        )

        return headlines[:limit], debug

    except Exception as e:

        logger.error(
            f"News fetch failed: {e}"
        )

        return [], {
            "status": "error",
            "totalResults": 0,
            "message": str(e),
        }


# =========================
# FINBERT MODEL
# =========================

_PIPE = None


def _get_model():

    global _PIPE

    if _PIPE is None:

        from transformers import pipeline

        print("[FinBERT] Loading model...")

        _PIPE = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            tokenizer="ProsusAI/finbert",
            device=-1,
        )

        print(
            "[FinBERT] Model loaded successfully"
        )

    return _PIPE


# =========================
# FINBERT SENTIMENT
# =========================

def _transform(text: str):

    model = _get_model()

    result = model(
        text[:MAX_TEXT_LENGTH]
    )[0]

    label = result["label"].lower()

    score = float(result["score"])

    if "positive" in label:

        return {
            "positive": score,
            "neutral": (1 - score) * 0.5,
            "negative": (1 - score) * 0.5,
        }

    elif "negative" in label:

        return {
            "positive": (1 - score) * 0.5,
            "neutral": (1 - score) * 0.5,
            "negative": score,
        }

    else:

        return {
            "positive": 0.15,
            "neutral": 0.7,
            "negative": 0.15,
        }


# =========================
# LEXICON FALLBACK
# =========================

def _lexicon_sentiment(text: str):

    words = set(
        WORD_PATTERN.findall(
            text.lower()
        )
    )

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

    probs = np.array(
        [p_pos, p_neu, p_neg],
        dtype=float,
    )

    probs = np.clip(
        probs,
        0.05,
        0.95,
    )

    probs /= probs.sum()

    return {
        "positive": float(probs[0]),
        "neutral": float(probs[1]),
        "negative": float(probs[2]),
    }


# =========================
# RANDOM FALLBACK
# =========================

def _seed_sentiment(symbol: str):

    digest = int(
        hashlib.md5(
            symbol.upper().encode()
        ).hexdigest(),
        16,
    )

    rng = np.random.default_rng(
        (digest + DUMMY_SEED)
        % (2**32)
    )

    vals = rng.dirichlet([2, 2, 2])

    return {
        "positive": float(vals[0]),
        "neutral": float(vals[1]),
        "negative": float(vals[2]),
    }


# =========================
# MAIN ANALYZER
# =========================

def analyze(
    symbol: str,
    text: str | None = None
):

    symbol = symbol.upper().strip()

    news_debug = None
    headlines_used = 0

    # =====================
    # DIRECT TEXT ANALYSIS
    # =====================

    if text:

        try:

            probs = _transform(text)

            model_used = "finbert_text"

            headlines_used = 1

        except Exception as e:

            logger.error(
                f"FinBERT failed: {e}"
            )

            probs = _lexicon_sentiment(text)

            model_used = "lexicon_text"

            news_debug = {
                "status": "text_fallback",
                "totalResults": 0,
                "message": str(e),
            }

    # =====================
    # LIVE NEWS ANALYSIS
    # =====================

    else:

        headlines, news_debug = (
            _fetch_live_headlines(symbol)
        )

        if headlines:

            scores = []

            for headline in headlines:

                try:

                    scores.append(
                        _transform(headline)
                    )

                except Exception as e:

                    logger.error(
                        f"Headline analysis failed: {e}"
                    )

                    scores.append(
                        _lexicon_sentiment(
                            headline
                        )
                    )

            probs = {
                "positive": float(
                    np.mean([
                        s["positive"]
                        for s in scores
                    ])
                ),
                "neutral": float(
                    np.mean([
                        s["neutral"]
                        for s in scores
                    ])
                ),
                "negative": float(
                    np.mean([
                        s["negative"]
                        for s in scores
                    ])
                ),
            }

            model_used = "live_news_finbert"

            headlines_used = len(headlines)

        else:

            probs = _seed_sentiment(symbol)

            model_used = "seed"

            headlines_used = 0

    # =====================
    # FINAL LABEL
    # =====================

    label = max(
        probs,
        key=probs.get
    )

    return {
        "symbol": symbol,
        "label": label,
        "positive": round(
            float(probs["positive"]),
            4,
        ),
        "neutral": round(
            float(probs["neutral"]),
            4,
        ),
        "negative": round(
            float(probs["negative"]),
            4
        ),
        "headlines_used": headlines_used,
        "model_used": model_used,
        "news_debug": news_debug,
    }