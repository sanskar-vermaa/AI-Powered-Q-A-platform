import { Bookmark, BookmarkCheck, Bot, Eye, Loader2, Pencil, Sparkles, Trash2 } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/endpoints";
import type { Answer } from "../api/types";
import { AnswerCard } from "../components/AnswerCard";
import { CommentList } from "../components/CommentList";
import { ErrorMessage, Spinner } from "../components/Feedback";
import { FlagButton } from "../components/FlagButton";
import { Markdown } from "../components/Markdown";
import { MarkdownEditor } from "../components/MarkdownEditor";
import { TagBadge } from "../components/TagBadge";
import { UserChip } from "../components/UserChip";
import { VoteControls } from "../components/VoteControls";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useAsync } from "../hooks/useAsync";
import { compactNumber, pluralize, timeAgo, wasEdited } from "../utils/format";

export function QuestionPage() {
  const id = Number(useParams().id);
  const { user } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const question = useAsync(() => api.questions.get(id), [id]);
  const answers = useAsync(() => api.answers.list(id), [id]);
  const comments = useAsync(() => api.questions.comments(id), [id]);
  const related = useAsync(() => api.questions.related(id), [id]);

  const [draft, setDraft] = useState("");
  const [posting, setPosting] = useState(false);
  const [aiBusy, setAiBusy] = useState(false);
  const [summary, setSummary] = useState<string>();
  const [summaryBusy, setSummaryBusy] = useState(false);

  if (question.loading) return <Spinner />;
  if (question.error || !question.data) return <ErrorMessage error={question.error ?? "Question not found"} />;
  const q = question.data;
  const isOwner = user?.id === q.author.id;
  const isStaff = !!user && user.role !== "user";
  const hasAiAnswer = answers.data?.some((a) => a.is_ai) ?? false;

  async function toggleBookmark() {
    try {
      await api.questions.bookmark(q.id, !q.bookmarked);
      question.setData({ ...q, bookmarked: !q.bookmarked });
    } catch (error) {
      toast.error(error);
    }
  }

  async function removeQuestion() {
    if (!confirm("Delete this question and all of its answers?")) return;
    try {
      await api.questions.remove(q.id);
      toast.success("Question deleted");
      navigate("/questions");
    } catch (error) {
      toast.error(error);
    }
  }

  async function accept(answerId: number) {
    try {
      const updated = await api.questions.accept(q.id, answerId);
      question.setData(updated);
      answers.reload();
    } catch (error) {
      toast.error(error);
    }
  }

  function addAnswer(answer: Answer) {
    answers.setData((current) => [...(current ?? []), answer]);
    question.setData({ ...q, answer_count: q.answer_count + 1 });
  }

  async function postAnswer(event: FormEvent) {
    event.preventDefault();
    setPosting(true);
    try {
      addAnswer(await api.answers.create(q.id, draft));
      setDraft("");
      toast.success("Answer posted");
    } catch (error) {
      toast.error(error);
    } finally {
      setPosting(false);
    }
  }

  async function generateAiAnswer() {
    setAiBusy(true);
    try {
      addAnswer(await api.ai.answer(q.id));
    } catch (error) {
      toast.error(error);
    } finally {
      setAiBusy(false);
    }
  }

  async function summarize() {
    setSummaryBusy(true);
    try {
      setSummary((await api.ai.summary(q.id)).summary);
    } catch (error) {
      toast.error(error);
    } finally {
      setSummaryBusy(false);
    }
  }

  return (
    <div className="grid gap-6 xl:grid-cols-[1fr_16rem]">
      <div className="min-w-0 space-y-6">
        <header className="space-y-2 border-b border-slate-200 pb-4 dark:border-slate-800">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <h1 className="text-2xl font-bold leading-tight">{q.title}</h1>
            <Link to="/ask" className="btn-primary shrink-0">
              Ask question
            </Link>
          </div>
          <div className="flex flex-wrap gap-4 text-xs text-slate-500">
            <span>Asked {timeAgo(q.created_at)}</span>
            {wasEdited(q.created_at, q.updated_at) && <span>Modified {timeAgo(q.updated_at)}</span>}
            <span className="inline-flex items-center gap-1">
              <Eye className="h-3.5 w-3.5" /> {pluralize(q.views, "view")}
            </span>
          </div>
        </header>

        <article className="flex gap-4">
          <div className="flex flex-col items-center gap-3">
            <VoteControls
              score={q.score}
              myVote={q.my_vote}
              disabled={isOwner}
              onVote={(v) => api.questions.vote(q.id, v)}
            />
            {user && (
              <button
                onClick={toggleBookmark}
                aria-label={q.bookmarked ? "Remove bookmark" : "Bookmark"}
                className="text-slate-400 hover:text-brand-600"
              >
                {q.bookmarked ? <BookmarkCheck className="h-5 w-5 text-brand-600" /> : <Bookmark className="h-5 w-5" />}
              </button>
            )}
          </div>
          <div className="min-w-0 flex-1">
            <Markdown>{q.body}</Markdown>
            <div className="mt-4 flex flex-wrap gap-1.5">
              {q.tags.map((tag) => (
                <TagBadge key={tag} name={tag} />
              ))}
            </div>
            <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
              <div className="flex gap-1">
                {(isOwner || isStaff) && (
                  <>
                    <Link to={`/questions/${q.id}/edit`} className="btn-ghost px-2 py-1 text-xs">
                      <Pencil className="h-3.5 w-3.5" /> Edit
                    </Link>
                    <button className="btn-ghost px-2 py-1 text-xs text-red-600" onClick={removeQuestion}>
                      <Trash2 className="h-3.5 w-3.5" /> Delete
                    </button>
                  </>
                )}
                {!isOwner && <FlagButton targetType="question" targetId={q.id} />}
              </div>
              <div className="rounded-lg bg-brand-50 px-3 py-2 dark:bg-brand-500/10">
                <UserChip user={q.author} action="asked" date={q.created_at} />
              </div>
            </div>
            {comments.data && (
              <CommentList
                comments={comments.data}
                onAdd={(body) => api.questions.addComment(q.id, body)}
                onDelete={(cid) => api.comments.remove(cid)}
              />
            )}
          </div>
        </article>

        {user && (q.answer_count > 0 || summary) && (
          <section className="card border-violet-200 p-4 dark:border-violet-900">
            <div className="flex items-center justify-between gap-2">
              <h2 className="flex items-center gap-2 font-semibold">
                <Sparkles className="h-4 w-4 text-violet-500" /> AI thread summary
              </h2>
              <button className="btn-secondary py-1" onClick={summarize} disabled={summaryBusy}>
                {summaryBusy && <Loader2 className="h-4 w-4 animate-spin" />} {summary ? "Refresh" : "Summarize"}
              </button>
            </div>
            {summary && <Markdown className="mt-3 text-sm">{summary}</Markdown>}
          </section>
        )}

        <section className="space-y-4">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <h2 className="text-xl font-semibold">{pluralize(answers.data?.length ?? q.answer_count, "Answer")}</h2>
            {user && !hasAiAnswer && (
              <button className="btn-ai" onClick={generateAiAnswer} disabled={aiBusy}>
                {aiBusy ? <Loader2 className="h-4 w-4 animate-spin" /> : <Bot className="h-4 w-4" />}
                {aiBusy ? "Generating answer…" : "Get an AI answer"}
              </button>
            )}
          </div>
          {answers.loading ? (
            <Spinner />
          ) : answers.error ? (
            <ErrorMessage error={answers.error} onRetry={answers.reload} />
          ) : (
            answers.data?.map((answer) => (
              <AnswerCard
                key={`${answer.id}-${answer.is_accepted}`}
                answer={answer}
                questionAuthorId={q.author.id}
                onAccept={accept}
                onDeleted={(answerId) => {
                  answers.setData((current) => (current ?? []).filter((a) => a.id !== answerId));
                  question.reload();
                }}
              />
            ))
          )}
        </section>

        <section className="space-y-3">
          <h2 className="text-lg font-semibold">Your answer</h2>
          {user ? (
            <form onSubmit={postAnswer} className="space-y-3">
              <MarkdownEditor
                value={draft}
                onChange={setDraft}
                minLength={20}
                placeholder="Write a helpful, detailed answer…"
              />
              <button className="btn-primary" disabled={posting || draft.trim().length < 20}>
                {posting ? "Posting…" : "Post your answer"}
              </button>
            </form>
          ) : (
            <p className="card p-4 text-sm">
              <Link to={`/login?next=/questions/${q.id}`} className="font-medium text-brand-600">
                Log in
              </Link>{" "}
              or{" "}
              <Link to="/register" className="font-medium text-brand-600">
                sign up
              </Link>{" "}
              to answer this question.
            </p>
          )}
        </section>
      </div>

      <aside className="space-y-4">
        <div className="card p-4">
          <h2 className="mb-3 text-sm font-semibold">Related questions</h2>
          {related.data && related.data.length ? (
            <ul className="space-y-2 text-sm">
              {related.data.map((r) => (
                <li key={r.id}>
                  <Link to={`/questions/${r.id}`} className="text-brand-600 hover:underline dark:text-brand-100">
                    {r.title}
                  </Link>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-slate-500">No related questions yet.</p>
          )}
        </div>
        <div className="card p-4 text-sm text-slate-500">
          <p>
            <span className="font-semibold text-slate-700 dark:text-slate-200">{compactNumber(q.score)}</span> score ·{" "}
            <span className="font-semibold text-slate-700 dark:text-slate-200">{compactNumber(q.views)}</span> views
          </p>
        </div>
      </aside>
    </div>
  );
}
