import { Link } from "wouter";
import { Home, AlertTriangle, ArrowLeft } from "lucide-react";
import { cn } from "@/lib/utils";

export default function NotFound() {
  return (
    <div className="min-h-[70vh] flex items-center justify-center animate-fade-in">
      <div className="text-center max-w-lg">
        {/* Animated 404 */}
        <div className="relative inline-flex items-center justify-center mb-8">
          <div className="text-[120px] font-display font-black text-transparent bg-clip-text bg-gradient-to-br from-datis-cyan via-datis-purple to-datis-cyan-dim leading-none">
            404
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-32 h-32 rounded-full border border-datis-cyan/10 animate-pulse-glow" />
          </div>
        </div>

        {/* Icon */}
        <div className="w-16 h-16 rounded-2xl bg-datis-amber/10 flex items-center justify-center mx-auto mb-6 animate-float">
          <AlertTriangle className="w-8 h-8 text-datis-amber" />
        </div>

        {/* Text */}
        <h2 className="text-2xl font-display font-bold text-datis-text mb-3">
          Signal Not Found
        </h2>
        <p className="text-sm text-datis-text-muted leading-relaxed mb-8 max-w-sm mx-auto">
          The page you're looking for doesn't exist in the DATIS network. It may have been moved, deleted, or the URL might be incorrect.
        </p>

        {/* Actions */}
        <div className="flex items-center justify-center gap-3">
          <Link href="/">
            <div
              className={cn(
                "flex items-center gap-2 px-6 py-3 rounded-xl",
                "bg-gradient-to-r from-datis-cyan to-datis-cyan-dim",
                "text-white font-display font-bold text-sm",
                "hover:shadow-lg hover:shadow-datis-cyan/30",
                "transition-all duration-300 cursor-pointer"
              )}
            >
              <Home className="w-4 h-4" />
              Back to Dashboard
            </div>
          </Link>
          <button
            onClick={() => window.history.back()}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-xl",
              "bg-datis-card border border-datis-border",
              "text-datis-text-secondary font-display font-semibold text-sm",
              "hover:border-datis-cyan/30 hover:bg-datis-card-hover",
              "transition-all duration-300"
            )}
          >
            <ArrowLeft className="w-4 h-4" />
            Go Back
          </button>
        </div>

        {/* Decorative grid */}
        <div className="mt-12 flex items-center justify-center gap-2 opacity-30">
          {Array.from({ length: 7 }).map((_, i) => (
            <div
              key={i}
              className="w-2 h-2 rounded-full bg-datis-cyan"
              style={{
                animationDelay: `${i * 0.15}s`,
                animation: "pulse-glow 2s ease-in-out infinite",
              }}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
