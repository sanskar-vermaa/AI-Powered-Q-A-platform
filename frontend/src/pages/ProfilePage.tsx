import { Award, CalendarDays } from "lucide-react";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";

import { api } from "../api/endpoints";
import { Avatar } from "../components/Avatar";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { QuestionCard } from "../components/QuestionCard";
import { useAsync } from "../hooks/useAsync";
import { compactNumber, timeAgo } from "../utils/format";

const BADGE_LABELS: Record<string, string> = {
  curious: "Asked a first question",
  helper: "Posted a first answer",
  teacher: "Had an answer accepted",
  enthusiast: "Posted 10 answers",
  popular: "A question scored 10+",
  trusted: "Reached 500 reputation",
};

export function ProfilePage() {
  const username = useParams().username ?? "";
  const [tab, setTab] = useState<"questions" | "answers">("questions");
  const profile = useAsync(() => api.users.profile(username), [username]);
  const questions = useAsync(() => api.questions.list({ author: username, page_size: 20 }), [username]);
  const answers = useAsync(() => api.users.answers(username), [username]);

  if (profile.loading) return <Spinner />;
  if (profile.error || !profile.data) return <ErrorMessage error={profile.error ?? "User not found"} />;
  const p = profile.data;

  return (
    <div className="space-y-6">
      <section className="card flex flex-wrap items-center gap-6 p-6">
        <Avatar name={p.username} size="lg" />
        <div className="min-w-0 flex-1">
          <h1 className="text-2xl font-bold">
            {p.username}
            {p.role !== "user" && (
              <span className="ml-2 rounded-full bg-amber-100 px-2 py-0.5 align-middle text-xs font-medium text-amber-800 dark:bg-amber-500/20 dark:text-amber-200">
                {p.role}
              </span>
            )}
          </h1>
          <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">{p.bio || "No bio yet."}</p>
          <p className="mt-2 flex items-center gap-1 text-xs text-slate-500">
            <CalendarDays className="h-3.5 w-3.5" /> Member {timeAgo(p.created_at)}
          </p>
        </div>
        <dl className="grid grid-cols-3 gap-6 text-center">
          {[
            ["Reputation", p.reputation],
            ["Questions", p.question_count],
            ["Answers", p.answer_count],
          ].map(([label, value]) => (
            <div key={label}>
              <dd className="text-2xl font-bold">{compactNumber(Number(value))}</dd>
              <dt className="text-xs text-slate-500">{label}</dt>
            </div>
          ))}
        </dl>
      </section>

      <section className="card p-5">
        <h2 className="mb-3 flex items-center gap-2 font-semibold">
          <Award className="h-4 w-4 text-amber-500" /> Badges
        </h2>
        {p.badges.length ? (
          <div className="flex flex-wrap gap-2">
            {p.badges.map((badge) => (
              <span
                key={badge}
                title={BADGE_LABELS[badge]}
                className="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800 dark:border-amber-700 dark:bg-amber-500/10 dark:text-amber-200"
              >
                🏅 {badge}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-slate-500">No badges yet.</p>
        )}
      </section>

      <section className="card">
        <div className="flex gap-1 border-b border-slate-200 p-2 dark:border-slate-800">
          {(["questions", "answers"] as const).map((name) => (
            <button
              key={name}
              className={tab === name ? "btn-primary py-1.5" : "btn-ghost py-1.5"}
              onClick={() => setTab(name)}
            >
              {name === "questions" ? "Questions" : "Answers"}
            </button>
          ))}
        </div>
        {tab === "questions" ? (
          questions.data?.items.length ? (
            questions.data.items.map((q) => <QuestionCard key={q.id} question={q} />)
          ) : (
            <EmptyState title="No questions yet" />
          )
        ) : answers.data?.length ? (
          <ul className="divide-y divide-slate-200 dark:divide-slate-800">
            {answers.data.map((a) => (
              <li key={a.id} className="flex items-center gap-3 p-4 text-sm">
                <span
                  className={`rounded-md px-2 py-0.5 text-xs font-semibold ${a.is_accepted ? "bg-emerald-600 text-white" : "bg-slate-100 dark:bg-slate-800"}`}
                >
                  {a.score}
                </span>
                <Link
                  to={`/questions/${a.question_id}#answer-${a.id}`}
                  className="line-clamp-1 flex-1 text-brand-600 hover:underline dark:text-brand-100"
                >
                  {a.body.replace(/[#*`>_]/g, "").slice(0, 140)}
                </Link>
                <span className="text-xs text-slate-500">{timeAgo(a.created_at)}</span>
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState title="No answers yet" />
        )}
      </section>
    </div>
  );
}
