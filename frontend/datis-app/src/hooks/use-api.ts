import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  STOCKS,
  MOCK_PORTFOLIO,
  MOCK_BLOCKCHAIN_LOGS,
  MOCK_FAILED_PREDICTIONS,
  ACCURACY_TIMELINE,
  type StockAnalysis,
  type PortfolioData,
  type BlockchainLog,
  type SocialAnalysisResult,
  type FailedPrediction,
  type SimulatorResult,
} from "@/lib/mock-data";

const BASE_URL = "http://localhost:8000";

const COMPANY_NAMES: Record<string, string> = {
  AAPL: "Apple Inc.",
  TSLA: "Tesla Inc.",
  NVDA: "NVIDIA Corporation",
  MSFT: "Microsoft Corporation",
  GOOGL: "Alphabet Inc.",
  RELIANCE: "Reliance Industries",
  TCS: "Tata Consultancy Services",
  INFY: "Infosys",
  HDFCBANK: "HDFC Bank",
  ICICIBANK: "ICICI Bank",
};

async function fetchWithFallback<T>(url: string, fallback: T): Promise<T> {
  try {
    const res = await fetch(url);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn("Backend fallback used:", url, err);
    return fallback;
  }
}

function mapPredictToStockAnalysis(api: any, fallback: StockAnalysis): StockAnalysis {
  if (!api?.success) return fallback;

  const symbol = String(api.symbol ?? fallback.symbol).toUpperCase();
  const action = api.fusion?.action ?? api.price?.label ?? "HOLD";
  const confidence = (api.fusion?.confidence ?? api.price?.confidence ?? 0) * 100;
  const lastClose = api.price?.last_close ?? fallback.price;
  const predictedClose = api.price?.predicted_close ?? lastClose;
  const changePct = api.price?.change_pct ?? 0;

  return {
    ...fallback,
    symbol,
    name: COMPANY_NAMES[symbol] ?? symbol,
    price: lastClose,
    change: predictedClose - lastClose,
    changePercent: changePct,
    signal: action,
    confidence,
    aiDecision: `${action} — ${api.fusion?.reason ?? "AI fusion decision"}`,
    trustScore: Math.round(confidence),
    finbertSentiment: api.sentiment?.positive ?? fallback.finbertSentiment,
    anomalyScore: api.anomaly?.anomaly_score ?? fallback.anomalyScore,
    bayesianFusion: api.fusion?.confidence ?? fallback.bayesianFusion,
    sentimentSummary: `Live sentiment: ${api.sentiment?.label ?? "neutral"} | Positive ${api.sentiment?.positive ?? 0}, Negative ${api.sentiment?.negative ?? 0}`,
    aiExplanation: api.fusion?.reason ?? fallback.aiExplanation,
    contradiction: (api.contradictions?.length ?? 0) > 0,
    contradictionDetails: api.contradictions?.join(", ") ?? "",
  };
}

function mapPortfolio(api: any): PortfolioData {
  const holdings = (api.holdings ?? []).map((h: any) => {
    const symbol = String(h.symbol ?? "").toUpperCase();
    const avg = Number(h.avg_price ?? h.avgPrice ?? 0);
    const shares = Number(h.shares ?? 0);
    const value = avg * shares;

    return {
      symbol,
      name: COMPANY_NAMES[symbol] ?? symbol,
      shares,
      avgPrice: avg,
      currentPrice: avg,
      value,
      pnl: 0,
      pnlPercent: 0,
    };
  });

  const totalValue = Number(api.total_value ?? 10000);
  const cashBalance = Number(api.cash ?? 10000);
  const totalPnl = Number(api.pnl ?? 0);

  return {
    totalValue,
    cashBalance,
    totalPnl,
    totalPnlPercent: Number(api.pnl_pct ?? 0),
    roi: Number(api.pnl_pct ?? 0),
    investedValue: holdings.reduce((sum: number, h: any) => sum + h.value, 0),
    holdings,
    allocation: holdings.map((h: any, i: number) => ({
      name: h.symbol,
      value: totalValue ? Math.round((h.value / totalValue) * 100) : 0,
      color: ["#06B6D4", "#22C55E", "#A855F7", "#F59E0B", "#EF4444"][i % 5],
    })),
    tradeHistory: (api.trade_history ?? []).map((t: any) => ({
      id: t.id,
      symbol: t.symbol,
      action: t.action,
      shares: Number(t.shares),
      price: Number(t.price),
      total: Number(t.total),
      timestamp: t.timestamp,
      status: "EXECUTED",
    })),
  };
}

