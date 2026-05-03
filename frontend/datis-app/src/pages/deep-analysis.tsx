import { useParams } from "wouter";
import {
  Brain,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Activity,
  Target,
  Layers,
  Lightbulb,
} from "lucide-react";
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from "recharts";
import { cn } from "@/lib/utils";
import { useGetStockAnalysis } from "@/hooks/use-api";
import { MetricCard, SignalBadge, ChartCard, ProgressRing } from "@/components/ui-cards";

export default function DeepAnalysis() {
  const params = useParams<{ symbol: string }>();
  const symbol = params.symbol || "RELIANCE";
  const { data: stock } = useGetStockAnalysis(symbol);

  if (!stock) return null;

  const radarData = stock.featureImportance.map((f) => ({
    feature: f.feature,
    value: f.importance * 100,
  }));

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
              Deep Analysis
            </h1>
            <SignalBadge signal={stock.signal} size="lg" />
          </div>
          <p className="text-sm text-datis-text-muted">
            {stock.name} ({stock.symbol}) — Multi-model AI analysis
          </p>
        </div>
        <div className="flex gap-2">
          <div className="glass-card px-4 py-2 rounded-xl">
            <span className="font-data text-lg font-bold text-datis-text">
              ₹{stock.price.toFixed(2)}
            </span>
            <span
              className={cn(
                "ml-2 font-data text-sm",
                stock.change >= 0 ? "text-datis-green" : "text-datis-red"
              )}
            >
              {stock.change >= 0 ? "+" : ""}{stock.changePercent.toFixed(2)}%
            </span>
          </div>
        </div>
      </div>

      {/* AI Model Scores */}
      <div className="grid grid-cols-4 gap-4">
        <MetricCard
          title="LSTM Prediction"
          value={`₹${stock.lstmPrediction.toFixed(0)}`}
          icon={Brain}
          trend={stock.lstmPrediction > stock.price ? "up" : "down"}
          trendValue={`${(
            ((stock.lstmPrediction - stock.price) / stock.price) * 100
          ).toFixed(2)}%`}
          glowColor="cyan"
        />
        <MetricCard
          title="FinBERT Sentiment"
          value={`${(stock.finbertSentiment * 100).toFixed(0)}%`}
          icon={Activity}
          trend={stock.finbertSentiment > 0.6 ? "up" : stock.finbertSentiment > 0.4 ? "neutral" : "down"}
          trendValue={
            stock.finbertSentiment > 0.6 ? "Positive" : stock.finbertSentiment > 0.4 ? "Neutral" : "Negative"
          }
          glowColor="green"
        />
        <MetricCard
          title="Anomaly Score"
          value={stock.anomalyScore.toFixed(3)}
          icon={AlertTriangle}
          trend={stock.anomalyScore < 0.3 ? "up" : stock.anomalyScore < 0.6 ? "neutral" : "down"}
          trendValue={stock.anomalyScore < 0.3 ? "Normal" : stock.anomalyScore < 0.6 ? "Elevated" : "Critical"}
          glowColor={stock.anomalyScore < 0.3 ? "green" : stock.anomalyScore < 0.6 ? "amber" : "red"}
        />
        <MetricCard
          title="Bayesian Fusion"
          value={`${(stock.bayesianFusion * 100).toFixed(0)}%`}
          icon={Layers}
          trend={stock.bayesianFusion > 0.7 ? "up" : stock.bayesianFusion > 0.5 ? "neutral" : "down"}
          trendValue={`Confidence: ${stock.confidence.toFixed(0)}%`}
          glowColor="purple"
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-12 gap-4">
        {/* Trend Chart: LSTM vs Actual */}
        <ChartCard
          title="LSTM vs Actual Price"
          subtitle="30-Day Comparison"
          className="col-span-8"
        >
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={stock.trendCharts}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis
                dataKey="date"
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
              <Legend />
              <Line
                type="monotone"
                dataKey="actual"
                stroke="#06B6D4"
                strokeWidth={2}
                dot={false}
                name="Actual Price"
              />
              <Line
                type="monotone"
                dataKey="lstm"
                stroke="#A855F7"
                strokeWidth={2}
                dot={false}
                strokeDasharray="5 5"
                name="LSTM Prediction"
              />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Feature Importance Radar */}
        <ChartCard
          title="Feature Importance"
          subtitle="AI Model Weights"
          className="col-span-4"
        >
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData} outerRadius={90}>
              <PolarGrid stroke="rgba(255,255,255,0.08)" />
              <PolarAngleAxis
                dataKey="feature"
                tick={{ fontSize: 9, fill: "#9CA3AF" }}
              />
              <PolarRadiusAxis tick={false} axisLine={false} />
              <Radar
                name="Importance"
                dataKey="value"
                stroke="#06B6D4"
                fill="#06B6D4"
                fillOpacity={0.2}
                strokeWidth={2}
              />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      {/* Sentiment Trend */}
      <ChartCard
        title="Sentiment Trend"
        subtitle="FinBERT sentiment scores over 30 days"
      >
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={stock.trendCharts}>
            <defs>
              <linearGradient id="sentGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#22C55E" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
            <XAxis dataKey="date" tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} domain={[0, 1]} />
            <Tooltip
              contentStyle={{
                background: "rgba(17, 24, 39, 0.95)",
                border: "1px solid rgba(34, 197, 94, 0.3)",
                borderRadius: "12px",
              }}
            />
            <Area
              type="monotone"
              dataKey="sentiment"
              stroke="#22C55E"
              strokeWidth={2}
              fill="url(#sentGrad)"
              name="Sentiment Score"
            />
          </AreaChart>
        </ResponsiveContainer>
      </ChartCard>

      {/* AI Explanation & Recommendation */}
      <div className="grid grid-cols-12 gap-4">
        <div className="col-span-8">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center gap-2 mb-4">
              <Lightbulb className="w-4 h-4 text-datis-amber" />
              <h3 className="font-display font-semibold text-sm text-datis-text">
                AI Explanation
              </h3>
            </div>
            <p className="text-sm text-datis-text-secondary leading-relaxed">
              {stock.aiExplanation}
            </p>
            {stock.contradiction && (
              <div className="mt-4 p-3 bg-datis-amber/5 border border-datis-amber/15 rounded-xl">
                <div className="flex items-center gap-2 mb-2">
                  <AlertTriangle className="w-3.5 h-3.5 text-datis-amber" />
                  <span className="text-xs font-display font-semibold text-datis-amber uppercase">
                    Model Contradiction
                  </span>
                </div>
                <p className="text-xs text-datis-amber/80 leading-relaxed">
                  {stock.contradictionDetails}
                </p>
              </div>
            )}
          </div>
        </div>

        <div className="col-span-4">
          <div className="glass-card rounded-xl p-6 h-full flex flex-col items-center justify-center text-center">
            <div className="flex items-center gap-2 mb-4">
              <Target className="w-4 h-4 text-datis-cyan" />
              <h3 className="font-display font-semibold text-sm text-datis-text">
                Recommendation
              </h3>
            </div>
            <ProgressRing
              value={stock.confidence}
              color={stock.signal.includes("BUY") ? "#22C55E" : stock.signal.includes("SELL") ? "#EF4444" : "#F59E0B"}
              label={stock.signal}
              sublabel={`${stock.confidence.toFixed(1)}% confidence`}
              size={150}
              strokeWidth={10}
            />
            <div className="mt-4">
              <div className="font-data text-lg font-bold text-datis-text">
                Target: ₹{stock.lstmPrediction.toFixed(0)}
              </div>
              <div className="text-xs text-datis-text-muted mt-1">
                Based on Bayesian Fusion of {stock.featureImportance.length} models
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
