import {
  Link2,
  Shield,
  CheckCircle2,
  Clock,
  XCircle,
  ExternalLink,
  Award,
  Hash,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useGetBlockchainLogs } from "@/hooks/use-api";
import { SignalBadge, ProgressRing } from "@/components/ui-cards";
import { truncateHash } from "@/lib/utils";

export default function Blockchain() {
  const { data: logs } = useGetBlockchainLogs();

  if (!logs) return null;

  const verified = logs.filter((l) => l.status === "VERIFIED").length;
  const totalNfts = logs.filter((l) => l.nftMinted).length;
  const avgTrust = logs.reduce((sum, l) => sum + l.trustChainScore, 0) / logs.length;

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
          Blockchain Verification
        </h1>
        <p className="text-sm text-datis-text-muted mt-1">
          On-chain prediction ledger with trust chain verification
        </p>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-green/10">
            <CheckCircle2 className="w-5 h-5 text-datis-green" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Verified
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{verified}/{logs.length}</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-purple/10">
            <Award className="w-5 h-5 text-datis-purple" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              NFT Predictions
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{totalNfts}</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-cyan/10">
            <Shield className="w-5 h-5 text-datis-cyan" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Avg Trust Score
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">{avgTrust.toFixed(0)}</div>
          </div>
        </div>
        <div className="glass-card rounded-xl p-5 flex items-center gap-4">
          <div className="p-3 rounded-xl bg-datis-amber/10">
            <Hash className="w-5 h-5 text-datis-amber" />
          </div>
          <div>
            <div className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
              Latest Block
            </div>
            <div className="font-data text-2xl font-bold text-datis-text">
              #{logs[0]?.blockNumber.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Prediction Ledger */}
      <div className="glass-card rounded-xl overflow-hidden">
        <div className="px-5 py-4 border-b border-datis-border/50 flex items-center gap-2">
          <Link2 className="w-4 h-4 text-datis-cyan" />
          <h3 className="font-display font-semibold text-sm text-datis-text">Prediction Ledger</h3>
        </div>
        <div className="divide-y divide-datis-border/20">
          {logs.map((log) => (
            <div
              key={log.id}
              className="px-5 py-4 hover:bg-datis-cyan/5 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    {log.status === "VERIFIED" ? (
                      <CheckCircle2 className="w-4 h-4 text-datis-green" />
                    ) : log.status === "PENDING" ? (
                      <Clock className="w-4 h-4 text-datis-amber" />
                    ) : (
                      <XCircle className="w-4 h-4 text-datis-red" />
                    )}
                    <span className="font-display font-semibold text-sm text-datis-text">
                      {log.prediction}
                    </span>
                    <SignalBadge signal={log.status} size="sm" />
                    {log.nftMinted && (
                      <span className="flex items-center gap-1 px-2 py-0.5 rounded-lg bg-datis-purple/10 border border-datis-purple/20 text-datis-purple text-[10px] font-display font-bold uppercase">
                        <Award className="w-3 h-3" />
                        NFT
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-6 text-xs text-datis-text-muted">
                    <span className="font-data flex items-center gap-1">
                      <Hash className="w-3 h-3" />
                      Block {log.blockNumber.toLocaleString()}
                    </span>
                    <span className="font-data">
                      TX: {truncateHash(log.txHash)}
                    </span>
                    <span className="font-data">
                      {new Date(log.timestamp).toLocaleString("en-IN")}
                    </span>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <ProgressRing
                    value={log.trustChainScore}
                    size={50}
                    strokeWidth={4}
                    color={
                      log.trustChainScore > 85
                        ? "#22C55E"
                        : log.trustChainScore > 70
                          ? "#F59E0B"
                          : "#EF4444"
                    }
                  />
                  <div className="text-right">
                    <div className="font-data text-sm font-bold text-datis-text">
                      {log.confidence.toFixed(1)}%
                    </div>
                    <div className="text-[10px] text-datis-text-muted font-display uppercase">
                      Confidence
                    </div>
                  </div>
                  <button className="p-2 rounded-lg hover:bg-white/5 transition-colors">
                    <ExternalLink className="w-4 h-4 text-datis-text-muted" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Trust Chain Visualization */}
      <div className="glass-card rounded-xl p-6">
        <h3 className="font-display font-semibold text-sm text-datis-text mb-4">
          Trust Chain
        </h3>
        <div className="flex items-center justify-between gap-2 overflow-x-auto pb-2">
          {logs.map((log, index) => (
            <div key={log.id} className="flex items-center gap-2 flex-shrink-0">
              <div
                className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center text-xs font-data font-bold border-2",
                  log.status === "VERIFIED"
                    ? "bg-datis-green/10 border-datis-green/30 text-datis-green"
                    : log.status === "PENDING"
                      ? "bg-datis-amber/10 border-datis-amber/30 text-datis-amber"
                      : "bg-datis-red/10 border-datis-red/30 text-datis-red"
                )}
              >
                {log.trustChainScore}
              </div>
              {index < logs.length - 1 && (
                <div className="w-8 h-0.5 bg-gradient-to-r from-datis-cyan/40 to-datis-cyan/10" />
              )}
            </div>
          ))}
        </div>
        <div className="flex items-center gap-4 mt-4 text-xs text-datis-text-muted">
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-datis-green" />
            <span>Verified</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-datis-amber" />
            <span>Pending</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2 h-2 rounded-full bg-datis-red" />
            <span>Failed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
