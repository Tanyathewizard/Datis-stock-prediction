import { useState } from "react";
import { useLocation } from "wouter";
import {
  Brain,
  TrendingUp,
  TrendingDown,
  Shield,
  Gauge,
  AlertTriangle,
  MessageSquare,
  Zap,
  ArrowUpRight,
  Activity,
  BarChart3,
  Link2,
  Loader2,
  MinusCircle,
  PlusCircle,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from "recharts";
import { cn } from "@/lib/utils";
import { useGetStockAnalysis, useExecuteTrade } from "@/hooks/use-api";
import {
  MetricCard,
  SignalBadge,
  ChartCard,
  ProgressRing,
} from "@/components/ui-cards";
import { TOP_MOVERS } from "@/lib/mock-data";

interface DashboardProps {
  selectedSymbol: string;
}

const BASE_URL = "http://localhost:8000";

export default function Dashboard({ selectedSymbol }: DashboardProps) {
  const {
    data: stock,
    isLoading,
    isError,
    refetch,
  } = useGetStockAnalysis(selectedSymbol);

  const tradeMutation = useExecuteTrade();
  const [, navigate] = useLocation();

  const [shares, setShares] = useState("1");
  const [tradeStatus, setTradeStatus] = useState("");
  const [blockchainStatus, setBlockchainStatus] = useState("");

  const handleSharesChange = (value: string) => {
    const clean = value.replace(/^0+(?=\d)/, "");
    setShares(clean || "1");
  };

  if (isLoading) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="glass-card rounded-2xl p-8 text-center">
          <Loader2 className="w-10 h-10 text-datis-cyan animate-spin mx-auto mb-4" />
          <h2 className="text-xl font-display font-bold text-datis-text">
            Analyzing Market...
          </h2>
          <p className="text-sm text-datis-text-muted mt-2">
            Fetching AI prediction, live sentiment, anomaly risk and fusion
            result.
          </p>
        </div>
      </div>
    );
  }

  if (isError || !stock) {
    return (
      <div className="min-h-[70vh] flex items-center justify-center">
        <div className="glass-card rounded-2xl p-8 text-center border border-datis-red/30">
          <AlertTriangle className="w-10 h-10 text-datis-red mx-auto mb-4" />
          <h2 className="text-xl font-display font-bold text-datis-text">
            Unable to analyze symbol
          </h2>
          <p className="text-sm text-datis-text-muted mt-2">
            Please check the stock symbol or backend server.
          </p>
          <button
            onClick={() => refetch()}
            className="mt-5 px-5 py-3 rounded-xl bg-datis-red/10 border border-datis-red/30 text-datis-red font-display font-bold text-sm"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  const action = stock.signal;
  const isBuy = action.includes("BUY");
  const isSell = action.includes("SELL");

  const executeTrade = (tradeAction: "BUY" | "SELL") => {
    const qty = Math.max(1, Number(shares || "0"));

    setTradeStatus(`${tradeAction} order processing...`);
    setBlockchainStatus("");

    tradeMutation.mutate(
      {
        symbol: selectedSymbol,
        action: tradeAction,
        shares: qty,
        price: stock.price,
      },
      {
        onSuccess: () => {
          setTradeStatus(
            `${tradeAction} executed: ${qty} shares of ${selectedSymbol}`
          );
        },
        onError: () => {
          setTradeStatus(`${tradeAction} failed. Check cash/holdings.`);
        },
      }
    );
  };

  const handleStoreBlockchain = async () => {
    try {
      setBlockchainStatus("Storing prediction...");
      setTradeStatus("");

      const res = await fetch(`${BASE_URL}/api/blockchain/store`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prediction: stock.signal,
          symbol: selectedSymbol,
          confidence: Math.round(stock.confidence),
          price: stock.price,
        }),
      });

      if (!res.ok) {
        throw new Error("Failed to store prediction");
      }

      const data = await res.json();

      setBlockchainStatus(
        data?.token_id ? `Stored: ${data.token_id}` : "Stored successfully"
      );
    } catch {
      setBlockchainStatus("Blockchain store failed");
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="glass-card rounded-3xl p-8 border border-datis-cyan/10 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-datis-cyan/10 via-transparent to-datis-purple/10 pointer-events-none" />

        <div className="relative grid grid-cols-12 gap-6 items-center">
          <div className="col-span-8">
            <p className="text-xs font-display font-bold uppercase tracking-[0.3em] text-datis-cyan mb-3">
              DATIS AI Trading Intelligence
            </p>

            <h1 className="text-5xl font-display font-black text-datis-text tracking-tight">
              {selectedSymbol}
              <span
                className={cn(
                  "ml-4",
                  isBuy
                    ? "text-datis-green"
                    : isSell
                      ? "text-datis-red"
                      : "text-datis-amber"
                )}
              >
                {stock.signal}
              </span>
            </h1>

            <p className="text-sm text-datis-text-muted mt-4 max-w-3xl leading-relaxed">
              {stock.aiDecision}
            </p>

            <div className="flex flex-wrap items-center gap-3 mt-6">
              <div className="flex items-center gap-2 px-3 py-2 rounded-xl bg-datis-bg/70 border border-datis-border">
                <span className="text-xs text-datis-text-muted font-display uppercase">
                  Shares
                </span>
                <input
                  type="number"
                  min={1}
                  value={shares}
                  onChange={(e) => handleSharesChange(e.target.value)}
                  className="w-20 bg-transparent text-datis-text font-data outline-none text-sm"
                />
              </div>

              <button
                onClick={() => executeTrade("BUY")}
                disabled={tradeMutation.isPending}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-datis-green/10 border border-datis-green/30 text-datis-green font-display font-bold text-sm hover:bg-datis-green/15 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <PlusCircle className="w-4 h-4" />
                BUY
              </button>

              <button
                onClick={() => executeTrade("SELL")}
                disabled={tradeMutation.isPending}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-datis-red/10 border border-datis-red/30 text-datis-red font-display font-bold text-sm hover:bg-datis-red/15 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <MinusCircle className="w-4 h-4" />
                SELL
              </button>

              <button
                onClick={handleStoreBlockchain}
                className="flex items-center gap-2 px-5 py-3 rounded-xl bg-datis-purple/10 border border-datis-purple/30 text-datis-purple font-display font-bold text-sm hover:bg-datis-purple/15 transition-all"
              >
                <Link2 className="w-4 h-4" />
                Store Prediction
              </button>

              {(tradeStatus || blockchainStatus) && (
                <span className="px-4 py-3 rounded-xl bg-datis-bg/70 border border-datis-border text-xs font-data text-datis-text-secondary">
                  {tradeStatus || blockchainStatus}
                </span>
              )}
            </div>
          </div>

          <div className="col-span-4 flex justify-center">
            <ProgressRing
              value={stock.confidence}
              color={isBuy ? "#22C55E" : isSell ? "#EF4444" : "#F59E0B"}
              label="Confidence"
              size={180}
              strokeWidth={12}
            />
          </div>
        </div>
      </div>

      <div className="flex items-end justify-between">
        <div>
          <h2 className="text-2xl font-display font-bold text-datis-text tracking-tight">
            Market Intelligence
          </h2>
          <p className="text-sm text-datis-text-muted mt-1 font-sans">
            AI-powered real-time analysis for {stock.name}
          </p>
        </div>

        <div className="glass-card px-4 py-2 rounded-xl flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-datis-green" />
          <span className="font-data text-xs text-datis-text-secondary">
            Live Backend Connected
          </span>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          title="AI Decision"
          value={stock.signal}
          subtitle={stock.aiDecision.split("—")[0]}
          icon={Brain}
          glowColor={isBuy ? "green" : isSell ? "red" : "amber"}
        />

        <MetricCard
          title="Live Price"
          value={`₹${stock.price.toFixed(2)}`}
          icon={stock.change >= 0 ? TrendingUp : TrendingDown}
          trend={stock.change >= 0 ? "up" : "down"}
          trendValue={`${stock.change >= 0 ? "+" : ""}${stock.changePercent.toFixed(2)}%`}
          glowColor={stock.change >= 0 ? "green" : "red"}
        />

        <MetricCard
          title="Trust Score"
          value={`${stock.trustScore}/100`}
          icon={Shield}
          trend={
            stock.trustScore > 80
              ? "up"
              : stock.trustScore > 60
                ? "neutral"
                : "down"
          }
          trendValue={
            stock.trustScore > 80
              ? "High"
              : stock.trustScore > 60
                ? "Medium"
                : "Low"
          }
          glowColor={
            stock.trustScore > 80
              ? "green"
              : stock.trustScore > 60
                ? "amber"
                : "red"
          }
        />

        <MetricCard
          title="Confidence"
          value={`${stock.confidence.toFixed(1)}%`}
          icon={Gauge}
          subtitle="Bayesian Fusion"
          glowColor="cyan"
        />

        <MetricCard
          title="Volume"
          value={`${(stock.volume / 1e6).toFixed(1)}M`}
          icon={BarChart3}
          subtitle={stock.marketCap}
          glowColor="purple"
        />
      </div>

      <div className="grid grid-cols-12 gap-4">
        <ChartCard
          title={`${stock.symbol} Price Chart`}
          subtitle="24H Intraday • Real-time"
          className="col-span-8"
        >
          <ResponsiveContainer width="100%" height={280}>
            <AreaChart data={stock.priceHistory}>
              <defs>
                <linearGradient id="priceGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#06B6D4" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="rgba(255,255,255,0.04)"
              />
              <XAxis
                dataKey="time"
                tick={{ fontSize: 10, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fontSize: 10, fill: "#6B7280" }}
                axisLine={false}
                tickLine={false}
                domain={["auto", "auto"]}
              />
              <Tooltip
                contentStyle={{
                  background: "rgba(17, 24, 39, 0.95)",
                  border: "1px solid rgba(6, 182, 212, 0.3)",
                  borderRadius: "12px",
                }}
              />
              <Area
                type="monotone"
                dataKey="price"
                stroke="#06B6D4"
                strokeWidth={2}
                fill="url(#priceGrad)"
                name="Price"
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        <div className="col-span-4 space-y-4">
          <div className="glass-card rounded-xl p-5 flex flex-col items-center justify-center text-center">
            <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-4">
              Trust Score
            </span>
            <ProgressRing
              value={stock.trustScore}
              color={
                stock.trustScore > 80
                  ? "#22C55E"
                  : stock.trustScore > 60
                    ? "#F59E0B"
                    : "#EF4444"
              }
              label={
                stock.trustScore > 80
                  ? "High"
                  : stock.trustScore > 60
                    ? "Medium"
                    : "Low"
              }
              size={140}
              strokeWidth={10}
            />
            <p className="text-xs text-datis-text-muted mt-4 px-2 leading-relaxed">
              {stock.sentimentSummary.slice(0, 120)}...
            </p>
            <div className="flex gap-2 mt-3">
              <SignalBadge signal={stock.signal} size="sm" />
              {stock.contradiction && (
                <SignalBadge signal="⚠ CONFLICT" size="sm" />
              )}
            </div>
          </div>

          <ChartCard title="Volume Profile" subtitle="24H Distribution">
            <ResponsiveContainer width="100%" height={100}>
              <BarChart data={stock.priceHistory.slice(-12)}>
                <Bar
                  dataKey="volume"
                  fill="#A855F7"
                  radius={[4, 4, 0, 0]}
                  opacity={0.7}
                />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-4">
          <div
            className={cn(
              "glass-card rounded-xl p-5",
              stock.contradiction && "border-datis-amber/30"
            )}
          >
            <div className="flex items-center gap-2 mb-3">
              <AlertTriangle
                className={cn(
                  "w-4 h-4",
                  stock.contradiction ? "text-datis-amber" : "text-datis-green"
                )}
              />
              <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                Contradiction Alert
              </span>
            </div>

            {stock.contradiction ? (
              <>
                <SignalBadge
                  signal="CONFLICT DETECTED"
                  size="sm"
                  className="mb-2"
                />
                <p className="text-sm text-datis-amber/80 leading-relaxed">
                  {stock.contradictionDetails}
                </p>
              </>
            ) : (
              <>
                <SignalBadge signal="ALL CLEAR" size="sm" className="mb-2" />
                <p className="text-sm text-datis-green/80 leading-relaxed">
                  All AI models are in agreement. No conflicting signals
                  detected.
                </p>
              </>
            )}
          </div>
        </div>

        <div className="col-span-4">
          <div className="glass-card rounded-xl p-5 h-full">
            <div className="flex items-center gap-2 mb-3">
              <MessageSquare className="w-4 h-4 text-datis-cyan" />
              <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                Sentiment Summary
              </span>
            </div>
            <p className="text-sm text-datis-text-secondary leading-relaxed">
              {stock.sentimentSummary}
            </p>
            <div className="mt-3 flex items-center gap-3">
              <div className="flex-1 bg-datis-border/30 rounded-full h-1.5 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-datis-cyan to-datis-green transition-all duration-700"
                  style={{ width: `${stock.finbertSentiment * 100}%` }}
                />
              </div>
              <span className="font-data text-xs text-datis-cyan">
                {(stock.finbertSentiment * 100).toFixed(0)}%
              </span>
            </div>
          </div>
        </div>

        <div className="col-span-4">
          <div className="glass-card rounded-xl p-5 h-full">
            <div className="flex items-center gap-2 mb-3">
              <Zap className="w-4 h-4 text-datis-amber" />
              <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                Top Movers
              </span>
            </div>
            <div className="space-y-2">
              {TOP_MOVERS.map((mover) => (
                <div
                  key={mover.symbol}
                  className="flex items-center justify-between py-1.5 px-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
                  onClick={() => navigate(`/analysis/${mover.symbol}`)}
                >
                  <div className="flex items-center gap-2">
                    <div
                      className={cn(
                        "w-1.5 h-1.5 rounded-full",
                        mover.change >= 0 ? "bg-datis-green" : "bg-datis-red"
                      )}
                    />
                    <span className="text-sm font-display font-semibold text-datis-text">
                      {mover.symbol}
                    </span>
                  </div>
                  <span
                    className={cn(
                      "font-data text-xs font-semibold",
                      mover.change >= 0
                        ? "text-datis-green"
                        : "text-datis-red"
                    )}
                  >
                    {mover.change >= 0 ? "+" : ""}
                    {mover.change.toFixed(2)}%
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          <div className="glass-card rounded-xl p-5">
            <div className="flex items-center gap-2 mb-5">
              <Shield className="w-4 h-4 text-datis-purple" />
              <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                Risk Intelligence Panel
              </span>
            </div>

            <div className="grid grid-cols-3 gap-6">
              {[
                {
                  label: "Volatility Index",
                  value: stock.anomalyScore * 100,
                  color: "#06B6D4",
                  detail:
                    stock.anomalyScore < 0.3
                      ? "Low"
                      : stock.anomalyScore < 0.6
                        ? "Medium"
                        : "High",
                },
                {
                  label: "Market Liquidity",
                  value: (1 - stock.anomalyScore) * 100,
                  color: "#22C55E",
                  detail: "Optimal",
                },
                {
                  label: "Bayesian Confidence",
                  value: stock.bayesianFusion * 100,
                  color: "#A855F7",
                  detail: `Score: ${stock.bayesianFusion.toFixed(2)}`,
                },
              ].map((risk) => (
                <div key={risk.label}>
                  <div className="flex justify-between text-xs mb-2">
                    <span className="text-datis-text-muted font-display uppercase font-semibold tracking-wider text-[10px]">
                      {risk.label}
                    </span>
                    <span className="font-data text-datis-text">
                      {risk.detail}
                    </span>
                  </div>
                  <div className="w-full h-1.5 bg-datis-border/30 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-1000"
                      style={{
                        width: `${risk.value}%`,
                        backgroundColor: risk.color,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-5 p-3 bg-datis-cyan/5 border border-datis-cyan/10 rounded-xl">
              <p className="text-[11px] text-datis-cyan/80 leading-relaxed italic">
                "{stock.aiDecision}"
              </p>
            </div>
          </div>
        </div>

        <div className="col-span-4">
          <div className="glass-card rounded-xl p-5 h-full">
            <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-4 block">
              Quick Actions
            </span>

            <div className="space-y-2">
              {[
                {
                  label: "Deep Analysis",
                  path: `/analysis/${selectedSymbol}`,
                  icon: BarChart3,
                  color: "text-datis-cyan",
                },
                {
                  label: "Run Simulator",
                  path: "/simulator",
                  icon: Zap,
                  color: "text-datis-amber",
                },
                {
                  label: "View Portfolio",
                  path: "/portfolio",
                  icon: TrendingUp,
                  color: "text-datis-green",
                },
                {
                  label: "Blockchain Log",
                  path: "/blockchain",
                  icon: Shield,
                  color: "text-datis-purple",
                },
              ].map((item) => (
                <button
                  key={item.label}
                  onClick={() => navigate(item.path)}
                  className="w-full flex items-center justify-between px-4 py-3 rounded-xl bg-datis-bg/50 border border-datis-border/50 hover:border-datis-cyan/20 hover:bg-datis-card-hover transition-all duration-200 group"
                >
                  <div className="flex items-center gap-3">
                    <item.icon className={cn("w-4 h-4", item.color)} />
                    <span className="text-sm font-display text-datis-text">
                      {item.label}
                    </span>
                  </div>
                  <ArrowUpRight className="w-3.5 h-3.5 text-datis-text-muted group-hover:text-datis-cyan transition-colors" />
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}