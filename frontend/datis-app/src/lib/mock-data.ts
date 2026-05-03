// ═══════════════════════════════════════════════════════════════
// DATIS Mock Data — Used when backend is unavailable
// ═══════════════════════════════════════════════════════════════

export interface StockAnalysis {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: string;
  signal: "BUY" | "SELL" | "HOLD" | "STRONG BUY" | "STRONG SELL";
  confidence: number;
  trustScore: number;
  lstmPrediction: number;
  finbertSentiment: number;
  anomalyScore: number;
  bayesianFusion: number;
  aiDecision: string;
  aiExplanation: string;
  contradiction: boolean;
  contradictionDetails?: string;
  priceHistory: { time: string; price: number; volume: number }[];
  featureImportance: { feature: string; importance: number }[];
  sentimentSummary: string;
  trendCharts: { date: string; lstm: number; actual: number; sentiment: number }[];
}

export interface PortfolioData {
  totalValue: number;
  cashBalance: number;
  investedValue: number;
  totalPnl: number;
  totalPnlPercent: number;
  roi: number;
  holdings: Holding[];
  tradeHistory: Trade[];
  allocation: { name: string; value: number; color: string }[];
}

export interface Holding {
  symbol: string;
  name: string;
  shares: number;
  avgPrice: number;
  currentPrice: number;
  pnl: number;
  pnlPercent: number;
  value: number;
}

export interface Trade {
  id: string;
  symbol: string;
  action: "BUY" | "SELL";
  shares: number;
  price: number;
  total: number;
  timestamp: string;
  status: "COMPLETED" | "PENDING" | "FAILED";
}

export interface BlockchainLog {
  id: string;
  txHash: string;
  prediction: string;
  symbol: string;
  confidence: number;
  timestamp: string;
  status: "VERIFIED" | "PENDING" | "FAILED";
  blockNumber: number;
  nftMinted: boolean;
  trustChainScore: number;
}

export interface SocialAnalysisResult {
  sentiment: "POSITIVE" | "NEGATIVE" | "NEUTRAL" | "MIXED";
  sentimentScore: number;
  credibility: number;
  aiSignal: string;
  keywords: string[];
  risks: string[];
  opportunities: string[];
  impactScore: number;
  explanation: string;
}

export interface FailedPrediction {
  id: string;
  symbol: string;
  predicted: string;
  actual: string;
  date: string;
  rootCause: string;
  lesson: string;
  accuracy: number;
  deviation: number;
}

export interface SimulatorResult {
  predictedPrice: number;
  confidence: number;
  action: string;
  riskLevel: string;
  riskScore: number;
  chartData: { time: string; predicted: number; lower: number; upper: number }[];
}

// ── Generate Price History ──
function generatePriceHistory(basePrice: number, points = 24) {
  const data = [];
  let price = basePrice;
  for (let i = 0; i < points; i++) {
    price += (Math.random() - 0.48) * basePrice * 0.008;
    data.push({
      time: `${String(i).padStart(2, "0")}:00`,
      price: parseFloat(price.toFixed(2)),
      volume: Math.floor(Math.random() * 5000000 + 1000000),
    });
  }
  return data;
}

// ── Generate Trend Charts ──
function generateTrendCharts(basePrice: number, points = 30) {
  const data = [];
  let price = basePrice;
  for (let i = 0; i < points; i++) {
    price += (Math.random() - 0.47) * basePrice * 0.01;
    const lstmPred = price + (Math.random() - 0.5) * basePrice * 0.02;
    data.push({
      date: `Day ${i + 1}`,
      lstm: parseFloat(lstmPred.toFixed(2)),
      actual: parseFloat(price.toFixed(2)),
      sentiment: parseFloat((Math.random() * 0.4 + 0.3).toFixed(3)),
    });
  }
  return data;
}

