import { useLocation, Link } from "wouter";
import { cn } from "@/lib/utils";
import {
  LayoutDashboard,
  BarChart3,
  FlaskConical,
  Wallet,
  Link2,
  Newspaper,
  AlertTriangle,
  HelpCircle,
  Settings,
  Terminal,
} from "lucide-react";

const NAV_ITEMS = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/analysis/RELIANCE", label: "Deep Analysis", icon: BarChart3 },
  { path: "/simulator", label: "Simulator", icon: FlaskConical },
  { path: "/portfolio", label: "Portfolio", icon: Wallet },
  { path: "/blockchain", label: "Blockchain", icon: Link2 },
  { path: "/social-news", label: "Social & News", icon: Newspaper },
  { path: "/failures", label: "Failures", icon: AlertTriangle },
];

export function Sidebar() {
  const [location] = useLocation();

  const isActive = (path: string) => {
    if (path === "/") return location === "/";
    return location.startsWith(path.split("/").slice(0, 2).join("/"));
  };

  return (
    <aside
      className={cn(
        "fixed left-0 top-0 h-screen w-64 z-40",
        "bg-datis-surface/95 backdrop-blur-xl",
        "border-r border-datis-border/50",
        "flex flex-col",
        "shadow-2xl shadow-black/30"
      )}
      id="sidebar"
    >
      {/* Logo */}
      <div className="p-6 pb-2">
        <Link href="/" className="flex items-center gap-3 group">
          <div
            className={cn(
              "w-9 h-9 rounded-xl flex items-center justify-center",
              "bg-gradient-to-br from-datis-cyan to-datis-cyan-dim",
              "shadow-lg shadow-datis-cyan/20",
              "group-hover:shadow-datis-cyan/40 transition-shadow duration-300"
            )}
          >
            <Terminal className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="text-base font-display font-bold tracking-tight text-datis-text">
              DATIS
            </div>
            <div className="text-[9px] font-display uppercase tracking-[0.2em] text-datis-text-muted">
              AI Trading Intel
            </div>
          </div>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-0.5 overflow-y-auto">
        <div className="px-3 mb-3">
          <span className="text-[10px] font-display font-semibold uppercase tracking-[0.15em] text-datis-text-muted">
            Navigation
          </span>
        </div>
        {NAV_ITEMS.map(({ path, label, icon: Icon }) => (
          <Link key={path} href={path}>
            <div
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all duration-200 cursor-pointer group",
                isActive(path)
                  ? "bg-datis-cyan/10 text-datis-cyan border-r-2 border-datis-cyan"
                  : "text-datis-text-secondary hover:bg-white/5 hover:text-datis-text"
              )}
            >
              <Icon
                className={cn(
                  "w-[18px] h-[18px] transition-colors",
                  isActive(path) ? "text-datis-cyan" : "text-datis-text-muted group-hover:text-datis-text-secondary"
                )}
              />
              <span className="text-sm font-display font-medium">{label}</span>
              {isActive(path) && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-datis-cyan animate-pulse-glow" />
              )}
            </div>
          </Link>
        ))}
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-datis-border/30 space-y-1">
        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-datis-text-muted hover:text-datis-text-secondary hover:bg-white/5 transition-colors">
          <HelpCircle className="w-4 h-4" />
          <span className="text-sm font-display">Support</span>
        </button>
        <button className="flex items-center gap-3 w-full px-3 py-2 rounded-xl text-datis-text-muted hover:text-datis-text-secondary hover:bg-white/5 transition-colors">
          <Settings className="w-4 h-4" />
          <span className="text-sm font-display">Settings</span>
        </button>
        <div className="pt-3 px-3">
          <div className="text-[9px] text-datis-text-muted font-display uppercase tracking-wider">
            DATIS v2.0 • Build 2026.4
          </div>
        </div>
      </div>
    </aside>
  );
}
