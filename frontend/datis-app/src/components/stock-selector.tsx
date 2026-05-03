import { useState } from "react";
import { ChevronDown, Search } from "lucide-react";
import { cn } from "@/lib/utils";
import { STOCK_LIST } from "@/lib/mock-data";

interface StockSelectorProps {
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
}

export function StockSelector({ selectedSymbol, onSelect }: StockSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [search, setSearch] = useState("");

  const filtered = STOCK_LIST.filter(
    (s) =>
      s.symbol.toLowerCase().includes(search.toLowerCase()) ||
      s.name.toLowerCase().includes(search.toLowerCase())
  );

  const selected = STOCK_LIST.find((s) => s.symbol === selectedSymbol);

  return (
    <div className="relative" id="stock-selector">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center gap-2.5 px-4 py-2 rounded-xl",
          "bg-datis-card border border-datis-border",
          "hover:border-datis-cyan/30 hover:bg-datis-card-hover",
          "transition-all duration-300 min-w-[200px]"
        )}
      >
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "w-2 h-2 rounded-full",
              selected && selected.change >= 0 ? "bg-datis-green" : "bg-datis-red"
            )}
          />
          <span className="font-display font-semibold text-sm text-datis-text">
            {selectedSymbol}
          </span>
        </div>
        {selected && (
          <span
            className={cn(
              "font-data text-xs",
              selected.change >= 0 ? "text-datis-green" : "text-datis-red"
            )}
          >
            {selected.change >= 0 ? "+" : ""}
            {selected.changePercent.toFixed(2)}%
          </span>
        )}
        <ChevronDown
          className={cn(
            "w-4 h-4 text-datis-text-muted ml-auto transition-transform duration-300",
            isOpen && "rotate-180"
          )}
        />
      </button>

      {isOpen && (
        <div
          className={cn(
            "absolute top-full mt-2 left-0 w-72 z-50",
            "bg-datis-card border border-datis-border rounded-xl",
            "shadow-2xl shadow-black/40 overflow-hidden",
            "animate-fade-in"
          )}
        >
          <div className="p-3 border-b border-datis-border">
            <div className="flex items-center gap-2 bg-datis-bg/60 rounded-lg px-3 py-2">
              <Search className="w-3.5 h-3.5 text-datis-text-muted" />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search stocks..."
                className="bg-transparent text-sm text-datis-text placeholder:text-datis-text-muted outline-none w-full font-sans"
                autoFocus
              />
            </div>
          </div>
          <div className="max-h-64 overflow-y-auto">
            {filtered.map((stock) => (
              <button
                key={stock.symbol}
                onClick={() => {
                  onSelect(stock.symbol);
                  setIsOpen(false);
                  setSearch("");
                }}
                className={cn(
                  "w-full flex items-center justify-between px-4 py-3",
                  "hover:bg-datis-cyan/5 transition-colors",
                  stock.symbol === selectedSymbol && "bg-datis-cyan/10"
                )}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "w-1.5 h-1.5 rounded-full",
                      stock.change >= 0 ? "bg-datis-green" : "bg-datis-red"
                    )}
                  />
                  <div className="text-left">
                    <div className="text-sm font-semibold text-datis-text font-display">
                      {stock.symbol}
                    </div>
                    <div className="text-xs text-datis-text-muted">{stock.name}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-sm font-data text-datis-text">
                    ₹{stock.price.toFixed(2)}
                  </div>
                  <div
                    className={cn(
                      "text-xs font-data",
                      stock.change >= 0 ? "text-datis-green" : "text-datis-red"
                    )}
                  >
                    {stock.change >= 0 ? "+" : ""}
                    {stock.changePercent.toFixed(2)}%
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {isOpen && (
        <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
      )}
    </div>
  );
}
