import {
  AlertTriangle,
  TrendingDown,
  Brain,
  BookOpen,
  Target,
  Calendar,
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
import { useGetFailedPredictions, useGetAccuracyTimeline } from "@/hooks/use-api";
import { SignalBadge, ChartCard, ProgressRing } from "@/components/ui-cards";
import { HEATMAP_DATA } from "@/lib/mock-data";

export default function Failures() {
  const { data: failures } = useGetFailedPredictions();
  const { data: timeline } = useGetAccuracyTimeline();

  if (!failures || !timeline) return null;

  const avgAccuracy = failures.reduce((sum, f) => sum + f.accuracy, 0) / failures.length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
          Failure Analysis & Learning
        </h1>
        <p className="text-sm text-datis-text-muted mt-1">
          Transparency dashboard — tracking failed predictions, root causes, and model improvements
        </p>
      </div>

      {/* Summary */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-red/10">
            <AlertTriangle className="w-5 h-5 text-datis-red" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Failed Predictions
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{failures.length}</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <ProgressRing
            value={avgAccuracy}
            size={50}
            strokeWidth={4}
            color="#F59E0B"
          />
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Avg Accuracy
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{avgAccuracy.toFixed(1)}%</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-green/10">
            <Brain className="w-5 h-5 text-datis-green" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Lessons Learned
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{failures.length}</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-cyan/10">
            <Target className="w-5 h-5 text-datis-cyan" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Current Accuracy
            </div>
            <div className="font-data text-2xl font-bold text-datis-green">{timeline[timeline.length - 1]?.accuracy}%</div>
          </div>
        </div>
      </div>

      {/* Accuracy Timeline + Heatmap */}
      <div className="grid grid-cols-12 gap-4">
        <ChartCard
          title="Accuracy Improvement Timeline"
          subtitle="Monthly model accuracy trend"
          className="col-span-7"
        >
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={timeline}>
              <defs>
                <linearGradient id="accGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22C55E" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#22C55E" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
              <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 10, fill: "#6B7280" }} axisLine={false} tickLine={false} domain={[60, 90]} />
              <Tooltip
                contentStyle={{
                  background: "rgba(17, 24, 39, 0.95)",
                  border: "1px solid rgba(34, 197, 94, 0.3)",
                  borderRadius: "12px",
                }}
                formatter={(val: number) => [`${val}%`, "Accuracy"]}
              />
              <Area type="monotone" dataKey="accuracy" stroke="#22C55E" strokeWidth={2.5} fill="url(#accGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>

        {/* Sector Failure Heatmap */}
        <div className="col-span-5">
          <div className="glass-card rounded-xl p-5 h-full">
            <h3 className="font-display font-semibold text-sm text-datis-text mb-4">
              Failure Heatmap by Sector
            </h3>
            <div className="space-y-2">
              <div className="grid grid-cols-6 gap-1 text-center">
                <div />
                {["Mon", "Tue", "Wed", "Thu", "Fri"].map((d) => (
                  <span key={d} className="text-[9px] font-display font-semibold text-datis-text-muted uppercase">
                    {d}
                  </span>
                ))}
              </div>
              {HEATMAP_DATA.map((row) => (
                <div key={row.sector} className="grid grid-cols-6 gap-1 items-center">
                  <span className="text-[10px] font-display font-semibold text-datis-text-muted uppercase truncate">
                    {row.sector}
                  </span>
                  {[row.mon, row.tue, row.wed, row.thu, row.fri].map((val, i) => (
                    <div
                      key={i}
                      className={cn(
                        "h-8 rounded-lg flex items-center justify-center text-[10px] font-data font-bold transition-colors",
                        val === 0 && "bg-datis-border/20 text-datis-text-muted",
                        val === 1 && "bg-datis-amber/15 text-datis-amber",
                        val === 2 && "bg-datis-amber/30 text-datis-amber",
                        val >= 3 && "bg-datis-red/30 text-datis-red"
                      )}
                    >
                      {val}
                    </div>
                  ))}
                </div>
              ))}
            </div>
            <div className="flex items-center gap-4 mt-4 text-[10px] text-datis-text-muted">
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-datis-border/20" />
                <span>0</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-datis-amber/15" />
                <span>Low</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-datis-amber/30" />
                <span>Medium</span>
              </div>
              <div className="flex items-center gap-1.5">
                <div className="w-3 h-3 rounded bg-datis-red/30" />
                <span>High</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Failed Prediction Details */}
      <div className="glass-card rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-datis-border/50 flex items-center gap-2">
          <TrendingDown className="w-4 h-4 text-datis-red" />
          <h3 className="font-display font-semibold text-sm text-datis-text">Failed Prediction Details</h3>
        </div>
        <div className="divide-y divide-datis-border/20">
          {failures.map((f) => (
            <div key={f.id} className="px-5 py-5 hover:bg-datis-cyan/5 transition-colors">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="font-display font-bold text-sm text-datis-text">{f.symbol}</span>
                  <div className="flex items-center gap-1.5 text-xs text-datis-text-muted">
                    <Calendar className="w-3 h-3" />
                    {f.date}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <div className={cn("font-data text-sm font-bold", f.deviation > 0 ? "text-datis-green" : "text-datis-red")}>
                    {f.deviation > 0 ? "+" : ""}{f.deviation.toFixed(1)}% deviation
                  </div>
                  <ProgressRing
                    value={f.accuracy}
                    size={42}
                    strokeWidth={4}
                    color={f.accuracy > 50 ? "#F59E0B" : "#EF4444"}
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 mb-3">
                <div className="p-3 rounded-xl bg-datis-red/5 border border-datis-red/10">
                  <div className="text-[10px] font-display font-semibold uppercase tracking-wider text-datis-red mb-1">
                    Predicted
                  </div>
                  <p className="text-xs text-datis-text-secondary">{f.predicted}</p>
                </div>
                <div className="p-3 rounded-xl bg-datis-amber/5 border border-datis-amber/10">
                  <div className="text-[10px] font-display font-semibold uppercase tracking-wider text-datis-amber mb-1">
                    Actual
                  </div>
                  <p className="text-xs text-datis-text-secondary">{f.actual}</p>
                </div>
              </div>
              <div className="p-3 rounded-xl bg-datis-bg/40 border border-datis-border/30 mb-2">
                <div className="text-[10px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-1">
                  Root Cause
                </div>
                <p className="text-xs text-datis-text-secondary leading-relaxed">{f.rootCause}</p>
              </div>
              <div className="p-3 rounded-xl bg-datis-green/5 border border-datis-green/10">
                <div className="flex items-center gap-1.5 mb-1">
                  <BookOpen className="w-3 h-3 text-datis-green" />
                  <span className="text-[10px] font-display font-semibold uppercase tracking-wider text-datis-green">
                    Lesson Learned
                  </span>
                </div>
                <p className="text-xs text-datis-text-secondary leading-relaxed">{f.lesson}</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
