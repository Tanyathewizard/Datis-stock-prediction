import socket
import numpy as np
import pandas as pd
import yfinance as yf

from pathlib import Path

from ..config import DUMMY_SEED, DATA_DIR


# =========================
# SOCKET TIMEOUT
# =========================

socket.setdefaulttimeout(20)

# =========================
# DATASET PATH
# =========================

DATASET_DIR = Path(
    r"F:\major stock market\data\dataset"
)

# =========================
# MAJOR INDIAN STOCKS
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
    "TITAN",
    "ULTRACEMCO",
}


# =========================
# CLEAN OHLCV
# =========================

def _clean_ohlcv(
    df: pd.DataFrame,
    rows: int
) -> pd.DataFrame:

    df = df.copy()

    df.columns = [
        str(c).lower().strip()
        for c in df.columns
    ]

    required = [
        "open",
        "high",
        "low",
        "close",
        "volume",
    ]

    if not all(
        col in df.columns
        for col in required
    ):
        raise ValueError(
            "Missing required OHLCV columns"
        )

    df = df[required].dropna()

    return (
        df.tail(rows)
        .reset_index(drop=True)
    )


# =========================
# SYMBOL ALIASES
# =========================

def _symbol_aliases(
    symbol: str
) -> list[str]:

    symbol = symbol.upper().strip()

    aliases = {

        "RELIANCE": [
            "RELIANCE",
            "RELIANCE.NS",
            "RELIANCE_NS",
        ],

        "TCS": [
            "TCS",
            "TCS.NS",
            "TCS_NS",
        ],

        "INFY": [
            "INFY",
            "INFY.NS",
            "INFY_NS",
        ],

        "HDFCBANK": [
            "HDFCBANK",
            "HDFCBANK.NS",
            "HDFCBANK_NS",
        ],

        "ICICIBANK": [
            "ICICIBANK",
            "ICICIBANK.NS",
            "ICICIBANK_NS",
        ],

        "SBIN": [
            "SBIN",
            "SBIN.NS",
            "SBIN_NS",
        ],

        "ITC": [
            "ITC",
            "ITC.NS",
            "ITC_NS",
        ],

        "LT": [
            "LT",
            "LT.NS",
            "LT_NS",
        ],

        "WIPRO": [
            "WIPRO",
            "WIPRO.NS",
            "WIPRO_NS",
        ],

        "AAPL": ["AAPL"],
        "TSLA": ["TSLA"],
        "NVDA": ["NVDA"],
        "MSFT": ["MSFT"],
        "GOOGL": ["GOOGL"],
    }

    return aliases.get(symbol, [symbol])


# =========================
# NORMALIZE TICKER
# =========================

def _normalize_ticker(
    symbol: str
) -> str:

    symbol = symbol.upper().strip()

    # Already normalized
    if symbol.endswith(".NS"):
        return symbol

    # Indian NSE stocks
    if symbol in INDIAN_STOCKS:
        return f"{symbol}.NS"

    # US/global stocks
    return symbol


# =========================
# LOAD INDIVIDUAL CSV
# =========================

def _load_from_individual_csv(
    symbol: str,
    rows: int
):

    file_map = {

        "AAPL": "AAPL.csv",
        "TSLA": "TSLA.csv",
        "NVDA": "NVDA.csv",
        "MSFT": "MSFT.csv",
        "GOOGL": "GOOGL.csv",

        "RELIANCE": "RELIANCE_NS.csv",
        "TCS": "TCS_NS.csv",
        "INFY": "INFY_NS.csv",
        "HDFCBANK": "HDFCBANK_NS.csv",
        "ICICIBANK": "ICICIBANK_NS.csv",
        "SBIN": "SBIN_NS.csv",
        "ITC": "ITC_NS.csv",
    }

    search_dirs = [
        DATASET_DIR,
        DATA_DIR,
    ]

    for folder in search_dirs:

        filename = file_map.get(
            symbol,
            f"{symbol}.csv"
        )

        csv_path = folder / filename

        if csv_path.exists():

            try:

                df = pd.read_csv(csv_path)

                print(
                    f"[utils] Loaded CSV dataset for {symbol}"
                )

                return _clean_ohlcv(df, rows)

            except Exception as e:

                print(
                    f"[utils] CSV read failed for {csv_path}: {e}"
                )

    return None


# =========================
# LOAD COMBINED DATASET
# =========================

