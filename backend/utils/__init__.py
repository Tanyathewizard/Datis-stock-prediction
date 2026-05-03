import numpy as np
import pandas as pd
import yfinance as yf
from pathlib import Path

from ..config import DUMMY_SEED, DATA_DIR

DATASET_DIR = Path(r"F:\major stock market\data\dataset")


def _clean_ohlcv(df: pd.DataFrame, rows: int) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(c).lower().strip() for c in df.columns]

    required = ["open", "high", "low", "close", "volume"]

    if not all(col in df.columns for col in required):
        raise ValueError("Missing OHLCV columns")

    df = df[required].dropna()
    return df.tail(rows).reset_index(drop=True)


def _symbol_aliases(symbol: str) -> list[str]:
    symbol = symbol.upper().strip()

    aliases = {
        "RELIANCE": ["RELIANCE", "RELIANCE.NS", "RELIANCE_NS"],
        "TCS": ["TCS", "TCS.NS", "TCS_NS"],
        "INFY": ["INFY", "INFY.NS", "INFY_NS"],
        "AAPL": ["AAPL"],
        "TSLA": ["TSLA"],
        "NVDA": ["NVDA"],
    }

    return aliases.get(symbol, [symbol])


def load_ohlcv(symbol: str, rows: int = 100) -> pd.DataFrame:
    symbol = symbol.upper().strip()

    try:
        ticker = symbol

        if symbol in ["RELIANCE", "TCS", "INFY"]:
            ticker = f"{symbol}.NS"

        df = yf.download(
            ticker,
            period="6mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
        )

        if not df.empty:
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            return _clean_ohlcv(df, rows)

    except Exception as e:
        print(f"[utils] Live fetch failed for {symbol}: {e}")

    file_map = {
        "AAPL": "AAPL.csv",
        "TSLA": "TSLA.csv",
        "NVDA": "NVDA.csv",
        "RELIANCE": "RELIANCE_NS.csv",
        "TCS": "TCS_NS.csv",
        "INFY": "INFY_NS.csv",
    }

    search_dirs = [DATASET_DIR, DATA_DIR]

    for folder in search_dirs:
        filename = file_map.get(symbol, f"{symbol}.csv")
        csv_path = folder / filename

        if csv_path.exists():
            try:
                df = pd.read_csv(csv_path)
                return _clean_ohlcv(df, rows)
            except Exception as e:
                print(f"[utils] CSV read failed for {csv_path}: {e}")

    combined_files = [
        DATASET_DIR / "DATIS_full_dataset_10000.csv",
        DATA_DIR / "DATIS_full_dataset_10000.csv",
    ]

    for combined_path in combined_files:
        if combined_path.exists():
            try:
                df = pd.read_csv(combined_path)
                df.columns = [str(c).lower().strip() for c in df.columns]

                if "symbol" not in df.columns and "ticker" in df.columns:
                    df["symbol"] = df["ticker"]

                if "symbol" in df.columns:
                    aliases = _symbol_aliases(symbol)
                    df = df[df["symbol"].astype(str).str.upper().isin(aliases)]

                required = ["open", "high", "low", "close", "volume"]

                if not df.empty and all(col in df.columns for col in required):
                    print(f"[utils] Loaded {len(df)} rows for {symbol} from combined dataset")
                    return df[required].tail(rows).reset_index(drop=True)

            except Exception as e:
                print(f"[utils] Combined dataset failed: {e}")

    print(f"[utils] Using synthetic fallback for {symbol}")

    rng = np.random.default_rng(DUMMY_SEED + hash(symbol) % 10000)

    close = 100 + np.cumsum(rng.normal(0, 1, rows))
    close = np.clip(close, 1, None)

    spread = rng.uniform(0.5, 2.5, rows)
    high = close + spread
    low = close - spread
    open_ = close + rng.uniform(-1, 1, rows)
    volume = rng.integers(500000, 5000000, rows).astype(float)

    return pd.DataFrame({
        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,
    })


def normalize_series(series: np.ndarray) -> np.ndarray:
    mn, mx = series.min(), series.max()

    if mx == mn:
        return np.zeros_like(series, dtype=float)

    return (series - mn) / (mx - mn)


def softmax(scores: dict) -> dict:
    vals = np.array(list(scores.values()), dtype=float)
    exps = np.exp(vals - vals.max())
    probs = exps / exps.sum()

    return {
        k: float(round(p, 4))
        for k, p in zip(scores.keys(), probs)
    }