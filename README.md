# DATIS — Decentralized AI Trading Intelligence System

> **AI-powered stock prediction, sentiment analysis, anomaly detection, and blockchain-verified trading intelligence platform.**

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Technology Stack](#-technology-stack)
3. [System Architecture](#-system-architecture)
4. [ML/AI Models](#-mlai-models)
5. [Integration Workflow](#-integration-workflow)
6. [API Reference](#-api-reference)
7. [Project Structure](#-project-structure)
8. [Setup & Installation](#-setup--installation)
9. [Environment Variables](#-environment-variables)
10. [Key Features](#-key-features)

---

## 🎯 Project Overview

**DATIS** is a full-stack AI trading intelligence platform that combines:

- **Machine Learning** price prediction (Random Forest + LSTM)
- **FinBERT/DistilBERT** sentiment analysis from live news
- **Isolation Forest** anomaly detection for market risk
- **Bayesian Fusion Engine** for multi-model decision consensus
- **Contradiction Detection** for conflicting signal alerts
- **Blockchain Integration** (Ethereum/Sepolia) for immutable prediction audit trails
- **Portfolio Simulation** with real-time trade execution
- **Trust Scoring** based on historical prediction accuracy

The system fuses outputs from three independent AI models using Bayesian probability theory to generate actionable BUY/SELL/HOLD signals with calibrated confidence scores.

---

## 🛠 Technology Stack

### Frontend
| Technology | Version | Purpose |
|------------|---------|---------|
| **React** | 19.2.5 | UI framework |
| **TypeScript** | ~6.0.2 | Type safety |
| **Vite** | 8.0.9 | Build tool & dev server |
| **Tailwind CSS** | 4.2.4 | Utility-first styling |
| **TanStack Query** | 5.99.2 | Server state management |
| **Recharts** | 3.8.1 | Data visualization |
| **Wouter** | 3.9.0 | Lightweight routing |
| **Framer Motion** | 12.38.0 | Animations |
| **Lucide React** | 1.8.0 | Icon library |
| **Zod** | 4.3.6 | Schema validation |

### Backend
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.111.0 | High-performance Python API framework |
| **Uvicorn** | 0.29.0 | ASGI server |
| **Pydantic** | 2.7.1 | Data validation & serialization |
| **Pandas** | 2.2.2 | Data manipulation |
| **NumPy** | 1.26.4 | Numerical computing |
| **Scikit-learn** | 1.4.2 | ML algorithms (Random Forest, Isolation Forest) |
| **PyTorch** | 2.3.0 | Deep learning (LSTM) |
| **Hugging Face Transformers** | 4.40.0 | FinBERT/DistilBERT sentiment models |
| **Joblib** | 1.4.0 | Model serialization |
| **yFinance** | 0.2.38 | Live stock data fetching |
| **SQLite** | Built-in | Portfolio & prediction history storage |
| **Web3.py** | 6.15.1 | Ethereum blockchain interaction |

### Blockchain
| Technology | Purpose |
|------------|---------|
| **Solidity** | Smart contract language (pragma ^0.8.19) |
| **Ethereum / Sepolia** | Testnet deployment target |
| **Ganache / Hardhat** | Local development nodes |
| **Web3.py** | Python blockchain interface |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATIS ARCHITECTURE                             │
├─────────────────────────────────────────────────────────────────────────┤
│  FRONTEND (React 19 + Vite + Tailwind)                                   │
│  ├── Dashboard      → Real-time AI predictions & trading                 │
│  ├── Deep Analysis  → Model explainability & SHAP/LIME insights          │
│  ├── Simulator      → What-if scenario testing                           │
│  ├── Portfolio      → Live positions, P&L, trade history                 │
│  ├── Blockchain     → On-chain prediction verification                   │
│  ├── Social News    → Live sentiment analysis from news headlines        │
│  └── Failures       → Post-mortem analysis of wrong predictions          │
│                                                                          │
│  Hooks: use-api.ts → TanStack Query wrappers with fallback to mock data  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP/JSON (CORS-enabled)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BACKEND (FastAPI + Python 3.11+)                                        │
│                                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Price Model │  │  Sentiment  │  │   Anomaly   │  │   Fusion    │     │
│  │  (Random    │  │   (FinBERT  │  │  (Isolation │  │  (Bayesian  │     │
│  │   Forest +  │  │  + Lexicon) │  │   Forest)   │  │   Engine)   │     │
│  │   LSTM)     │  │             │  │             │  │             │     │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘     │
│         │                │                │                │            │
│         └────────────────┴────────────────┘                │            │
│                          │                                  │            │
│                    Contradiction Engine                     │            │
│                    (5 rule-based checks)                    │            │
│                          │                                  │            │
│         ┌────────────────┴────────────────┐                 │            │
│         ▼                                 ▼                 ▼            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  /predict   │  │  /explain   │  │   /whatif   │  │  /portfolio │     │
│  │  /sentiment │  │  /trustscore│  │  /failure   │  │  /blockchain│     │
│  │  /history   │  │  /persona   │  │  /health    │  │             │     │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘     │
│                                                                          │
│  Data Sources: yFinance (live OHLCV) | NewsAPI (live headlines)          │
│  Databases:    SQLite (portfolio.db, history.db)                         │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ Web3.py / JSON-RPC
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  BLOCKCHAIN LAYER                                                        │
│  ├── Smart Contract: DatisPredictions.sol (Solidity ^0.8.19)            │
│  │   ├── storePrediction(symbol, prediction, confidence, price)         │
│  │   ├── updateActualResult(tokenId, actualResult, price)               │
│  │   └── getPrediction(tokenId) → full prediction struct                │
│  │                                                                        │
│  ├── Modes: MOCK (default) | LOCAL (Ganache) | TESTNET (Sepolia)        │
│  └── web3_handler.py: Web3 connection, tx signing, mock fallback        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 ML/AI Models

### 1. Price Prediction Model (`models/price_model.py`)

| Aspect | Details |
|--------|---------|
| **Primary Algorithm** | Random Forest Classifier (400 estimators, max_depth=15) |
| **Deep Learning** | PyTorch LSTM (optional, when checkpoint available) |
| **Features** | OHLCV + RSI + MACD + MA20 + Volatility + Sentiment Score + Anomaly Flag |
| **Output** | BUY / HOLD / SELL probabilities, predicted close price, confidence score |
| **Training** | `train_price_ml.py` — trains on `DATIS_full_dataset_10000.csv` |
| **Serialization** | Joblib (`price_ml_model.joblib`) |

**Feature Engineering:**
- Technical indicators: RSI(14), MACD(12,26), EMA(20), rolling volatility
- Cross-model features: sentiment score, anomaly flag
- Target: `label` column (BUY/HOLD/SELL)

### 2. Sentiment Analysis Model (`models/sentiment_model.py`)

| Aspect | Details |
|--------|---------|
| **Primary Model** | DistilBERT (Hugging Face `sentiment-analysis` pipeline) |
| **Fallback** | Lexicon-based (positive/negative word counting) |
| **Data Source** | NewsAPI.org live headlines per symbol |
| **Output** | Positive / Neutral / Negative probabilities |
| **Symbols Supported** | AAPL, TSLA, MSFT, GOOGL, AMZN, NVDA, META, RELIANCE, TCS, INFY |

**Pipeline:**
1. Fetch live headlines from NewsAPI (`q={company} stock`)
2. Run each headline through DistilBERT
3. Aggregate scores (mean across headlines)
4. Fallback to lexicon if DistilBERT fails
5. Ultimate fallback: deterministic seeded random for offline demos

### 3. Anomaly Detection Model (`models/anomaly_model.py`)

| Aspect | Details |
|--------|---------|
| **Algorithm** | Isolation Forest (100 estimators, 5% contamination) |
| **Features** | Intraday range, gap %, volume Z-score, body ratio, upper/lower shadows |
| **Output** | Anomaly score (0–1), is_anomaly boolean, anomaly_type, risk_level |
| **Anomaly Types** | `volume_spike`, `price_gap`, `high_volatility`, `strong_candle_move`, `pattern_anomaly` |

### 4. Bayesian Fusion Engine (`engines/fusion.py`)

| Aspect | Details |
|--------|---------|
| **Method** | Log-Bayesian posterior fusion with configurable priors |
| **Weights** | Price: 45% | Sentiment: 35% | Anomaly: 20% |
| **Priors** | BUY: 0.33 | HOLD: 0.34 | SELL: 0.33 |
| **Confidence Thresholds** | HIGH ≥ 70% | MEDIUM ≥ 50% | LOW < 50% → forced HOLD |
| **Output** | Final action, confidence, market_state, agreement_score, reason |

**Market States:**
- `bullish` — price & sentiment aligned upward
- `bearish` — price & sentiment aligned downward
- `volatile` — anomaly risk elevated
- `sideways` — mixed or weak signals

### 5. Contradiction Detection Engine (`engines/contradiction.py`)

Five rule-based contradiction checks:

| Rule Code | Trigger Condition | Severity |
|-----------|-------------------|----------|
| `POS_SENTIMENT_FALLING_PRICE` | Positive news + falling price | HIGH |
| `BULLISH_TREND_WITH_ANOMALY` | Bullish trend + anomaly detected | HIGH |
| `NEG_SENTIMENT_RISING_PRICE` | Negative news + rising price | MEDIUM |
| `FULL_MODEL_DISAGREEMENT` | All 3 models disagree | MEDIUM |
| `VOLUME_SPIKE_NEUTRAL_PRICE` | Volume spike + flat price | LOW |

### 6. Trust Score Engine (`routes/trust.py`)

Composite trust score (0.0 – 1.0) with letter grades:

| Sub-Score | Weight | Description |
|-----------|--------|-------------|
| Accuracy | 40% | Correct / (Correct + Incorrect) |
| Confidence Calibration | 35% | How well stated confidence matches actual accuracy |
| Recency Performance | 25% | Exponentially-weighted accuracy on last 10 predictions |

**Grades:** A (≥0.80) | B (≥0.65) | C (≥0.50) | D (≥0.35) | F (<0.35)

---

## 🔄 Integration Workflow

### Core Prediction Flow

```
User Request (GET /api/predict/{symbol})
│
├─→ Load OHLCV Data ──→ yFinance or local CSV
│
├─→ Sentiment Model ──→ NewsAPI → DistilBERT → {positive, neutral, negative}
│
├─→ Anomaly Model ──→ Isolation Forest → {anomaly_score, is_anomaly, risk_level}
│
├─→ Price Model ──→ Random Forest/LSTM → {buy, hold, sell, predicted_close}
│       ↑ uses sentiment_score & anomaly_flag as features
│
├─→ Fusion Engine ──→ Bayesian posterior → {action, confidence, reason}
│
├─→ Contradiction Engine ──→ 5 rule checks → [warnings] or []
│
└─→ Response JSON ──→ {price, sentiment, anomaly, fusion, contradictions}
```

### Portfolio Trade Flow

```
User Request (POST /api/portfolio/trade)
│
├─→ Validate action (BUY/SELL/HOLD)
│
├─→ Check cash (BUY) or holdings (SELL)
│
├─→ Update SQLite portfolio DB
│   ├── holdings table (symbol, shares, avg_price)
│   ├── trade_history table (symbol, action, shares, price, pnl)
│   └── portfolio table (cash, total_value, pnl)
│
└─→ Response JSON ──→ {success, action, pnl_this_trade, portfolio_value}
```

### Blockchain Storage Flow

```
User Request (POST /api/blockchain/store)
│
├─→ Check DATIS_WEB3_MODE env var
│   ├── MOCK (default) → in-memory dict store
│   ├── LOCAL → Ganache/Hardhat @ 127.0.0.1:8545
│   └── TESTNET → Sepolia via Infura/Alchemy RPC
│
├─→ If LIVE: sign tx with DATIS_PRIVATE_KEY
│
├─→ Call storePrediction(symbol, prediction, confidence, price*100)
│
└─→ Response JSON ──→ {token_id, tx_hash, mode, status}
```

### What-If Simulation Flow

```
User Request (GET /api/whatif/{symbol}?sentiment_shift=0.2)
│
├─→ Run base prediction pipeline
│
├─→ Apply user-defined shifts:
│   ├── sentiment_shift: add to positive, subtract from negative
│   └── anomaly_score: override anomaly score
│
├─→ Re-run fusion with modified inputs
│
└─→ Response JSON ──→ {scenario, price, sentiment, anomaly, fusion}
```

---

## 📡 API Reference

### Prediction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/health` | — | Backend health check |
| `GET /api/predict/{symbol}` | GET | Full prediction pipeline |
| `GET /api/sentiment/{symbol}?text=` | GET | Sentiment analysis (optional custom text) |
| `GET /api/explain/{symbol}` | GET | Explainability report with model outputs |
| `GET /api/whatif/{symbol}?sentiment_shift=&anomaly_score=` | GET | Scenario simulation |
| `GET /api/failure/{symbol}?expected_action=` | GET | Failure analysis vs expected action |

### Portfolio Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/portfolio/` | GET | Full portfolio state |
| `POST /api/portfolio/trade` | POST | Execute BUY/SELL trade |
| `DELETE /api/portfolio/reset` | DELETE | Reset to ₹10,000 starting capital |

### Blockchain Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/blockchain/wallet` | GET | Wallet connection status |
| `POST /api/blockchain/store` | POST | Store prediction on-chain |
| `POST /api/blockchain/update` | POST | Update prediction outcome |
| `GET /api/blockchain/token/{id}` | GET | Retrieve token by ID |

### History & Trust

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/history?symbol=&limit=&offset=` | GET | Paginated prediction history |
| `GET /api/history/resolved?symbol=` | GET | Only resolved predictions |
| `POST /api/history/outcome` | POST | Record actual outcome (CORRECT/INCORRECT) |
| `GET /api/trustscore` | GET | Overall model trust score |
| `GET /api/trustscore/{symbol}` | GET | Per-symbol trust score |
| `GET /api/persona/{type}?risk_level=` | GET | Trading strategy by persona |

---

## 📁 Project Structure

```
major stock market/
├── README.md                          # This file
├── TODO.md                            # Development task tracker
├── backend/                           # FastAPI Python backend
│   ├── main.py                        # Unified entry point (uvicorn)
│   ├── config.py                      # Central configuration & hyperparameters
│   ├── requirements.txt               # Python dependencies
│   ├── data/
│   │   └── DATIS_full_dataset_10000.csv
│   ├── models/                        # ML model implementations
│   │   ├── price_model.py             # Random Forest + LSTM price predictor
│   │   ├── sentiment_model.py         # FinBERT + lexicon sentiment analyzer
│   │   ├── anomaly_model.py           # Isolation Forest anomaly detector
│   │   ├── train_price_ml.py          # Training script for price model
│   │   ├── train_fusion_ml.py         # Training script for fusion model
│   │   ├── price_ml_model.joblib      # Serialized price model
│   │   └── fusion_ml_model.joblib     # Serialized fusion model
│   ├── engines/                       # Decision engines
│   │   ├── fusion.py                  # Bayesian fusion engine
│   │   ├── contradiction.py           # Contradiction detection rules
│   │   └── strategy.py                # Strategy generator (unused)
│   ├── routes/                        # FastAPI routers
│   │   ├── explain.py                 # Explainability endpoint
│   │   ├── whatif.py                  # What-if simulation endpoint
│   │   ├── persona.py                 # Trading persona strategies
│   │   ├── portfolio.py               # Portfolio & trade execution
│   │   ├── failure.py                 # Failure analysis endpoint
│   │   ├── blockchain.py              # Blockchain interaction routes
│   │   ├── history.py                 # Prediction history CRUD
│   │   └── trust.py                   # Trust score computation
│   ├── utils/                         # Shared utilities
│   │   ├── db.py                      # SQLite portfolio DB handler
│   │   └── feature_utils.py           # SHAP/LIME explainability helpers
│   └── blockchain/                    # Blockchain layer
│       ├── blockchain_core/
│       │   ├── contract.sol           # Solidity smart contract
│       │   └── web3_handler.py        # Web3.py interface (mock/local/testnet)
│       └── database/
│           └── history_db.py          # SQLite history DB for predictions
├── frontend/                          # React frontend
│   └── datis-app/
│       ├── index.html
│       ├── package.json
│       ├── vite.config.ts
│       ├── tsconfig.json
│       └── src/
│           ├── App.tsx                # Router setup (wouter)
│           ├── main.tsx               # React entry point
│           ├── index.css              # Tailwind CSS imports
│           ├── hooks/
│           │   └── use-api.ts         # TanStack Query API hooks + mappers
│           ├── lib/
│           │   ├── mock-data.ts       # Fallback mock data (STOCKS, PORTFOLIO)
│           │   └── utils.ts           # cn() helper
│           ├── components/
│           │   ├── layout.tsx         # Main layout with symbol search
│           │   ├── sidebar.tsx        # Navigation sidebar
│           │   ├── topbar.tsx         # Top bar with theme toggle
│           │   ├── stock-selector.tsx # Symbol dropdown
│           │   ├── ui-cards.tsx       # Reusable MetricCard, ChartCard, etc.
│           │   ├── theme-provider.tsx # Dark/light mode provider
│           │   └── theme-toggle.tsx   # Theme switch button
│           └── pages/
│               ├── dashboard.tsx      # Main AI prediction dashboard
│               ├── deep-analysis.tsx  # Model explainability & SHAP
│               ├── simulator.tsx      # What-if scenario simulator
│               ├── portfolio.tsx      # Portfolio management
│               ├── blockchain.tsx     # On-chain verification viewer
│               ├── social-news.tsx    # Sentiment analysis tool
│               ├── failures.tsx       # Failed prediction analysis
│               └── not-found.tsx      # 404 page
├── dataset/                           # Additional datasets
├── datis_portfolio.db                 # SQLite DB (portfolio state)
└── history.db                         # SQLite DB (prediction history)
```

---

## ⚙ Setup & Installation

### Prerequisites
- Python 3.11+
- Node.js 20+
- (Optional) Ganache or Hardhat for local blockchain
- (Optional) Infura/Alchemy API key for testnet

### Backend Setup

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train models (if .joblib files missing)
python models/train_price_ml.py
python models/train_fusion_ml.py

# 5. Start server
uvicorn backend.main:app --reload --port 8000
```

### Frontend Setup

```bash
# 1. Navigate to frontend
cd frontend/datis-app

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
# → http://localhost:5173
```

### Unified Access
With both running:
- **API Docs:** http://localhost:8000/docs
- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:5173 (or http://localhost:8000/frontend if mounted)

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
# NewsAPI for live sentiment
NEWS_API_KEY=your_newsapi_key_here

# Blockchain mode: mock | local | testnet
DATIS_WEB3_MODE=mock
DATIS_RPC_URL=http://127.0.0.1:8545
DATIS_CONTRACT_ADDRESS=0x...
DATIS_PRIVATE_KEY=0x...
```

| Variable | Required | Description |
|----------|----------|-------------|
| `NEWS_API_KEY` | No | NewsAPI.org API key for live headlines |
| `DATIS_WEB3_MODE` | No | Blockchain mode: `mock` (default), `local`, `testnet` |