def _load_from_combined_dataset(
    symbol: str,
    rows: int
):

    combined_files = [

        DATASET_DIR /
        "DATIS_full_dataset_10000.csv",

        DATA_DIR /
        "DATIS_full_dataset_10000.csv",
    ]

    for combined_path in combined_files:

        if combined_path.exists():

            try:

                df = pd.read_csv(combined_path)

                df.columns = [
                    str(c).lower().strip()
                    for c in df.columns
                ]

                # Normalize symbol column
                if (
                    "symbol" not in df.columns
                    and "ticker" in df.columns
                ):
                    df["symbol"] = df["ticker"]

                if "symbol" in df.columns:

                    aliases = _symbol_aliases(symbol)

                    df = df[
                        df["symbol"]
                        .astype(str)
                        .str.upper()
                        .isin(aliases)
                    ]

                required = [
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                ]

                if (
                    not df.empty
                    and all(
                        col in df.columns
                        for col in required
                    )
                ):

                    print(
                        f"[utils] Loaded {len(df)} rows for {symbol} from combined dataset"
                    )

                    return (
                        df[required]
                        .tail(rows)
                        .reset_index(drop=True)
                    )

            except Exception as e:

                print(
                    f"[utils] Combined dataset failed: {e}"
                )

    return None


# =========================
# SYNTHETIC FALLBACK
# =========================

def _synthetic_fallback(
    symbol: str,
    rows: int
):

    print(
        f"[utils] Using synthetic fallback for {symbol}"
    )

    rng = np.random.default_rng(
        DUMMY_SEED + hash(symbol) % 10000
    )

    close = 100 + np.cumsum(
        rng.normal(0, 1, rows)
    )

    close = np.clip(close, 1, None)

    spread = rng.uniform(
        0.5,
        2.5,
        rows
    )

    high = close + spread
    low = close - spread

    open_ = close + rng.uniform(
        -1,
        1,
        rows
    )

    volume = rng.integers(
        500000,
        5000000,
        rows
    ).astype(float)

    return pd.DataFrame({

        "open": open_,
        "high": high,
        "low": low,
        "close": close,
        "volume": volume,

    })


# =========================
# MAIN STOCK LOADER
# =========================

def load_ohlcv(
    symbol: str,
    rows: int = 100
) -> pd.DataFrame:

    symbol = symbol.upper().strip()

    # =====================
    # LIVE YAHOO FETCH
    # =====================

    try:

        ticker = _normalize_ticker(symbol)

        print(
            f"[yfinance] Fetching live data for {ticker}"
        )

        df = yf.download(

            ticker,

            period="6mo",
            interval="1d",

            progress=False,

            auto_adjust=True,

            threads=False,

            timeout=10,

            prepost=True,

            repair=True,
        )

        # Fix MultiIndex issue
        if isinstance(
            df.columns,
            pd.MultiIndex
        ):
            df.columns = (
                df.columns
                .get_level_values(0)
            )

        if not df.empty:

            print(
                f"[yfinance] Successfully loaded {ticker}"
            )

            return _clean_ohlcv(df, rows)

        else:

            raise Exception(
                "Yahoo returned empty dataframe"
            )

    except Exception as e:

        print(
            f"[utils] Live fetch failed for {symbol}: {e}"
        )

    # =====================
    # INDIVIDUAL CSV
    # =====================

    df = _load_from_individual_csv(
        symbol,
        rows
    )

    if df is not None:
        return df

    # =====================
    # COMBINED DATASET
    # =====================

    df = _load_from_combined_dataset(
        symbol,
        rows
    )

    if df is not None:
        return df

    # =====================
    # SYNTHETIC FALLBACK
    # =====================

    return _synthetic_fallback(
        symbol,
        rows
    )


# =========================
# NORMALIZE SERIES
# =========================

def normalize_series(
    series: np.ndarray
) -> np.ndarray:

    mn = series.min()
    mx = series.max()

    if mx == mn:

        return np.zeros_like(
            series,
            dtype=float
        )

    return (
        (series - mn)
        / (mx - mn)
    )


# =========================
# SOFTMAX
# =========================

def softmax(
    scores: dict
) -> dict:

    vals = np.array(
        list(scores.values()),
        dtype=float
    )

    exps = np.exp(
        vals - vals.max()
    )

    probs = exps / exps.sum()

    return {

        k: float(round(p, 4))

        for k, p in zip(
            scores.keys(),
            probs
        )
    }