// ── Stock Data ──
export const STOCKS: Record<string, StockAnalysis> = {
  RELIANCE: {
    symbol: "RELIANCE",
    name: "Reliance Industries",
    price: 2847.65,
    change: 42.3,
    changePercent: 1.51,
    volume: 12450000,
    marketCap: "₹19.2L Cr",
    signal: "STRONG BUY",
    confidence: 87.4,
    trustScore: 92,
    lstmPrediction: 2912.0,
    finbertSentiment: 0.78,
    anomalyScore: 0.12,
    bayesianFusion: 0.85,
    aiDecision: "ACCUMULATE — Strong upward momentum with institutional backing",
    aiExplanation:
      "LSTM model predicts 2.3% upside in 5 days. FinBERT sentiment is highly positive due to Jio platform expansion news. Bayesian fusion of technical and fundamental signals confirms bullish outlook. Low anomaly score indicates stable pattern.",
    contradiction: false,
    priceHistory: generatePriceHistory(2847.65),
    featureImportance: [
      { feature: "LSTM Momentum", importance: 0.32 },
      { feature: "News Sentiment", importance: 0.24 },
      { feature: "Volume Surge", importance: 0.18 },
      { feature: "RSI Signal", importance: 0.14 },
      { feature: "Sector Trend", importance: 0.12 },
    ],
    sentimentSummary:
      "Strong positive sentiment across financial media. Jio expansion and refining margin improvement dominate discourse.",
    trendCharts: generateTrendCharts(2847.65),
  },
  TCS: {
    symbol: "TCS",
    name: "Tata Consultancy Services",
    price: 3654.2,
    change: -28.45,
    changePercent: -0.77,
    volume: 5830000,
    marketCap: "₹13.4L Cr",
    signal: "HOLD",
    confidence: 62.1,
    trustScore: 78,
    lstmPrediction: 3640.0,
    finbertSentiment: 0.45,
    anomalyScore: 0.28,
    bayesianFusion: 0.52,
    aiDecision: "HOLD — Mixed signals with moderate uncertainty",
    aiExplanation:
      "LSTM shows slight downward pressure. FinBERT sentiment neutral — Q4 results in line but guidance cautious. Higher anomaly score suggests unusual trading patterns. Bayesian fusion indicates wait-and-watch.",
    contradiction: true,
    contradictionDetails:
      "LSTM bearish (-0.4%) conflicts with positive sector momentum (+1.2%). Volume profile suggests institutional accumulation despite price weakness.",
    priceHistory: generatePriceHistory(3654.2),
    featureImportance: [
      { feature: "Earnings Impact", importance: 0.28 },
      { feature: "LSTM Signal", importance: 0.22 },
      { feature: "Sector Correlation", importance: 0.2 },
      { feature: "FII Flow", importance: 0.17 },
      { feature: "Volatility", importance: 0.13 },
    ],
    sentimentSummary:
      "Neutral to slightly cautious. Q4 results met expectations but management guidance for FY27 was conservative.",
    trendCharts: generateTrendCharts(3654.2),
  },
  INFY: {
    symbol: "INFY",
    name: "Infosys Limited",
    price: 1542.8,
    change: 18.9,
    changePercent: 1.24,
    volume: 8920000,
    marketCap: "₹6.4L Cr",
    signal: "BUY",
    confidence: 74.8,
    trustScore: 85,
    lstmPrediction: 1580.0,
    finbertSentiment: 0.65,
    anomalyScore: 0.15,
    bayesianFusion: 0.72,
    aiDecision: "BUY — Positive momentum with deal pipeline strength",
    aiExplanation:
      "LSTM predicts 2.4% upside. Strong deal wins reported in digital transformation space. FinBERT positivity driven by large contract announcements. Low anomaly score confirms stable trend.",
    contradiction: false,
    priceHistory: generatePriceHistory(1542.8),
    featureImportance: [
      { feature: "Deal Pipeline", importance: 0.3 },
      { feature: "LSTM Trend", importance: 0.25 },
      { feature: "Currency Impact", importance: 0.18 },
      { feature: "Attrition Data", importance: 0.15 },
      { feature: "Market Breadth", importance: 0.12 },
    ],
    sentimentSummary:
      "Positive sentiment. Large deal announcements and digital transformation wins boosting investor confidence.",
    trendCharts: generateTrendCharts(1542.8),
  },
  HDFCBANK: {
    symbol: "HDFCBANK",
    name: "HDFC Bank Limited",
    price: 1678.45,
    change: -12.3,
    changePercent: -0.73,
    volume: 15600000,
    marketCap: "₹12.8L Cr",
    signal: "SELL",
    confidence: 71.2,
    trustScore: 68,
    lstmPrediction: 1645.0,
    finbertSentiment: 0.32,
    anomalyScore: 0.45,
    bayesianFusion: 0.38,
    aiDecision: "REDUCE — Bearish signals with NPA concerns",
    aiExplanation:
      "LSTM predicts further 2% downside. FinBERT negative due to rising NPA concerns and RBI commentary. High anomaly score flags unusual selling patterns. Bayesian fusion strongly bearish.",
    contradiction: false,
    priceHistory: generatePriceHistory(1678.45),
    featureImportance: [
      { feature: "NPA Trend", importance: 0.35 },
      { feature: "LSTM Momentum", importance: 0.22 },
      { feature: "RBI Policy", importance: 0.2 },
      { feature: "Credit Growth", importance: 0.13 },
      { feature: "Yield Curve", importance: 0.1 },
    ],
    sentimentSummary:
      "Negative sentiment. Rising NPA concerns and hawkish RBI commentary weighing on banking sector outlook.",
    trendCharts: generateTrendCharts(1678.45),
  },
  TATAMOTORS: {
    symbol: "TATAMOTORS",
    name: "Tata Motors Limited",
    price: 892.35,
    change: 35.2,
    changePercent: 4.11,
    volume: 22100000,
    marketCap: "₹3.3L Cr",
    signal: "STRONG BUY",
    confidence: 91.3,
    trustScore: 94,
    lstmPrediction: 945.0,
    finbertSentiment: 0.89,
    anomalyScore: 0.08,
    bayesianFusion: 0.92,
    aiDecision: "STRONG BUY — JLR margins + EV momentum = breakout imminent",
    aiExplanation:
      "LSTM predicts 5.9% surge. FinBERT extremely positive — JLR margin expansion and EV order book strength. Lowest anomaly score in portfolio. Bayesian fusion at near-maximum conviction.",
    contradiction: false,
    priceHistory: generatePriceHistory(892.35),
    featureImportance: [
      { feature: "JLR Margins", importance: 0.33 },
      { feature: "EV Orders", importance: 0.27 },
      { feature: "LSTM Prediction", importance: 0.2 },
      { feature: "Volume Breakout", importance: 0.12 },
      { feature: "Sector Rotation", importance: 0.08 },
    ],
    sentimentSummary:
      "Extremely positive. JLR margin expansion surprise and strong EV booking numbers creating massive investor enthusiasm.",
    trendCharts: generateTrendCharts(892.35),
  },
};

