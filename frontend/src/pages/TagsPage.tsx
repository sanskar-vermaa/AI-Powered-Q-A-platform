import { Search } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { useAsync } from "../hooks/useAsync";
import { useDebounce } from "../hooks/useDebounce";
import { pluralize } from "../utils/format";

export function TagsPage() {
  const [filter, setFilter] = useState("");
  const [sort, setSort] = useState<"popular" | "name">("popular");
  const q = useDebounce(filter, 300);
  const tags = useAsync(() => api.tags.list({ q, sort, limit: 100 }), [q, sort]);

  return (
    <div className="space-y-4">
      <div>
        <h1 className="text-2xl font-bold">Tags</h1>
        <p className="text-sm text-slate-500">Tags group questions by topic so experts can find them.</p>
      </div>
      <div className="flex flex-wrap gap-2">
        <div className="relative max-w-xs flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            className="input pl-9"
            placeholder="Filter by tag name"
            aria-label="Filter tags"
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
          />
        </div>
        <select
          className="input w-auto"
          value={sort}
          onChange={(e) => setSort(e.target.value as "popular" | "name")}
          aria-label="Sort tags"
        >
          <option value="popular">Popular</option>
          <option value="name">Name</option>
        </select>
      </div>
      {tags.loading ? (
        <Spinner />
      ) : tags.error ? (
        <ErrorMessage error={tags.error} onRetry={tags.reload} />
      ) : tags.data?.length ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {tags.data.map((tag) => (
            <Link
              key={tag.id}
              to={`/questions?tag=${encodeURIComponent(tag.name)}`}
              className="card p-4 transition hover:border-brand-500"
            >
              <span className="rounded-md bg-brand-50 px-2 py-0.5 text-sm font-medium text-brand-700 dark:bg-brand-500/15 dark:text-brand-100">
                {tag.name}
              </span>
              <p className="mt-2 line-clamp-3 text-sm text-slate-600 dark:text-slate-400">
                {tag.description || "No description yet."}
              </p>
              <p className="mt-3 text-xs text-slate-500">{pluralize(tag.question_count, "question")}</p>
            </Link>
          ))}
        </div>
      ) : (
        <EmptyState title="No tags found" />
      )}
    </div>
  );
}
