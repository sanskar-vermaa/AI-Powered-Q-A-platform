import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import type { Flag } from "../api/types";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { useToast } from "../context/ToastContext";
import { useAsync } from "../hooks/useAsync";
import { timeAgo } from "../utils/format";

function targetLink(flag: Flag): string | null {
  if (flag.target_type === "question") return `/questions/${flag.target_id}`;
  return null;
}

export function ModerationPage() {
  const toast = useToast();
  const [status, setStatus] = useState("open");
  const flags = useAsync(() => api.moderation.queue(status), [status]);

  async function resolve(flag: Flag, next: "resolved" | "dismissed", deleteContent = false) {
    if (deleteContent && !confirm(`Delete this ${flag.target_type}? This cannot be undone.`)) return;
    try {
      await api.moderation.resolve(flag.id, next, deleteContent);
      toast.success(`Flag ${next}`);
      flags.reload();
    } catch (error) {
      toast.error(error);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h1 className="text-2xl font-bold">Moderation queue</h1>
        <select
          className="input w-auto"
          value={status}
          onChange={(e) => setStatus(e.target.value)}
          aria-label="Flag status"
        >
          <option value="open">Open</option>
          <option value="resolved">Resolved</option>
          <option value="dismissed">Dismissed</option>
          <option value="all">All</option>
        </select>
      </div>
      {flags.loading ? (
        <Spinner />
      ) : flags.error ? (
        <ErrorMessage error={flags.error} onRetry={flags.reload} />
      ) : flags.data?.length ? (
        <div className="space-y-3">
          {flags.data.map((flag) => {
            const link = targetLink(flag);
            return (
              <div key={flag.id} className="card flex flex-wrap items-center gap-4 p-4">
                <div className="min-w-0 flex-1 text-sm">
                  <p className="font-medium">
                    {flag.reason.replace("_", " ")} · {flag.target_type} #{flag.target_id}{" "}
                    {link && (
                      <Link to={link} className="text-brand-600 hover:underline">
                        view
                      </Link>
                    )}
                  </p>
                  {flag.details && <p className="mt-1 text-slate-600 dark:text-slate-400">“{flag.details}”</p>}
                  <p className="mt-1 text-xs text-slate-500">
                    Reported by {flag.reporter.username} {timeAgo(flag.created_at)} · {flag.status}
                  </p>
                </div>
                {flag.status === "open" && (
                  <div className="flex gap-2">
                    <button className="btn-secondary" onClick={() => resolve(flag, "dismissed")}>
                      Dismiss
                    </button>
                    <button className="btn-secondary" onClick={() => resolve(flag, "resolved")}>
                      Resolve
                    </button>
                    <button className="btn-danger" onClick={() => resolve(flag, "resolved", true)}>
                      Delete content
                    </button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      ) : (
        <EmptyState title="Nothing to review" />
      )}
    </div>
  );
}
