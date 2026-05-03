import type { ReactNode } from "react";
import { cn } from "@/lib/utils";
import { type LucideIcon } from "lucide-react";

// ═══════════════════════════════════════════════════════════════
// Metric Card
// ═══════════════════════════════════════════════════════════════
interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  glowColor?: "cyan" | "green" | "red" | "amber" | "purple";
  className?: string;
}

export function MetricCard({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  trendValue,
  glowColor = "cyan",
  className,
}: MetricCardProps) {
  const glowClasses = {
    cyan: "hover:shadow-[0_0_30px_rgba(6,182,212,0.08)]",
    green: "hover:shadow-[0_0_30px_rgba(34,197,94,0.08)]",
    red: "hover:shadow-[0_0_30px_rgba(239,68,68,0.08)]",
    amber: "hover:shadow-[0_0_30px_rgba(245,158,11,0.08)]",
    purple: "hover:shadow-[0_0_30px_rgba(168,85,247,0.08)]",
  };

  const iconBgClasses = {
    cyan: "bg-datis-cyan/10 text-datis-cyan",
    green: "bg-datis-green/10 text-datis-green",
    red: "bg-datis-red/10 text-datis-red",
    amber: "bg-datis-amber/10 text-datis-amber",
    purple: "bg-datis-purple/10 text-datis-purple",
  };

  return (
    <div
      className={cn(
        "glass-card rounded-xl p-5 transition-all duration-300",
        glowClasses[glowColor],
        className
      )}
    >
      <div className="flex items-start justify-between mb-3">
        <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
          {title}
        </span>
        {Icon && (
          <div className={cn("p-2 rounded-lg", iconBgClasses[glowColor])}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="font-data text-2xl font-bold text-datis-text tracking-tight">
        {value}
      </div>
      <div className="flex items-center gap-2 mt-2">
        {trend && trendValue && (
          <span
            className={cn(
              "text-xs font-data font-semibold",
              trend === "up" && "text-datis-green",
              trend === "down" && "text-datis-red",
              trend === "neutral" && "text-datis-amber"
            )}
          >
            {trend === "up" ? "↑" : trend === "down" ? "↓" : "→"} {trendValue}
          </span>
        )}
        {subtitle && (
          <span className="text-xs text-datis-text-muted">{subtitle}</span>
        )}
      </div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Signal Badge
// ═══════════════════════════════════════════════════════════════
interface SignalBadgeProps {
  signal: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}

export function SignalBadge({ signal, size = "md", className }: SignalBadgeProps) {
  const colorMap: Record<string, string> = {
    "STRONG BUY": "bg-datis-green/15 text-datis-green border-datis-green/25",
    BUY: "bg-datis-green/10 text-datis-green border-datis-green/20",
    HOLD: "bg-datis-amber/10 text-datis-amber border-datis-amber/20",
    SELL: "bg-datis-red/10 text-datis-red border-datis-red/20",
    "STRONG SELL": "bg-datis-red/15 text-datis-red border-datis-red/25",
    BULLISH: "bg-datis-green/10 text-datis-green border-datis-green/20",
    BEARISH: "bg-datis-red/10 text-datis-red border-datis-red/20",
    NEUTRAL: "bg-datis-amber/10 text-datis-amber border-datis-amber/20",
    VERIFIED: "bg-datis-green/10 text-datis-green border-datis-green/20",
    PENDING: "bg-datis-amber/10 text-datis-amber border-datis-amber/20",
    FAILED: "bg-datis-red/10 text-datis-red border-datis-red/20",
    POSITIVE: "bg-datis-green/10 text-datis-green border-datis-green/20",
    NEGATIVE: "bg-datis-red/10 text-datis-red border-datis-red/20",
    MIXED: "bg-datis-purple/10 text-datis-purple border-datis-purple/20",
    COMPLETED: "bg-datis-green/10 text-datis-green border-datis-green/20",
  };

  const sizeClasses = {
    sm: "text-[10px] px-2 py-0.5",
    md: "text-xs px-2.5 py-1",
    lg: "text-sm px-3 py-1.5",
  };

  return (
    <span
      className={cn(
        "inline-flex items-center font-display font-bold uppercase tracking-wider rounded-lg border",
        sizeClasses[size],
        colorMap[signal.toUpperCase()] || "bg-datis-cyan/10 text-datis-cyan border-datis-cyan/20",
        className
      )}
    >
      {signal}
    </span>
  );
}

// ═══════════════════════════════════════════════════════════════
// Chart Card
// ═══════════════════════════════════════════════════════════════
interface ChartCardProps {
  title: string;
  subtitle?: string;
  children: ReactNode;
  actions?: ReactNode;
  className?: string;
}

export function ChartCard({ title, subtitle, children, actions, className }: ChartCardProps) {
  return (
    <div className={cn("glass-card rounded-xl overflow-hidden", className)}>
      <div className="flex items-center justify-between px-5 py-4 border-b border-datis-border/50">
        <div>
          <h3 className="font-display font-semibold text-sm text-datis-text">{title}</h3>
          {subtitle && (
            <p className="text-xs text-datis-text-muted mt-0.5">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
      <div className="p-5">{children}</div>
    </div>
  );
}

// ═══════════════════════════════════════════════════════════════
// Progress Ring
// ═══════════════════════════════════════════════════════════════
interface ProgressRingProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  color?: string;
  label?: string;
  sublabel?: string;
}

export function ProgressRing({
  value,
  max = 100,
  size = 120,
  strokeWidth = 8,
  color = "#06B6D4",
  label,
  sublabel,
}: ProgressRingProps) {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const percentage = Math.min(value / max, 1);
  const offset = circumference - percentage * circumference;

  return (
    <div className="relative inline-flex items-center justify-center" style={{ width: size, height: size }}>
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke="rgba(255,255,255,0.05)"
          strokeWidth={strokeWidth}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="text-2xl font-display font-bold text-datis-text">{Math.round(value)}</span>
        {label && (
          <span className="text-[10px] font-display font-semibold uppercase tracking-wider mt-0.5" style={{ color }}>
            {label}
          </span>
        )}
        {sublabel && (
          <span className="text-[9px] text-datis-text-muted mt-0.5">{sublabel}</span>
        )}
      </div>
    </div>
  );
}
