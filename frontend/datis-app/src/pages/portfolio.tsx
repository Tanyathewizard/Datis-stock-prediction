import { useState } from "react";
import {
  Wallet,
  TrendingUp,
  TrendingDown,
  PlusCircle,
  MinusCircle,
  DollarSign,
  PieChart as PieIcon,
  History,
  X,
} from "lucide-react";
import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";
import { cn } from "@/lib/utils";
import { useGetPortfolio } from "@/hooks/use-api";
import { MetricCard, SignalBadge, ChartCard } from "@/components/ui-cards";

export default function Portfolio() {
  const { data: portfolio } = useGetPortfolio();
  const [showModal, setShowModal] = useState(false);
  const [modalAction, setModalAction] = useState<"BUY" | "SELL">("BUY");

  if (!portfolio) return null;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex items-end justify-between">
        <div>
          <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
            Virtual Portfolio
          </h1>
          <p className="text-sm text-datis-text-muted mt-1">
            ₹10,000 virtual paper trading portfolio
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => { setModalAction("BUY"); setShowModal(true); }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl",
              "bg-datis-green/10 border border-datis-green/20",
              "text-datis-green font-display font-semibold text-sm",
              "hover:bg-datis-green/15 transition-all"
            )}
          >
            <PlusCircle className="w-4 h-4" />
            Buy
          </button>
          <button
            onClick={() => { setModalAction("SELL"); setShowModal(true); }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl",
              "bg-datis-red/10 border border-datis-red/20",
              "text-datis-red font-display font-semibold text-sm",
              "hover:bg-datis-red/15 transition-all"
            )}
          >
            <MinusCircle className="w-4 h-4" />
            Sell
          </button>
        </div>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-5 gap-4">
        <MetricCard
          title="Total Value"
          value={`₹${portfolio.totalValue.toLocaleString("en-IN")}`}
          icon={Wallet}
          glowColor="cyan"
        />
        <MetricCard
          title="Cash Balance"
          value={`₹${portfolio.cashBalance.toLocaleString("en-IN")}`}
          icon={DollarSign}
          glowColor="purple"
        />
        <MetricCard
          title="Total P&L"
          value={`₹${portfolio.totalPnl.toLocaleString("en-IN")}`}
          icon={portfolio.totalPnl >= 0 ? TrendingUp : TrendingDown}
          trend={portfolio.totalPnl >= 0 ? "up" : "down"}
          trendValue={`${portfolio.totalPnlPercent.toFixed(2)}%`}
          glowColor={portfolio.totalPnl >= 0 ? "green" : "red"}
        />
        <MetricCard
          title="ROI"
          value={`${portfolio.roi.toFixed(2)}%`}
          icon={TrendingUp}
          trend={portfolio.roi >= 0 ? "up" : "down"}
          trendValue="Since inception"
          glowColor={portfolio.roi >= 0 ? "green" : "red"}
        />
        <MetricCard
          title="Invested"
          value={`₹${portfolio.investedValue.toLocaleString("en-IN")}`}
          icon={PieIcon}
          subtitle="Initial capital"
          glowColor="amber"
        />
      </div>

      {/* Holdings + Allocation */}
      <div className="grid grid-cols-12 gap-4">
        {/* Holdings Table */}
        <div className="col-span-8">
          <div className="glass-card rounded-xl overflow-hidden">
            <div className="px-5 py-4 border-b border-datis-border/50 flex items-center justify-between">
              <h3 className="font-display font-semibold text-sm text-datis-text">Current Holdings</h3>
              <span className="text-xs text-datis-text-muted font-data">{portfolio.holdings.length} positions</span>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-datis-border/30">
                    {["Symbol", "Shares", "Avg Price", "Current", "Value", "P&L", "% Change"].map((h) => (
                      <th
                        key={h}
                        className="px-5 py-3 text-[10px] font-display font-semibold uppercase tracking-wider text-datis-text-muted"
                      >
                        {h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {portfolio.holdings.map((h) => (
                    <tr
                      key={h.symbol}
                      className="border-b border-datis-border/20 hover:bg-datis-cyan/5 transition-colors"
                    >
                      <td className="px-5 py-3">
                        <div className="flex items-center gap-2">
                          <div className={cn("w-1.5 h-1.5 rounded-full", h.pnl >= 0 ? "bg-datis-green" : "bg-datis-red")} />
                          <span className="font-display font-semibold text-sm text-datis-text">{h.symbol}</span>
                        </div>
                        <div className="text-xs text-datis-text-muted mt-0.5">{h.name}</div>
                      </td>
                      <td className="px-5 py-3 font-data text-sm text-datis-text">{h.shares}</td>
                      <td className="px-5 py-3 font-data text-sm text-datis-text-secondary">₹{h.avgPrice.toFixed(2)}</td>
                      <td className="px-5 py-3 font-data text-sm text-datis-text">₹{h.currentPrice.toFixed(2)}</td>
                      <td className="px-5 py-3 font-data text-sm text-datis-text">₹{h.value.toFixed(2)}</td>
                      <td className={cn("px-5 py-3 font-data text-sm font-semibold", h.pnl >= 0 ? "text-datis-green" : "text-datis-red")}>
                        {h.pnl >= 0 ? "+" : ""}₹{h.pnl.toFixed(2)}
                      </td>
                      <td className={cn("px-5 py-3 font-data text-sm font-semibold", h.pnlPercent >= 0 ? "text-datis-green" : "text-datis-red")}>
                        {h.pnlPercent >= 0 ? "+" : ""}{h.pnlPercent.toFixed(2)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Allocation Pie */}
        <div className="col-span-4">
          <ChartCard title="Portfolio Allocation" subtitle="By holdings weight">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={portfolio.allocation}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {portfolio.allocation.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} stroke="transparent" />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    background: "rgba(17, 24, 39, 0.95)",
                    border: "1px solid rgba(6, 182, 212, 0.3)",
                    borderRadius: "12px",
                  }}
                  formatter={(val: number) => [`${val}%`, "Allocation"]}
                />
              </PieChart>
            </ResponsiveContainer>
            <div className="space-y-2 mt-2">
              {portfolio.allocation.map((a) => (
                <div key={a.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2.5 h-2.5 rounded-sm" style={{ backgroundColor: a.color }} />
                    <span className="text-xs font-display text-datis-text-secondary">{a.name}</span>
                  </div>
                  <span className="font-data text-xs text-datis-text">{a.value}%</span>
                </div>
              ))}
            </div>
          </ChartCard>
        </div>
      </div>

      {/* Trade History */}
      <div className="glass-card rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-datis-border/50 flex items-center gap-2">
          <History className="w-4 h-4 text-datis-text-muted" />
          <h3 className="font-display font-semibold text-sm text-datis-text">Trade History</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead>
              <tr className="border-b border-datis-border/30">
                {["ID", "Symbol", "Action", "Shares", "Price", "Total", "Date", "Status"].map((h) => (
                  <th
                    key={h}
                    className="px-5 py-3 text-[10px] font-display font-semibold uppercase tracking-wider text-datis-text-muted"
                  >
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {portfolio.tradeHistory.map((t) => (
                <tr key={t.id} className="border-b border-datis-border/20 hover:bg-datis-cyan/5 transition-colors">
                  <td className="px-5 py-3 font-data text-xs text-datis-text-muted">{t.id}</td>
                  <td className="px-5 py-3 font-display font-semibold text-sm text-datis-text">{t.symbol}</td>
                  <td className="px-5 py-3">
                    <SignalBadge signal={t.action} size="sm" />
                  </td>
                  <td className="px-5 py-3 font-data text-sm text-datis-text">{t.shares}</td>
                  <td className="px-5 py-3 font-data text-sm text-datis-text">₹{t.price.toFixed(2)}</td>
                  <td className="px-5 py-3 font-data text-sm text-datis-text">₹{t.total.toFixed(2)}</td>
                  <td className="px-5 py-3 font-data text-xs text-datis-text-secondary">
                    {new Date(t.timestamp).toLocaleDateString("en-IN")}
                  </td>
                  <td className="px-5 py-3">
                    <SignalBadge signal={t.status} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Buy/Sell Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">
          <div className="glass-card rounded-2xl w-full max-w-md p-6 relative border border-datis-border shadow-2xl">
            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-4 h-4 text-datis-text-muted" />
            </button>
            <h3 className="font-display font-bold text-lg text-datis-text mb-6">
              {modalAction === "BUY" ? "Buy Stock" : "Sell Stock"}
            </h3>
            <div className="space-y-4">
              <div>
                <label className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-2">
                  Symbol
                </label>
                <input
                  type="text"
                  placeholder="e.g. RELIANCE"
                  className="w-full px-4 py-2.5 rounded-xl bg-datis-bg/80 border border-datis-border text-datis-text text-sm font-data outline-none focus:border-datis-cyan/50 transition-colors"
                />
              </div>
              <div>
                <label className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-2">
                  Quantity
                </label>
                <input
                  type="number"
                  placeholder="Number of shares"
                  className="w-full px-4 py-2.5 rounded-xl bg-datis-bg/80 border border-datis-border text-datis-text text-sm font-data outline-none focus:border-datis-cyan/50 transition-colors"
                />
              </div>
              <div>
                <label className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-2">
                  Price (₹)
                </label>
                <input
                  type="number"
                  placeholder="Market price"
                  className="w-full px-4 py-2.5 rounded-xl bg-datis-bg/80 border border-datis-border text-datis-text text-sm font-data outline-none focus:border-datis-cyan/50 transition-colors"
                />
              </div>
              <button
                onClick={() => setShowModal(false)}
                className={cn(
                  "w-full py-3 rounded-xl font-display font-bold text-sm uppercase tracking-wider transition-all",
                  modalAction === "BUY"
                    ? "bg-gradient-to-r from-datis-green to-datis-green-dim text-white hover:shadow-lg hover:shadow-datis-green/30"
                    : "bg-gradient-to-r from-datis-red to-datis-red-dim text-white hover:shadow-lg hover:shadow-datis-red/30"
                )}
              >
                {modalAction === "BUY" ? "Place Buy Order" : "Place Sell Order"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
