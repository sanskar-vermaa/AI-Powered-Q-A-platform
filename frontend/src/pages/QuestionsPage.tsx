import { X } from "lucide-react";
import { Link, useSearchParams } from "react-router-dom";

import { api } from "../api/endpoints";
import type { QuestionSort } from "../api/types";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { Pagination } from "../components/Pagination";
import { QuestionCard } from "../components/QuestionCard";
import { useAsync } from "../hooks/useAsync";
import { pluralize } from "../utils/format";

const SORTS: { value: QuestionSort; label: string }[] = [
  { value: "newest", label: "Newest" },
  { value: "active", label: "Active" },
  { value: "votes", label: "Top voted" },
  { value: "views", label: "Most viewed" },
  { value: "unanswered", label: "Unanswered" },
];

export function QuestionsPage() {
  const [params, setParams] = useSearchParams();
  const sort = (params.get("sort") as QuestionSort) || "newest";
  const page = Number(params.get("page") || 1);
  const tag = params.get("tag") || undefined;
  const q = params.get("q") || undefined;

  const result = useAsync(() => api.questions.list({ sort, page, tag, q, page_size: 15 }), [sort, page, tag, q]);

  function update(changes: Record<string, string | undefined>) {
    const next = new URLSearchParams(params);
    for (const [key, value] of Object.entries(changes)) {
      if (value) next.set(key, value);
      else next.delete(key);
    }
    if (!("page" in changes)) next.delete("page");
    setParams(next);
  }

  const heading = q ? `Results for “${q}”` : tag ? `Questions tagged [${tag}]` : "All questions";

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold">{heading}</h1>
          {result.data && <p className="text-sm text-slate-500">{pluralize(result.data.total, "question")}</p>}
        </div>
        <Link to="/ask" className="btn-primary">
          Ask question
        </Link>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <div className="inline-flex rounded-lg border border-slate-200 bg-white p-1 dark:border-slate-800 dark:bg-slate-900">
          {SORTS.map((option) => (
            <button
              key={option.value}
              className={`rounded-md px-3 py-1.5 text-sm ${
                sort === option.value
                  ? "bg-brand-600 text-white"
                  : "text-slate-600 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              }`}
              onClick={() => update({ sort: option.value })}
            >
              {option.label}
            </button>
          ))}
        </div>
        {(tag || q) && (
          <button className="btn-secondary py-1.5" onClick={() => update({ tag: undefined, q: undefined })}>
            <X className="h-3.5 w-3.5" /> Clear filters
          </button>
        )}
      </div>

      <div className="card">
        {result.loading ? (
          <Spinner />
        ) : result.error ? (
          <div className="p-4">
            <ErrorMessage error={result.error} onRetry={result.reload} />
          </div>
        ) : result.data && result.data.items.length ? (
          result.data.items.map((question) => <QuestionCard key={question.id} question={question} />)
        ) : (
          <EmptyState title="No questions found">
            <p className="text-sm">Try a different search, or ask it yourself.</p>
          </EmptyState>
        )}
      </div>
      {result.data && (
        <Pagination page={result.data.page} pages={result.data.pages} onChange={(p) => update({ page: String(p) })} />
      )}
    </div>
  );
}