export function useGetStockAnalysis(symbol: string) {
  const cleanSymbol = symbol.toUpperCase().trim();

  return useQuery<StockAnalysis>({
    queryKey: ["stock-analysis", cleanSymbol],
    queryFn: async () => {
      const fallback = STOCKS[cleanSymbol] ?? STOCKS.RELIANCE;
      const api = await fetchWithFallback(`${BASE_URL}/api/predict/${cleanSymbol}`, null);
      return mapPredictToStockAnalysis(api, fallback);
    },
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useGetAllStocks() {
  return useQuery<StockAnalysis[]>({
    queryKey: ["all-stocks"],
    queryFn: () => Promise.resolve(Object.values(STOCKS)),
    staleTime: 30000,
  });
}

export function useGetPrediction(params: {
  sentiment: number;
  volatility: number;
  newsImpact: number;
  volume: number;
  timeHorizon: number;
}) {
  return useQuery<SimulatorResult>({
    queryKey: ["prediction", params],
    queryFn: async () => {
      const api = await fetchWithFallback(`${BASE_URL}/api/whatif/AAPL?sentiment_shift=0`, null);

      const price = api?.price?.predicted_close ?? 150;
      const confidence = (api?.fusion?.confidence ?? 0.5) * 100;

      return {
        predictedPrice: price,
        confidence,
        action: api?.fusion?.action ?? "HOLD",
        riskLevel: api?.anomaly?.risk_level?.toUpperCase?.() ?? "LOW",
        riskScore: Math.round((api?.anomaly?.anomaly_score ?? 0.2) * 100),
        chartData: Array.from({ length: params.timeHorizon + 1 }, (_, i) => ({
          time: `Day ${i}`,
          predicted: price + i * 2,
          lower: price + i,
          upper: price + i * 3,
        })),
      };
    },
    enabled: false,
  });
}

export function useGetPortfolio() {
  return useQuery<PortfolioData>({
    queryKey: ["portfolio"],
    queryFn: async () => {
      const api = await fetchWithFallback(`${BASE_URL}/api/portfolio/`, null);
      return api ? mapPortfolio(api) : MOCK_PORTFOLIO;
    },
    refetchInterval: 10000,
    staleTime: 5000,
  });
}

export function useExecuteTrade() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (trade: {
      symbol: string;
      action: "BUY" | "SELL" | "HOLD";
      shares: number;
      price: number;
    }) => {
      const res = await fetch(`${BASE_URL}/api/portfolio/trade`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(trade),
      });

      if (!res.ok) throw new Error("Trade failed");
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["portfolio"] });
    },
  });
}

export function useGetBlockchainLogs() {
  return useQuery<BlockchainLog[]>({
    queryKey: ["blockchain-logs"],
    queryFn: async () => {
      await fetchWithFallback(`${BASE_URL}/api/blockchain/wallet`, null);
      return MOCK_BLOCKCHAIN_LOGS;
    },
    staleTime: 30000,
  });
}

export function usePostSocialAnalysis() {
  return useMutation<SocialAnalysisResult, Error, { text: string; symbol?: string }>({
    mutationFn: async ({ text, symbol = "AAPL" }) => {
      const res = await fetch(
        `${BASE_URL}/api/sentiment/${symbol}?text=${encodeURIComponent(text)}`
      );

      if (!res.ok) throw new Error("Sentiment failed");

      const api = await res.json();

      return {
        sentiment: api.label?.toUpperCase?.() ?? "NEUTRAL",
        sentimentScore: api.positive ?? 0.5,
        credibility: 80,
        aiSignal: `Model used: ${api.model_used}`,
        keywords: extractKeywords(text),
        risks: ["Market volatility may impact short-term price action"],
        opportunities: ["Positive sentiment may support upside momentum"],
        impactScore: Math.round((api.positive ?? 0.5) * 100),
        explanation: `Positive: ${api.positive}, Neutral: ${api.neutral}, Negative: ${api.negative}`,
      };
    },
  });
}

function extractKeywords(text: string): string[] {
  const words = text.toLowerCase().split(/\s+/);
  const keywords = [
    "market", "stock", "trading", "bullish", "bearish", "growth", "profit",
    "loss", "revenue", "earnings", "dividend", "investment", "rally", "crash",
    "buy", "sell", "momentum", "volatility", "inflation", "rate",
  ];
  const found = words.filter((w) => keywords.includes(w));
  return found.length > 0 ? [...new Set(found)].slice(0, 6) : ["market", "analysis", "signal"];
}

export function useGetFailedPredictions() {
  return useQuery<FailedPrediction[]>({
    queryKey: ["failed-predictions"],
    queryFn: () =>
      fetchWithFallback(
        `${BASE_URL}/api/failure/AAPL?expected_action=BUY`,
        MOCK_FAILED_PREDICTIONS as any
      ),
    staleTime: 60000,
  });
}

export function useGetAccuracyTimeline() {
  return useQuery({
    queryKey: ["accuracy-timeline"],
    queryFn: () => Promise.resolve(ACCURACY_TIMELINE),
    staleTime: 60000,
  });
}