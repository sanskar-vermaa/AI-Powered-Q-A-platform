import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import { Avatar } from "../components/Avatar";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { useAsync } from "../hooks/useAsync";
import { useDebounce } from "../hooks/useDebounce";
import { compactNumber } from "../utils/format";

export function UsersPage() {
  const [filter, setFilter] = useState("");
  const q = useDebounce(filter, 300);
  const users = useAsync(() => api.users.list(q || undefined), [q]);

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Users</h1>
      <input
        className="input max-w-xs"
        placeholder="Filter by username"
        aria-label="Filter users"
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      {users.loading ? (
        <Spinner />
      ) : users.error ? (
        <ErrorMessage error={users.error} onRetry={users.reload} />
      ) : users.data?.length ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {users.data.map((u) => (
            <Link
              key={u.id}
              to={`/users/${u.username}`}
              className="card flex items-center gap-3 p-4 transition hover:border-brand-500"
            >
              <Avatar name={u.username} />
              <div className="min-w-0">
                <p className="truncate font-medium">{u.username}</p>
                <p className="text-xs text-slate-500">
                  {compactNumber(u.reputation)} reputation{u.role !== "user" && ` · ${u.role}`}
                </p>
              </div>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No users found" />
      )}
    </div>
  );
}
