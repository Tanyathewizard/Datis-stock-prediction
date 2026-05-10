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

import {
  MetricCard,
  SignalBadge,
  ChartCard,
} from "@/components/ui-cards";

export default function Portfolio() {

  const { data: portfolio } = useGetPortfolio();

  // =========================
  // MODAL STATES
  // =========================

  const [showModal, setShowModal] = useState(false);

  const [modalAction, setModalAction] = useState<
    "BUY" | "SELL" | "DEPOSIT" | "WITHDRAW"
  >("BUY");

  // =========================
  // WALLET STATE
  // =========================

  const [walletBalance, setWalletBalance] = useState(50000);

  const [walletAmount, setWalletAmount] = useState("");

  // =========================
  // BUY / SELL STATES
  // =========================

  const [symbol, setSymbol] = useState("");

  const [quantity, setQuantity] = useState("");

  const [price, setPrice] = useState("");

  if (!portfolio) return null;

  // =========================
  // WALLET ACTIONS
  // =========================

  const handleWalletAction = () => {

    const amount = Number(walletAmount);

    if (!amount || amount <= 0) {
      alert("Enter valid amount");
      return;
    }

    // Deposit
    if (modalAction === "DEPOSIT") {

      setWalletBalance(prev => prev + amount);

      alert(`₹${amount.toLocaleString()} added successfully`);

    }

    // Withdraw
    else if (modalAction === "WITHDRAW") {

      if (amount > walletBalance) {

        alert("Insufficient wallet balance");

        return;
      }

      setWalletBalance(prev => prev - amount);

      alert(`₹${amount.toLocaleString()} withdrawn successfully`);
    }

    setWalletAmount("");

    setShowModal(false);
  };

  // =========================
  // BUY / SELL ACTIONS
  // =========================

  const handleTradeAction = () => {

    if (!symbol || !quantity || !price) {

      alert("Please fill all fields");

      return;
    }

    const total = Number(quantity) * Number(price);

    // BUY
    if (modalAction === "BUY") {

      if (total > walletBalance) {

        alert("Insufficient wallet balance");

        return;
      }

      setWalletBalance(prev => prev - total);

      alert(
        `BUY order placed for ${quantity} shares of ${symbol}`
      );
    }

    // SELL
    else {

      setWalletBalance(prev => prev + total);

      alert(
        `SELL order placed for ${quantity} shares of ${symbol}`
      );
    }

    setSymbol("");
    setQuantity("");
    setPrice("");

    setShowModal(false);
  };

  return (

    <div className="space-y-6 animate-fade-in">

      {/* ========================= */}
      {/* HEADER */}
      {/* ========================= */}

      <div className="flex items-end justify-between">

        <div>

          <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
            Virtual Portfolio
          </h1>

          <p className="text-sm text-datis-text-muted mt-1">
            AI-powered virtual paper trading platform
          </p>

        </div>

        {/* ACTION BUTTONS */}

        <div className="flex gap-2">

          {/* ADD MONEY */}

          <button
            onClick={() => {
              setModalAction("DEPOSIT");
              setShowModal(true);
            }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl",
              "bg-datis-cyan/10 border border-datis-cyan/20",
              "text-datis-cyan font-display font-semibold text-sm",
              "hover:bg-datis-cyan/15 transition-all"
            )}
          >
            <Wallet className="w-4 h-4" />
            Add Money
          </button>

          {/* WITHDRAW */}

          <button
            onClick={() => {
              setModalAction("WITHDRAW");
              setShowModal(true);
            }}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-xl",
              "bg-amber-500/10 border border-amber-500/20",
              "text-amber-400 font-display font-semibold text-sm",
              "hover:bg-amber-500/15 transition-all"
            )}
          >
            <DollarSign className="w-4 h-4" />
            Withdraw
          </button>

          {/* BUY */}

          <button
            onClick={() => {
              setModalAction("BUY");
              setShowModal(true);
            }}
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

          {/* SELL */}

          <button
            onClick={() => {
              setModalAction("SELL");
              setShowModal(true);
            }}
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

      {/* ========================= */}
      {/* SUMMARY METRICS */}
      {/* ========================= */}

      <div className="grid grid-cols-5 gap-4">

        <MetricCard
          title="Total Value"
          value={`₹${portfolio.totalValue.toLocaleString("en-IN")}`}
          icon={Wallet}
          glowColor="cyan"
        />

        <MetricCard
          title="Wallet Balance"
          value={`₹${walletBalance.toLocaleString("en-IN")}`}
          icon={DollarSign}
          glowColor="purple"
        />

        <MetricCard
          title="Total P&L"
          value={`₹${portfolio.totalPnl.toLocaleString("en-IN")}`}
          icon={
            portfolio.totalPnl >= 0
              ? TrendingUp
              : TrendingDown
          }
          trend={
            portfolio.totalPnl >= 0
              ? "up"
              : "down"
          }
          trendValue={`${portfolio.totalPnlPercent.toFixed(2)}%`}
          glowColor={
            portfolio.totalPnl >= 0
              ? "green"
              : "red"
          }
        />

        <MetricCard
          title="ROI"
          value={`${portfolio.roi.toFixed(2)}%`}
          icon={TrendingUp}
          trend={
            portfolio.roi >= 0
              ? "up"
              : "down"
          }
          trendValue="Since inception"
          glowColor={
            portfolio.roi >= 0
              ? "green"
              : "red"
          }
        />

        <MetricCard
          title="Invested"
          value={`₹${portfolio.investedValue.toLocaleString("en-IN")}`}
          icon={PieIcon}
          subtitle="Initial capital"
          glowColor="amber"
        />

      </div>

      {/* Existing Holdings + Charts + History remain SAME */}

      {/* ========================= */}
      {/* MODAL */}
      {/* ========================= */}

      {showModal && (

        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm animate-fade-in">

          <div className="glass-card rounded-2xl w-full max-w-md p-6 relative border border-datis-border shadow-2xl">

            {/* CLOSE BUTTON */}

            <button
              onClick={() => setShowModal(false)}
              className="absolute top-4 right-4 p-1 rounded-lg hover:bg-white/10 transition-colors"
            >
              <X className="w-4 h-4 text-datis-text-muted" />
            </button>

            {/* TITLE */}

            <h3 className="font-display font-bold text-lg text-datis-text mb-6">

              {
                modalAction === "BUY"
                  ? "Buy Stock"
                  : modalAction === "SELL"
                  ? "Sell Stock"
                  : modalAction === "DEPOSIT"
                  ? "Add Money"
                  : "Withdraw Money"
              }

            </h3>

            {/* ========================= */}
            {/* WALLET MODAL */}
            {/* ========================= */}

            {(modalAction === "DEPOSIT" ||
              modalAction === "WITHDRAW") ? (

              <div className="space-y-4">

                <div>

                  <label className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-2">
                    Amount (₹)
                  </label>

                  <input
                    type="number"
                    placeholder="Enter amount"
                    value={walletAmount}
                    onChange={(e) =>
                      setWalletAmount(e.target.value)
                    }
                    className="w-full px-4 py-2.5 rounded-xl bg-datis-bg/80 border border-datis-border text-datis-text text-sm font-data outline-none focus:border-datis-cyan/50 transition-colors"
                  />

                </div>

                <button
                  onClick={handleWalletAction}
                  className={cn(
                    "w-full py-3 rounded-xl font-display font-bold text-sm uppercase tracking-wider transition-all",
                    modalAction === "DEPOSIT"
                      ? "bg-gradient-to-r from-datis-cyan to-cyan-500 text-white"
                      : "bg-gradient-to-r from-amber-500 to-yellow-500 text-white"
                  )}
                >
                  {
                    modalAction === "DEPOSIT"
                      ? "Add Funds"
                      : "Withdraw Funds"
                  }
                </button>

              </div>

            ) : (

              /* ========================= */
              /* BUY / SELL MODAL */
              /* ========================= */

              <div className="space-y-4">

                <div>

                  <label className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted block mb-2">
                    Symbol
                  </label>

                  <input
                    type="text"
                    placeholder="e.g. RELIANCE"
                    value={symbol}
                    onChange={(e) =>
                      setSymbol(e.target.value)
                    }
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
                    value={quantity}
                    onChange={(e) =>
                      setQuantity(e.target.value)
                    }
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
                    value={price}
                    onChange={(e) =>
                      setPrice(e.target.value)
                    }
                    className="w-full px-4 py-2.5 rounded-xl bg-datis-bg/80 border border-datis-border text-datis-text text-sm font-data outline-none focus:border-datis-cyan/50 transition-colors"
                  />

                </div>

                <button
                  onClick={handleTradeAction}
                  className={cn(
                    "w-full py-3 rounded-xl font-display font-bold text-sm uppercase tracking-wider transition-all",
                    modalAction === "BUY"
                      ? "bg-gradient-to-r from-datis-green to-datis-green-dim text-white hover:shadow-lg hover:shadow-datis-green/30"
                      : "bg-gradient-to-r from-datis-red to-datis-red-dim text-white hover:shadow-lg hover:shadow-datis-red/30"
                  )}
                >
                  {
                    modalAction === "BUY"
                      ? "Place Buy Order"
                      : "Place Sell Order"
                  }
                </button>

              </div>

            )}

          </div>

        </div>

      )}

    </div>
  );
}