import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(value: number, currency = "INR"): string {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value);
}

export function formatPercent(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-IN").format(value);
}

export function truncateHash(hash: string, chars = 6): string {
  return `${hash.slice(0, chars)}...${hash.slice(-chars)}`;
}

export function getSignalColor(signal: string): string {
  switch (signal.toUpperCase()) {
    case "BUY":
    case "BULLISH":
    case "STRONG BUY":
      return "text-datis-green";
    case "SELL":
    case "BEARISH":
    case "STRONG SELL":
      return "text-datis-red";
    case "HOLD":
    case "NEUTRAL":
      return "text-datis-amber";
    default:
      return "text-datis-cyan";
  }
}

export function getSignalBg(signal: string): string {
  switch (signal.toUpperCase()) {
    case "BUY":
    case "BULLISH":
    case "STRONG BUY":
      return "bg-datis-green/10 border-datis-green/20";
    case "SELL":
    case "BEARISH":
    case "STRONG SELL":
      return "bg-datis-red/10 border-datis-red/20";
    case "HOLD":
    case "NEUTRAL":
      return "bg-datis-amber/10 border-datis-amber/20";
    default:
      return "bg-datis-cyan/10 border-datis-cyan/20";
  }
}

export function randomBetween(min: number, max: number): number {
  return Math.random() * (max - min) + min;
}
