import { useState, type ReactNode } from "react";
import { Search } from "lucide-react";
import { Sidebar } from "./sidebar";
import { Topbar } from "./topbar";

interface LayoutProps {
  children: (props: { selectedSymbol: string }) => ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [selectedSymbol, setSelectedSymbol] = useState("AAPL");
  const [symbolInput, setSymbolInput] = useState("AAPL");

  const applySymbol = () => {
    const cleanSymbol = symbolInput.trim().toUpperCase();

    if (!cleanSymbol) return;

    setSelectedSymbol(cleanSymbol);
  };

  return (
    <div className="min-h-screen grid-bg">
      <Sidebar />

      <Topbar
        selectedSymbol={selectedSymbol}
        onSymbolChange={(symbol: string) => {
          const cleanSymbol = symbol.toUpperCase();
          setSelectedSymbol(cleanSymbol);
          setSymbolInput(cleanSymbol);
        }}
      />

      <main className="ml-64 pt-14 min-h-screen">
        <div className="p-6 space-y-6">
          <div className="glass-card rounded-2xl p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4 border border-datis-cyan/10">
            <div>
              <h2 className="text-xl font-display font-bold text-datis-text">
                Analyze Stock
              </h2>
              <p className="text-sm text-datis-text-muted mt-1">
                Type any symbol like AAPL, TSLA, NVDA, RELIANCE, TCS, INFY.
              </p>
            </div>

            <div className="flex items-center gap-3 w-full md:w-auto">
              <div className="relative flex-1 md:w-80">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-datis-text-muted" />

                <input
                  value={symbolInput}
                  onChange={(e) => setSymbolInput(e.target.value.toUpperCase())}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") applySymbol();
                  }}
                  placeholder="Enter symbol..."
                  className="w-full pl-10 pr-4 py-3 rounded-xl bg-datis-bg/70 border border-datis-border text-datis-text placeholder:text-datis-text-muted outline-none focus:border-datis-cyan/60 transition-all font-data"
                />
              </div>

              <button
                onClick={applySymbol}
                className="px-5 py-3 rounded-xl bg-gradient-to-r from-datis-cyan to-datis-cyan-dim text-white font-display font-bold text-sm uppercase tracking-wider hover:shadow-lg hover:shadow-datis-cyan/30 transition-all active:scale-[0.98]"
              >
                Analyze
              </button>
            </div>
          </div>

          {children({ selectedSymbol })}
        </div>
      </main>
    </div>
  );
}