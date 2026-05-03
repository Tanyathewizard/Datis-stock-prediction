import { useState, useEffect } from "react";
import { Bell, Wifi } from "lucide-react";
import { cn } from "@/lib/utils";
import { ThemeToggle } from "./theme-toggle";
import { StockSelector } from "./stock-selector";

interface TopbarProps {
  selectedSymbol: string;
  onSymbolChange: (symbol: string) => void;
}

export function Topbar({ selectedSymbol, onSymbolChange }: TopbarProps) {
  const [time, setTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header
      className={cn(
        "fixed top-0 right-0 h-14 z-30",
        "w-[calc(100%-16rem)]",
        "bg-datis-surface/80 backdrop-blur-xl",
        "border-b border-datis-border/40",
        "flex items-center justify-between px-6",
        "shadow-sm"
      )}
      id="topbar"
    >
      {/* Left: Stock Selector */}
      <div className="flex items-center gap-4">
        <StockSelector selectedSymbol={selectedSymbol} onSelect={onSymbolChange} />
      </div>

      {/* Right: Status, Clock, Actions */}
      <div className="flex items-center gap-4">
        {/* System Online Pulse */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-datis-green/5 border border-datis-green/20">
          <div className="relative flex items-center justify-center">
            <div className="w-2 h-2 rounded-full bg-datis-green pulse-dot" />
          </div>
          <span className="text-[10px] font-display font-semibold uppercase tracking-wider text-datis-green">
            System Online
          </span>
        </div>

        {/* Clock */}
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-datis-card/50 border border-datis-border/50">
          <span className="font-data text-xs text-datis-text-secondary">
            {time.toLocaleTimeString("en-IN", { hour12: false })}
          </span>
          <span className="text-[9px] text-datis-text-muted font-display">IST</span>
        </div>

        {/* Notifications */}
        <button
          className={cn(
            "relative p-2 rounded-lg",
            "bg-datis-card/50 border border-datis-border/50",
            "hover:border-datis-cyan/30 hover:bg-datis-card-hover",
            "transition-all duration-300"
          )}
          id="notifications-btn"
        >
          <Bell className="w-4 h-4 text-datis-text-secondary" />
          <span className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-datis-red rounded-full border-2 border-datis-surface" />
        </button>

        {/* Connection */}
        <button
          className={cn(
            "p-2 rounded-lg",
            "bg-datis-card/50 border border-datis-border/50",
            "hover:border-datis-cyan/30 hover:bg-datis-card-hover",
            "transition-all duration-300"
          )}
        >
          <Wifi className="w-4 h-4 text-datis-green" />
        </button>

        {/* Theme Toggle */}
        <ThemeToggle />
      </div>
    </header>
  );
}
