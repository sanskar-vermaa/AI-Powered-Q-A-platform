import { Award, Bot, CheckCircle2, MessageCircle, MessageSquareText } from "lucide-react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import type { Notification } from "../api/types";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { useToast } from "../context/ToastContext";
import { useAsync } from "../hooks/useAsync";
import { timeAgo } from "../utils/format";

const ICONS: Record<string, typeof MessageCircle> = {
  answer: MessageSquareText,
  comment: MessageCircle,
  accepted: CheckCircle2,
  badge: Award,
  ai_answer: Bot,
};

export function NotificationsPage() {
  const toast = useToast();
  const notifications = useAsync(() => api.notifications.list(), []);

  async function markAll() {
    try {
      await api.notifications.markAllRead();
      notifications.setData((current) => (current ?? []).map((n) => ({ ...n, is_read: true })));
    } catch (error) {
      toast.error(error);
    }
  }

  function open(notification: Notification) {
    if (!notification.is_read) {
      api.notifications.markRead(notification.id).catch(() => undefined);
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Notifications</h1>
        <button className="btn-secondary" onClick={markAll} disabled={!notifications.data?.some((n) => !n.is_read)}>
          Mark all as read
        </button>
      </div>
      <div className="card divide-y divide-slate-200 dark:divide-slate-800">
        {notifications.loading ? (
          <Spinner />
        ) : notifications.error ? (
          <div className="p-4">
            <ErrorMessage error={notifications.error} onRetry={notifications.reload} />
          </div>
        ) : notifications.data?.length ? (
          notifications.data.map((n) => {
            const Icon = ICONS[n.kind] ?? MessageCircle;
            return (
              <Link
                key={n.id}
                to={n.link || "#"}
                onClick={() => open(n)}
                className={`flex items-start gap-3 p-4 hover:bg-slate-50 dark:hover:bg-slate-800/50 ${n.is_read ? "" : "bg-brand-50/60 dark:bg-brand-500/5"}`}
              >
                <Icon className="mt-0.5 h-5 w-5 shrink-0 text-brand-600" />
                <div className="flex-1 text-sm">
                  <p className={n.is_read ? "text-slate-600 dark:text-slate-400" : "font-medium"}>{n.message}</p>
                  <p className="mt-0.5 text-xs text-slate-500">{timeAgo(n.created_at)}</p>
                </div>
                {!n.is_read && <span className="mt-1.5 h-2 w-2 rounded-full bg-brand-600" aria-label="unread" />}
              </Link>
            );
          })
        ) : (
          <EmptyState title="You're all caught up" />
        )}
      </div>
    </div>
  );
}
