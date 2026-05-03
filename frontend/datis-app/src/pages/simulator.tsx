import { useState } from "react";
import {
  FlaskConical,
  Play,
  TrendingUp,
  Gauge,
  Shield,
  Target,
  Zap,
} from "lucide-react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { cn } from "@/lib/utils";
import { useGetPrediction } from "@/hooks/use-api";
import { MetricCard, SignalBadge, ChartCard, ProgressRing } from "@/components/ui-cards";

export default function Simulator() {
  const [params, setParams] = useState({
    sentiment: 5,
    volatility: 3,
    newsImpact: 4,
    volume: 6,
    timeHorizon: 14,
  });

  const [hasRun, setHasRun] = useState(false);
  const { data: result, refetch } = useGetPrediction(params);

  const handleRun = () => {
    setHasRun(true);
    refetch();
  };

  const sliders = [
    { key: "sentiment" as const, label: "Sentiment Score", min: 0, max: 10, icon: TrendingUp, color: "#22C55E" },
    { key: "volatility" as const, label: "Volatility Level", min: 0, max: 10, icon: Gauge, color: "#EF4444" },
    { key: "newsImpact" as const, label: "News Impact", min: 0, max: 10, icon: Zap, color: "#F59E0B" },
    { key: "volume" as const, label: "Volume Factor", min: 0, max: 10, icon: Target, color: "#A855F7" },
    { key: "timeHorizon" as const, label: "Time Horizon (Days)", min: 1, max: 30, icon: Shield, color: "#06B6D4" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
          AI Prediction Simulator
        </h1>
        <p className="text-sm text-datis-text-muted mt-1">
          Adjust market parameters and run AI predictions in real-time
        </p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        {/* Input Controls */}
        <div className="col-span-5">
          <div className="glass-card rounded-xl p-6">
            <div className="flex items-center gap-2 mb-6">
              <FlaskConical className="w-4 h-4 text-datis-cyan" />
              <h2 className="font-display font-semibold text-sm text-datis-text uppercase tracking-wider">
                Simulation Parameters
              </h2>
            </div>

            <div className="space-y-6">
              {sliders.map(({ key, label, min, max, icon: Icon, color }) => (
                <div key={key}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Icon className="w-3.5 h-3.5" style={{ color }} />
                      <span className="text-xs font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                        {label}
                      </span>
                    </div>
                    <span className="font-data text-sm font-bold text-datis-text">
                      {params[key]}
                    </span>
                  </div>
                  <input
                    type="range"
                    min={min}
                    max={max}
                    value={params[key]}
                    onChange={(e) => setParams({ ...params, [key]: parseInt(e.target.value) })}
                    className="w-full h-1.5 rounded-full appearance-none cursor-pointer"
                    style={{
                      background: `linear-gradient(to right, ${color} 0%, ${color} ${
                        ((params[key] - min) / (max - min)) * 100
                      }%, rgba(255,255,255,0.1) ${
                        ((params[key] - min) / (max - min)) * 100
                      }%, rgba(255,255,255,0.1) 100%)`,
                    }}
                  />
                  <div className="flex justify-between text-[10px] text-datis-text-muted mt-1 font-data">
                    <span>{min}</span>
                    <span>{max}</span>
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={handleRun}
              className={cn(
                "w-full mt-6 flex items-center justify-center gap-2 py-3 rounded-xl",
                "bg-gradient-to-r from-datis-cyan to-datis-cyan-dim",
                "text-white font-display font-bold text-sm uppercase tracking-wider",
                "hover:shadow-lg hover:shadow-datis-cyan/30",
                "transition-all duration-300 active:scale-[0.98]"
              )}
            >
              <Play className="w-4 h-4" />
              Run Simulation
            </button>
          </div>
        </div>

        {/* Output */}
        <div className="col-span-7 space-y-4">
          {hasRun && result ? (
            <>
              {/* Result Metrics */}
              <div className="grid grid-cols-3 gap-4">
                <MetricCard
                  title="Predicted Price"
                  value={`₹${result.predictedPrice.toFixed(2)}`}
                  icon={TrendingUp}
                  glowColor="cyan"
                />
                <MetricCard
                  title="Confidence"
                  value={`${result.confidence.toFixed(1)}%`}
                  icon={Gauge}
                  glowColor="green"
                />
                <div className="glass-card rounded-xl p-5 flex items-center justify-between">
                  <div>
                    <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-1">
                      AI Action
                    </span>
                    <SignalBadge signal={result.action} size="lg" />
                  </div>
                  <ProgressRing
                    value={result.riskScore}
                    max={100}
                    size={70}
                    strokeWidth={6}
                    color={
                      result.riskLevel === "HIGH" ? "#EF4444" : result.riskLevel === "MEDIUM" ? "#F59E0B" : "#22C55E"
                    }
                    label={result.riskLevel}
                  />
                </div>
              </div>

              {/* Prediction Chart */}
              <ChartCard
                title="Predicted Price Trajectory"
                subtitle={`${params.timeHorizon}-day forecast with confidence bands`}
              >
                <ResponsiveContainer width="100%" height={320}>
                  <AreaChart data={result.chartData}>
                    <defs>
                      <linearGradient id="predGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#06B6D4" stopOpacity={0.2} />
                        <stop offset="95%" stopColor="#06B6D4" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="bandGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#A855F7" stopOpacity={0.1} />
                        <stop offset="95%" stopColor="#A855F7" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                    <XAxis dataKey="time" tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} domain={["auto", "auto"]} />
                    <Tooltip
                      contentStyle={{
                        background: "rgba(17, 24, 39, 0.95)",
                        border: "1px solid rgba(6, 182, 212, 0.3)",
                        borderRadius: "12px",
                      }}
                    />
                    <Area type="monotone" dataKey="upper" stroke="none" fill="url(#bandGrad)" name="Upper Band" />
                    <Area type="monotone" dataKey="lower" stroke="none" fill="url(#bandGrad)" name="Lower Band" />
                    <Area
                      type="monotone"
                      dataKey="predicted"
                      stroke="#06B6D4"
                      strokeWidth={2.5}
                      fill="url(#predGrad)"
                      name="Predicted Price"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </ChartCard>
            </>
          ) : (
            <div className="glass-card rounded-xl p-16 flex flex-col items-center justify-center text-center h-full">
              <div className="w-16 h-16 rounded-2xl bg-datis-cyan/10 flex items-center justify-center mb-6 animate-float">
                <FlaskConical className="w-8 h-8 text-datis-cyan" />
              </div>
              <h3 className="font-display font-bold text-lg text-datis-text mb-2">
                Configure & Run
              </h3>
              <p className="text-sm text-datis-text-muted max-w-sm">
                Adjust the simulation parameters on the left, then click "Run Simulation" to generate AI-powered predictions.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