export const STOCK_LIST = Object.values(STOCKS);

// ── Top Movers ──
export const TOP_MOVERS = [
  { symbol: "TATAMOTORS", change: 4.11, price: 892.35 },
  { symbol: "ADANIENT", change: 3.82, price: 2456.7 },
  { symbol: "RELIANCE", change: 1.51, price: 2847.65 },
  { symbol: "INFY", change: 1.24, price: 1542.8 },
  { symbol: "BAJFINANCE", change: -2.34, price: 6891.2 },
  { symbol: "HDFCBANK", change: -0.73, price: 1678.45 },
];

// ── Portfolio Mock ──
export const MOCK_PORTFOLIO: PortfolioData = {
  totalValue: 12847.5,
  cashBalance: 2847.5,
  investedValue: 10000.0,
  totalPnl: 2847.5,
  totalPnlPercent: 28.47,
  roi: 28.47,
  holdings: [
    {
      symbol: "RELIANCE",
      name: "Reliance Industries",
      shares: 2,
      avgPrice: 2780.0,
      currentPrice: 2847.65,
      pnl: 135.3,
      pnlPercent: 2.43,
      value: 5695.3,
    },
    {
      symbol: "INFY",
      name: "Infosys Limited",
      shares: 3,
      avgPrice: 1480.0,
      currentPrice: 1542.8,
      pnl: 188.4,
      pnlPercent: 4.24,
      value: 4628.4,
    },
    {
      symbol: "TCS",
      name: "Tata Consultancy",
      shares: 1,
      avgPrice: 3600.0,
      currentPrice: 3654.2,
      pnl: 54.2,
      pnlPercent: 1.51,
      value: 3654.2,
    },
  ],
  tradeHistory: [
    {
      id: "TRD001",
      symbol: "RELIANCE",
      action: "BUY",
      shares: 2,
      price: 2780.0,
      total: 5560.0,
      timestamp: "2026-04-20T10:30:00Z",
      status: "COMPLETED",
    },
    {
      id: "TRD002",
      symbol: "INFY",
      action: "BUY",
      shares: 3,
      price: 1480.0,
      total: 4440.0,
      timestamp: "2026-04-19T14:15:00Z",
      status: "COMPLETED",
    },
    {
      id: "TRD003",
      symbol: "TATAMOTORS",
      action: "SELL",
      shares: 5,
      price: 856.0,
      total: 4280.0,
      timestamp: "2026-04-18T11:45:00Z",
      status: "COMPLETED",
    },
    {
      id: "TRD004",
      symbol: "TCS",
      action: "BUY",
      shares: 1,
      price: 3600.0,
      total: 3600.0,
      timestamp: "2026-04-17T09:20:00Z",
      status: "COMPLETED",
    },
    {
      id: "TRD005",
      symbol: "HDFCBANK",
      action: "SELL",
      shares: 4,
      price: 1695.0,
      total: 6780.0,
      timestamp: "2026-04-16T15:30:00Z",
      status: "COMPLETED",
    },
  ],
  allocation: [
    { name: "RELIANCE", value: 40, color: "#06B6D4" },
    { name: "INFY", value: 33, color: "#22C55E" },
    { name: "TCS", value: 27, color: "#A855F7" },
  ],
};

