import { AlertTriangle, Inbox, Loader2 } from "lucide-react";
import type { ReactNode } from "react";

export function Spinner({ label = "Loading…" }: { label?: string }) {
  return (
    <div className="flex items-center justify-center gap-2 py-12 text-sm text-slate-500" role="status">
      <Loader2 className="h-5 w-5 animate-spin" />
      {label}
    </div>
  );
}

export function ErrorMessage({ error, onRetry }: { error: Error | string; onRetry?: () => void }) {
  return (
    <div
      className="flex items-center justify-between gap-3 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700 dark:border-red-900 dark:bg-red-950/40 dark:text-red-300"
      role="alert"
    >
      <span className="flex items-center gap-2">
        <AlertTriangle className="h-4 w-4 shrink-0" />
        {typeof error === "string" ? error : error.message}
      </span>
      {onRetry && (
        <button className="btn-secondary py-1" onClick={onRetry}>
          Retry
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title, children }: { title: string; children?: ReactNode }) {
  return (
    <div className="flex flex-col items-center gap-2 px-4 py-14 text-center text-slate-500">
      <Inbox className="h-10 w-10 text-slate-300 dark:text-slate-600" />
      <p className="font-medium text-slate-700 dark:text-slate-300">{title}</p>
      {children}
    </div>
  );
}
