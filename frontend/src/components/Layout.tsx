import { X } from "lucide-react";
import { useState } from "react";
import { Link, Outlet } from "react-router-dom";

import { Navbar } from "./Navbar";
import { Sidebar } from "./Sidebar";

export function Layout() {
  const [drawer, setDrawer] = useState(false);
  return (
    <div className="flex min-h-screen flex-col">
      <Navbar onMenu={() => setDrawer(true)} />
      {drawer && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/40" onClick={() => setDrawer(false)} />
          <aside className="absolute inset-y-0 left-0 w-64 bg-white p-4 shadow-xl dark:bg-slate-950">
            <button className="btn-ghost mb-4 px-2" onClick={() => setDrawer(false)} aria-label="Close navigation">
              <X className="h-5 w-5" />
            </button>
            <Sidebar onNavigate={() => setDrawer(false)} />
          </aside>
        </div>
      )}
      <div className="mx-auto flex w-full max-w-7xl flex-1 gap-6 px-4 py-6">
        <aside className="sticky top-22 hidden h-fit w-52 shrink-0 lg:block">
          <Sidebar />
        </aside>
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
      <footer className="border-t border-slate-200 py-8 text-sm text-slate-500 dark:border-slate-800">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-4">
          <p>© {new Date().getFullYear()} AskAI. Community answers, powered by AI.</p>
          <div className="flex gap-4">
            <Link to="/questions" className="hover:text-brand-600">
              Questions
            </Link>
            <Link to="/tags" className="hover:text-brand-600">
              Tags
            </Link>
            <a href="/docs" className="hover:text-brand-600">
              API docs
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
