import { useState } from "react";
import {
  Newspaper,
  Search,
  Send,
  Brain,
  Shield,
  Target,
  AlertTriangle,
  TrendingUp,
  Lightbulb,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { usePostSocialAnalysis } from "@/hooks/use-api";
import { SignalBadge, ProgressRing } from "@/components/ui-cards";

const EXAMPLE_TEXTS = [
  "Reliance Jio announces record subscriber growth of 15 million in Q4, with ARPU increasing to ₹183. Strong momentum in 5G rollout across tier-2 cities.",
  "Markets crash 3% as US Fed signals aggressive rate hikes. Foreign investors pull ₹8,000 crore from Indian markets in panic selling.",
  "TCS wins $2.5 billion deal from major European bank for digital transformation. Largest deal in Indian IT history signals strong demand.",
  "RBI keeps repo rate unchanged at 6.5%, inflation remains within target band. Banking stocks rally on policy stability.",
];

export default function SocialNews() {
  const [text, setText] = useState("");
  const { data: result, mutate: analyze, isPending } = usePostSocialAnalysis();

  const handleAnalyze = () => {
    if (text.trim()) {
      analyze({ text });
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-display font-bold text-datis-text tracking-tight">
          Social & News Intelligence
        </h1>
        <p className="text-sm text-datis-text-muted mt-1">
          AI-powered sentiment analysis on news articles and social media content
        </p>
      </div>

      {/* Two Column Layout */}
      <div className="grid grid-cols-12 gap-6">
        {/* Left: Input */}
        <div className="col-span-5 space-y-4">
          <div className="glass-card rounded-xl p-5">
            <div className="flex items-center gap-2 mb-4">
              <Newspaper className="w-4 h-4 text-datis-cyan" />
              <h2 className="font-display font-semibold text-sm text-datis-text uppercase tracking-wider">
                Analyze Content
              </h2>
            </div>

            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Paste a news article, social media post, or market commentary here..."
              className={cn(
                "w-full h-48 px-4 py-3 rounded-xl resize-none",
                "bg-datis-bg/60 border border-datis-border",
                "text-sm text-datis-text placeholder:text-datis-text-muted",
                "outline-none focus:border-datis-cyan/40 transition-colors",
                "font-sans leading-relaxed"
              )}
            />

            <button
              onClick={handleAnalyze}
              disabled={!text.trim() || isPending}
              className={cn(
                "w-full mt-3 flex items-center justify-center gap-2 py-3 rounded-xl",
                "bg-gradient-to-r from-datis-cyan to-datis-cyan-dim",
                "text-white font-display font-bold text-sm uppercase tracking-wider",
                "hover:shadow-lg hover:shadow-datis-cyan/30",
                "transition-all duration-300 active:scale-[0.98]",
                "disabled:opacity-50 disabled:cursor-not-allowed"
              )}
            >
              {isPending ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Analyze with AI
                </>
              )}
            </button>
          </div>

          {/* Example Texts */}
          <div className="glass-card rounded-xl p-5">
            <div className="flex items-center gap-2 mb-3">
              <Lightbulb className="w-4 h-4 text-datis-amber" />
              <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                Example Texts
              </span>
            </div>
            <div className="space-y-2">
              {EXAMPLE_TEXTS.map((ex, i) => (
                <button
                  key={i}
                  onClick={() => setText(ex)}
                  className={cn(
                    "w-full text-left p-3 rounded-xl",
                    "bg-datis-bg/40 border border-datis-border/50",
                    "hover:border-datis-cyan/20 hover:bg-datis-card-hover",
                    "transition-all duration-200 group"
                  )}
                >
                  <p className="text-xs text-datis-text-secondary leading-relaxed line-clamp-2 group-hover:text-datis-text">
                    {ex}
                  </p>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right: Results */}
        <div className="col-span-7">
          {result ? (
            <div className="space-y-4 animate-slide-up">
              {/* Sentiment & Credibility */}
              <div className="grid grid-cols-3 gap-4">
                <div className="glass-card rounded-xl p-5 flex flex-col items-center text-center">
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-3">
                    Sentiment
                  </span>
                  <SignalBadge signal={result.sentiment} size="lg" />
                  <div className="font-data text-2xl font-bold text-datis-text mt-3">
                    {(result.sentimentScore * 100).toFixed(0)}%
                  </div>
                </div>
                <div className="glass-card rounded-xl p-5 flex flex-col items-center text-center">
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-3">
                    Credibility
                  </span>
                  <ProgressRing
                    value={result.credibility}
                    size={80}
                    strokeWidth={6}
                    color={result.credibility > 75 ? "#22C55E" : result.credibility > 50 ? "#F59E0B" : "#EF4444"}
                  />
                </div>
                <div className="glass-card rounded-xl p-5 flex flex-col items-center text-center">
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted mb-3">
                    Impact
                  </span>
                  <ProgressRing
                    value={result.impactScore}
                    size={80}
                    strokeWidth={6}
                    color="#06B6D4"
                  />
                </div>
              </div>

              {/* AI Signal */}
              <div className="glass-card rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Brain className="w-4 h-4 text-datis-cyan" />
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                    AI Signal
                  </span>
                </div>
                <p className="text-sm text-datis-text leading-relaxed">{result.aiSignal}</p>
              </div>

              {/* Keywords */}
              <div className="glass-card rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Search className="w-4 h-4 text-datis-purple" />
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                    Key Terms Detected
                  </span>
                </div>
                <div className="flex flex-wrap gap-2">
                  {result.keywords.map((kw) => (
                    <span
                      key={kw}
                      className="px-3 py-1.5 rounded-lg bg-datis-purple/10 border border-datis-purple/20 text-datis-purple text-xs font-display font-semibold uppercase"
                    >
                      {kw}
                    </span>
                  ))}
                </div>
              </div>

              {/* Risks & Opportunities */}
              <div className="grid grid-cols-2 gap-4">
                <div className="glass-card rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <AlertTriangle className="w-4 h-4 text-datis-red" />
                    <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                      Risks
                    </span>
                  </div>
                  <div className="space-y-2">
                    {result.risks.map((r, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <div className="w-1 h-1 rounded-full bg-datis-red mt-2 flex-shrink-0" />
                        <p className="text-xs text-datis-text-secondary leading-relaxed">{r}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="glass-card rounded-xl p-5">
                  <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-datis-green" />
                    <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                      Opportunities
                    </span>
                  </div>
                  <div className="space-y-2">
                    {result.opportunities.map((o, i) => (
                      <div key={i} className="flex items-start gap-2">
                        <div className="w-1 h-1 rounded-full bg-datis-green mt-2 flex-shrink-0" />
                        <p className="text-xs text-datis-text-secondary leading-relaxed">{o}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Explanation */}
              <div className="glass-card rounded-xl p-5">
                <div className="flex items-center gap-2 mb-3">
                  <Shield className="w-4 h-4 text-datis-amber" />
                  <span className="text-[11px] font-display font-semibold uppercase tracking-wider text-datis-text-muted">
                    AI Explanation
                  </span>
                </div>
                <p className="text-sm text-datis-text-secondary leading-relaxed italic">
                  "{result.explanation}"
                </p>
              </div>
            </div>
          ) : (
            <div className="glass-card rounded-xl p-16 flex flex-col items-center justify-center text-center h-full">
              <div className="w-16 h-16 rounded-2xl bg-datis-cyan/10 flex items-center justify-center mb-6 animate-float">
                <Brain className="w-8 h-8 text-datis-cyan" />
              </div>
              <h3 className="font-display font-bold text-lg text-datis-text mb-2">
                Paste & Analyze
              </h3>
              <p className="text-sm text-datis-text-muted max-w-sm">
                Paste any news article, tweet, or market commentary on the left. Our AI will analyze sentiment, credibility, and market impact.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
