import { Trophy } from "lucide-react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import { Avatar } from "../components/Avatar";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { useAsync } from "../hooks/useAsync";
import { compactNumber } from "../utils/format";

const MEDALS = ["text-amber-400", "text-slate-400", "text-orange-500"];

export function LeaderboardPage() {
  const board = useAsync(() => api.stats.leaderboard(25), []);
  return (
    <div className="space-y-4">
      <h1 className="flex items-center gap-2 text-2xl font-bold">
        <Trophy className="h-6 w-6 text-amber-500" /> Leaderboard
      </h1>
      <div className="card overflow-hidden">
        {board.loading ? (
          <Spinner />
        ) : board.error ? (
          <div className="p-4">
            <ErrorMessage error={board.error} onRetry={board.reload} />
          </div>
        ) : board.data?.length ? (
          <table className="w-full text-sm">
            <thead className="bg-slate-50 text-left text-xs uppercase text-slate-500 dark:bg-slate-800/50">
              <tr>
                <th className="px-4 py-3">Rank</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3 text-right">Answers</th>
                <th className="px-4 py-3 text-right">Reputation</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 dark:divide-slate-800">
              {board.data.map((entry, index) => (
                <tr key={entry.username}>
                  <td className="px-4 py-3 font-semibold">
                    {index < 3 ? (
                      <Trophy className={`h-4 w-4 ${MEDALS[index]}`} aria-label={`#${index + 1}`} />
                    ) : (
                      index + 1
                    )}
                  </td>
                  <td className="px-4 py-3">
                    <Link
                      to={`/users/${entry.username}`}
                      className="flex items-center gap-2 font-medium hover:text-brand-600"
                    >
                      <Avatar name={entry.username} size="sm" /> {entry.username}
                    </Link>
                  </td>
                  <td className="px-4 py-3 text-right">{compactNumber(entry.answer_count)}</td>
                  <td className="px-4 py-3 text-right font-semibold">{compactNumber(entry.reputation)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <EmptyState title="No users yet" />
        )}
      </div>
    </div>
  );
}
