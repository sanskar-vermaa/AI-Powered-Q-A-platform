import { Bookmark, Home, MessageSquareText, Shield, Sparkles, Tags, Trophy, Users } from "lucide-react";
import type { ComponentType } from "react";
import { NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

interface Item {
  to: string;
  label: string;
  icon: ComponentType<{ className?: string }>;
  auth?: boolean;
  staff?: boolean;
}

const ITEMS: Item[] = [
  { to: "/", label: "Home", icon: Home },
  { to: "/questions", label: "Questions", icon: MessageSquareText },
  { to: "/tags", label: "Tags", icon: Tags },
  { to: "/users", label: "Users", icon: Users },
  { to: "/leaderboard", label: "Leaderboard", icon: Trophy },
  { to: "/assistant", label: "AI Assistant", icon: Sparkles, auth: true },
  { to: "/bookmarks", label: "Bookmarks", icon: Bookmark, auth: true },
  { to: "/moderation", label: "Moderation", icon: Shield, staff: true },
];

export function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const { user } = useAuth();
  const visible = ITEMS.filter((item) => (!item.auth || user) && (!item.staff || (user && user.role !== "user")));
  return (
    <nav className="flex flex-col gap-1" aria-label="Main">
      {visible.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === "/"}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition ${
              isActive
                ? "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-100"
                : "text-slate-600 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-800"
            }`
          }
        >
          <Icon className="h-4 w-4" />
          {label}
        </NavLink>
      ))}
    </nav>
  );
}