// ── Blockchain Logs ──
export const MOCK_BLOCKCHAIN_LOGS: BlockchainLog[] = [
  {
    id: "BLK001",
    txHash: "0xa4f2e8c9d1b3f6a7e5c2d8b9f4a1e3c7d6b8a2f5e1c9d3b7a4f8e2c6d1b5a9",
    prediction: "RELIANCE → BUY @ ₹2,912",
    symbol: "RELIANCE",
    confidence: 87.4,
    timestamp: "2026-04-22T14:32:00Z",
    status: "VERIFIED",
    blockNumber: 18947231,
    nftMinted: true,
    trustChainScore: 94,
  },
  {
    id: "BLK002",
    txHash: "0xb7d1e3f5a9c2d8b4f6a1e7c3d9b5a8f2e4c6d1b3a7f9e5c2d8b4f6a1e3c7d9",
    prediction: "TCS → HOLD @ ₹3,640",
    symbol: "TCS",
    confidence: 62.1,
    timestamp: "2026-04-22T13:15:00Z",
    status: "VERIFIED",
    blockNumber: 18947198,
    nftMinted: false,
    trustChainScore: 78,
  },
  {
    id: "BLK003",
    txHash: "0xc9f2a4d6b8e1c3f5a7d9b2e4c6f8a1d3b5e7c9f2a4d6b8e1c3f5a7d9b2e4c6",
    prediction: "TATAMOTORS → STRONG BUY @ ₹945",
    symbol: "TATAMOTORS",
    confidence: 91.3,
    timestamp: "2026-04-22T12:00:00Z",
    status: "VERIFIED",
    blockNumber: 18947156,
    nftMinted: true,
    trustChainScore: 96,
  },
  {
    id: "BLK004",
    txHash: "0xd1e3f5a7c9b2d4f6a8e1c3d5b7f9a2e4c6d8b1f3a5e7c9d2b4f6a8e1c3d5b7",
    prediction: "HDFCBANK → SELL @ ₹1,645",
    symbol: "HDFCBANK",
    confidence: 71.2,
    timestamp: "2026-04-22T10:45:00Z",
    status: "PENDING",
    blockNumber: 18947112,
    nftMinted: false,
    trustChainScore: 65,
  },
  {
    id: "BLK005",
    txHash: "0xe5a7c9d1f3b2e4d6a8c1f3b5d7e9a2c4f6b8d1e3a5c7f9b2d4e6a8c1f3b5d7",
    prediction: "INFY → BUY @ ₹1,580",
    symbol: "INFY",
    confidence: 74.8,
    timestamp: "2026-04-22T09:30:00Z",
    status: "VERIFIED",
    blockNumber: 18947089,
    nftMinted: true,
    trustChainScore: 88,
  },
];

