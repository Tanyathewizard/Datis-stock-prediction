import { Moon, Sun } from "lucide-react";
import { useTheme } from "./theme-provider";
import { cn } from "@/lib/utils";

export function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className={cn(
        "relative flex items-center justify-center w-9 h-9 rounded-lg",
        "bg-datis-card border border-datis-border",
        "hover:border-datis-cyan/40 hover:bg-datis-card-hover",
        "transition-all duration-300 group"
      )}
      aria-label="Toggle theme"
      id="theme-toggle"
    >
      {theme === "dark" ? (
        <Sun className="w-4 h-4 text-datis-amber group-hover:text-datis-amber transition-colors" />
      ) : (
        <Moon className="w-4 h-4 text-datis-purple group-hover:text-datis-cyan transition-colors" />
      )}
    </button>
  );
}
