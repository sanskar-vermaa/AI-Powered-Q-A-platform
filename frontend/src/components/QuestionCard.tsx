import { CheckCircle2 } from "lucide-react";
import { Link } from "react-router-dom";

import type { QuestionSummary } from "../api/types";
import { compactNumber } from "../utils/format";
import { TagBadge } from "./TagBadge";
import { UserChip } from "./UserChip";

function Stat({ value, label, highlight }: { value: number; label: string; highlight?: "answered" | "accepted" }) {
  const styles = {
    accepted: "bg-emerald-600 text-white border-emerald-600",
    answered: "border-emerald-600 text-emerald-700 dark:text-emerald-400",
    none: "border-transparent text-slate-500 dark:text-slate-400",
  };
  return (
    <div
      className={`flex items-center justify-end gap-1 rounded-md border px-2 py-0.5 text-xs ${styles[highlight ?? "none"]}`}
    >
      {highlight === "accepted" && <CheckCircle2 className="h-3 w-3" />}
      <span className="font-semibold">{compactNumber(value)}</span> {label}
    </div>
  );
}

export function QuestionCard({ question }: { question: QuestionSummary }) {
  const answerState = question.has_accepted_answer ? "accepted" : question.answer_count > 0 ? "answered" : undefined;
  return (
    <article className="flex gap-4 border-b border-slate-200 p-4 last:border-b-0 dark:border-slate-800">
      <div className="hidden w-28 shrink-0 flex-col gap-1.5 sm:flex">
        <Stat value={question.score} label={Math.abs(question.score) === 1 ? "vote" : "votes"} />
        <Stat
          value={question.answer_count}
          label={question.answer_count === 1 ? "answer" : "answers"}
          highlight={answerState}
        />
        <Stat value={question.views} label="views" />
      </div>
      <div className="min-w-0 flex-1">
        <h3 className="text-base font-semibold leading-snug">
          <Link
            to={`/questions/${question.id}`}
            className="text-brand-700 hover:text-brand-600 dark:text-brand-100 dark:hover:text-white"
          >
            {question.title}
          </Link>
        </h3>
        <p className="mt-1 line-clamp-2 text-sm text-slate-600 dark:text-slate-400">{question.excerpt}</p>
        <div className="mt-3 flex flex-wrap items-center justify-between gap-2">
          <div className="flex flex-wrap gap-1.5">
            {question.tags.map((tag) => (
              <TagBadge key={tag} name={tag} />
            ))}
          </div>
          <UserChip user={question.author} action="asked" date={question.created_at} />
        </div>
      </div>
    </article>
  );
}