// ── Failed Predictions ──
export const MOCK_FAILED_PREDICTIONS: FailedPrediction[] = [
  {
    id: "FP001",
    symbol: "ADANIENT",
    predicted: "BUY — Price target ₹2,800",
    actual: "Price dropped to ₹2,340 (-16.4%)",
    date: "2026-03-15",
    rootCause: "Unexpected regulatory investigation announcement. Black swan event not captured by sentiment analysis.",
    lesson: "Incorporate regulatory risk scoring and insider activity detection.",
    accuracy: 23.6,
    deviation: -16.4,
  },
  {
    id: "FP002",
    symbol: "PAYTM",
    predicted: "HOLD — Stability expected",
    actual: "Sharp decline to ₹320 (-22.1%)",
    date: "2026-02-28",
    rootCause: "RBI action on Paytm Payments Bank. Regulatory risk model failed to flag severity.",
    lesson: "Weight regulatory news higher for fintech stocks. Add RBI circular monitoring.",
    accuracy: 18.9,
    deviation: -22.1,
  },
  {
    id: "FP003",
    symbol: "TATASTEEL",
    predicted: "STRONG BUY — Commodity cycle peak",
    actual: "Sideways movement, +0.8% only",
    date: "2026-03-01",
    rootCause: "Global steel demand softened. China stimulus was weaker than expected.",
    lesson: "Integrate global macro indicators more heavily for commodity stocks.",
    accuracy: 62.4,
    deviation: -4.2,
  },
  {
    id: "FP004",
    symbol: "ZOMATO",
    predicted: "SELL — Profitability concerns",
    actual: "Price surged +18.3% on Blinkit growth",
    date: "2026-01-20",
    rootCause: "Quick commerce segment growth outpaced expectations. Model underweighted segment data.",
    lesson: "Include segment-level revenue analysis for platform companies.",
    accuracy: 31.7,
    deviation: 18.3,
  },
];

// ── Accuracy Timeline ──
export const ACCURACY_TIMELINE = [
  { month: "Oct", accuracy: 68 },
  { month: "Nov", accuracy: 72 },
  { month: "Dec", accuracy: 69 },
  { month: "Jan", accuracy: 75 },
  { month: "Feb", accuracy: 71 },
  { month: "Mar", accuracy: 78 },
  { month: "Apr", accuracy: 82 },
];

// ── Heatmap Data ──
export const HEATMAP_DATA = [
  { sector: "IT", mon: 3, tue: 1, wed: 2, thu: 0, fri: 1 },
  { sector: "Banking", mon: 2, tue: 3, wed: 1, thu: 2, fri: 0 },
  { sector: "Auto", mon: 0, tue: 1, wed: 1, thu: 0, fri: 2 },
  { sector: "Pharma", mon: 1, tue: 0, wed: 2, thu: 1, fri: 1 },
  { sector: "Energy", mon: 1, tue: 2, wed: 0, thu: 1, fri: 0 },
];
