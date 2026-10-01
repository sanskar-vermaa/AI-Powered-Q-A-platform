import { Bell, LogOut, Menu, Moon, Search, Sparkles, Sun, User as UserIcon } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";

import { api } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { useTheme } from "../context/ThemeContext";
import { Avatar } from "./Avatar";

export function Navbar({ onMenu }: { onMenu: () => void }) {
  const { user, logout } = useAuth();
  const { theme, toggle } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [search, setSearch] = useState("");
  const [unread, setUnread] = useState(0);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    if (!user) return;
    let active = true;
    const load = () =>
      api.notifications
        .unreadCount()
        .then((r) => active && setUnread(r.unread))
        .catch(() => undefined);
    load();
    const timer = setInterval(load, 30000);
    return () => {
      active = false;
      clearInterval(timer);
    };
  }, [user, location.pathname]);

  useEffect(() => setMenuOpen(false), [location.pathname]);

  function submit(event: FormEvent) {
    event.preventDefault();
    navigate(`/questions?q=${encodeURIComponent(search.trim())}`);
  }

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
      <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-4">
        <button className="btn-ghost px-2 lg:hidden" onClick={onMenu} aria-label="Open navigation">
          <Menu className="h-5 w-5" />
        </button>
        <Link to="/" className="flex items-center gap-2 text-lg font-bold">
          <img src="/favicon.svg" alt="" className="h-8 w-8" />
          <span>
            Ask<span className="text-brand-600">AI</span>
          </span>
        </Link>

        <form onSubmit={submit} className="relative mx-auto hidden w-full max-w-xl md:block" role="search">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Search questions…"
            aria-label="Search questions"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
        </form>

        <div className="ml-auto flex items-center gap-1">
          <button className="btn-ghost px-2" onClick={toggle} aria-label="Toggle dark mode">
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
          {user ? (
            <>
              <Link to="/assistant" className="btn-ghost hidden px-2 sm:inline-flex" aria-label="AI assistant">
                <Sparkles className="h-5 w-5 text-violet-500" />
              </Link>
              <Link to="/notifications" className="btn-ghost relative px-2" aria-label="Notifications">
                <Bell className="h-5 w-5" />
                {unread > 0 && (
                  <span className="absolute -right-0.5 -top-0.5 min-w-[1.1rem] rounded-full bg-red-500 px-1 text-center text-[10px] font-bold leading-[1.1rem] text-white">
                    {unread > 99 ? "99+" : unread}
                  </span>
                )}
              </Link>
              <div className="relative">
                <button
                  className="flex items-center gap-2 rounded-full p-1 hover:bg-slate-100 dark:hover:bg-slate-800"
                  onClick={() => setMenuOpen((o) => !o)}
                  aria-label="Account menu"
                >
                  <Avatar name={user.username} />
                </button>
                {menuOpen && (
                  <div className="card absolute right-0 mt-2 w-56 overflow-hidden py-1 text-sm shadow-lg">
                    <div className="border-b border-slate-100 px-4 py-2 dark:border-slate-800">
                      <p className="font-semibold">{user.username}</p>
                      <p className="text-xs text-slate-500">{user.reputation} reputation</p>
                    </div>
                    <Link
                      to={`/users/${user.username}`}
                      className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 dark:hover:bg-slate-800"
                    >
                      <UserIcon className="h-4 w-4" /> Profile
                    </Link>
                    <Link
                      to="/settings"
                      className="flex items-center gap-2 px-4 py-2 hover:bg-slate-50 dark:hover:bg-slate-800"
                    >
                      Settings
                    </Link>
                    <button
                      className="flex w-full items-center gap-2 px-4 py-2 text-left text-red-600 hover:bg-slate-50 dark:hover:bg-slate-800"
                      onClick={() => {
                        logout();
                        navigate("/");
                      }}
                    >
                      <LogOut className="h-4 w-4" /> Log out
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-ghost">
                Log in
              </Link>
              <Link to="/register" className="btn-primary">
                Sign up
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
