import { ArrowRight, Bot, MessageSquareText, Sparkles, Tags, Users } from "lucide-react";
import { Link } from "react-router-dom";

import { api } from "../api/endpoints";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { QuestionCard } from "../components/QuestionCard";
import { useAuth } from "../context/AuthContext";
import { useAsync } from "../hooks/useAsync";
import { compactNumber } from "../utils/format";

export function HomePage() {
  const { user } = useAuth();
  const stats = useAsync(() => api.stats.site(), []);
  const latest = useAsync(() => api.questions.list({ page_size: 8, sort: "active" }), []);

  const tiles = stats.data
    ? [
        { label: "Questions", value: stats.data.questions, icon: MessageSquareText },
        { label: "AI answers", value: stats.data.ai_answers, icon: Bot },
        { label: "Members", value: stats.data.users, icon: Users },
        { label: "Tags", value: stats.data.tags, icon: Tags },
      ]
    : [];

  return (
    <div className="space-y-8">
      <section className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-brand-600 via-violet-600 to-fuchsia-600 p-8 text-white shadow-lg sm:p-10">
        <div className="relative z-10 max-w-2xl">
          <span className="inline-flex items-center gap-1.5 rounded-full bg-white/15 px-3 py-1 text-xs font-medium">
            <Sparkles className="h-3.5 w-3.5" /> Community knowledge + AI
          </span>
          <h1 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">
            Get answers in seconds, from people and AI.
          </h1>
          <p className="mt-3 text-white/85">
            Ask a question and get an instant AI draft answer, then let the community vote, refine and accept the best
            solution.
          </p>
          <div className="mt-6 flex flex-wrap gap-3">
            <Link to={user ? "/ask" : "/register"} className="btn bg-white text-brand-700 hover:bg-white/90">
              {user ? "Ask a question" : "Join the community"} <ArrowRight className="h-4 w-4" />
            </Link>
            <Link to="/assistant" className="btn border border-white/40 text-white hover:bg-white/10">
              <Bot className="h-4 w-4" /> Chat with the AI assistant
            </Link>
          </div>
        </div>
        <div className="absolute -right-16 -top-16 h-64 w-64 rounded-full bg-white/10 blur-2xl" />
      </section>

      {tiles.length > 0 && (
        <section className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          {tiles.map(({ label, value, icon: Icon }) => (
            <div key={label} className="card flex items-center gap-3 p-4">
              <span className="rounded-lg bg-brand-50 p-2 text-brand-600 dark:bg-brand-500/15 dark:text-brand-100">
                <Icon className="h-5 w-5" />
              </span>
              <div>
                <p className="text-2xl font-bold">{compactNumber(value)}</p>
                <p className="text-xs text-slate-500">{label}</p>
              </div>
            </div>
          ))}
        </section>
      )}

      <section className="card">
        <div className="flex items-center justify-between border-b border-slate-200 p-4 dark:border-slate-800">
          <h2 className="text-lg font-semibold">Recently active</h2>
          <Link to="/questions" className="text-sm font-medium text-brand-600 hover:underline">
            View all
          </Link>
        </div>
        {latest.loading ? (
          <Spinner />
        ) : latest.error ? (
          <div className="p-4">
            <ErrorMessage error={latest.error} onRetry={latest.reload} />
          </div>
        ) : latest.data && latest.data.items.length > 0 ? (
          latest.data.items.map((q) => <QuestionCard key={q.id} question={q} />)
        ) : (
          <EmptyState title="No questions yet">
            <Link to="/ask" className="btn-primary mt-2">
              Ask the first question
            </Link>
          </EmptyState>
        )}
      </section>
    </div>
  );
}
