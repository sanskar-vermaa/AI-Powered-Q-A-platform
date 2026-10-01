import { Lightbulb, Loader2, Sparkles, Wand2 } from "lucide-react";
import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import { api } from "../api/endpoints";
import type { ImprovedQuestion, SimilarQuestion } from "../api/types";
import { ErrorMessage, Spinner } from "../components/Feedback";
import { MarkdownEditor } from "../components/MarkdownEditor";
import { TagInput } from "../components/TagInput";
import { useToast } from "../context/ToastContext";
import { useDebounce } from "../hooks/useDebounce";

/** Ask a new question, or edit an existing one when the route has an :id. */
export function AskPage() {
  const { id } = useParams();
  const editing = id !== undefined;
  const navigate = useNavigate();
  const toast = useToast();

  const [title, setTitle] = useState("");
  const [body, setBody] = useState("");
  const [tags, setTags] = useState<string[]>([]);
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);
  const [loading, setLoading] = useState(editing);
  const [aiBusy, setAiBusy] = useState<"tags" | "improve" | null>(null);
  const [improved, setImproved] = useState<ImprovedQuestion | null>(null);
  const [similar, setSimilar] = useState<SimilarQuestion[]>([]);
  const debouncedTitle = useDebounce(title, 500);

  useEffect(() => {
    if (!editing) return;
    api.questions
      .get(Number(id))
      .then((q) => {
        setTitle(q.title);
        setBody(q.body);
        setTags(q.tags);
      })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [editing, id]);

  useEffect(() => {
    if (editing || debouncedTitle.trim().length < 10) {
      setSimilar([]);
      return;
    }
    api.questions
      .similar(debouncedTitle)
      .then(setSimilar)
      .catch(() => setSimilar([]));
  }, [debouncedTitle, editing]);

  async function suggestTags() {
    setAiBusy("tags");
    try {
      const { tags: suggested } = await api.ai.suggestTags(title, body);
      setTags((current) => [...new Set([...current, ...suggested])].slice(0, 5));
      if (!suggested.length) toast.error("No tag suggestions for this question");
    } catch (err) {
      toast.error(err);
    } finally {
      setAiBusy(null);
    }
  }

  async function improve() {
    setAiBusy("improve");
    try {
      setImproved(await api.ai.improve(title, body));
    } catch (err) {
      toast.error(err);
    } finally {
      setAiBusy(null);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(undefined);
    try {
      const question = editing
        ? await api.questions.update(Number(id), { title, body, tags })
        : await api.questions.create({ title, body, tags });
      toast.success(editing ? "Question updated" : "Question posted");
      navigate(`/questions/${question.id}`);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <Spinner />;
  const canUseAi = title.trim().length >= 5;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_18rem]">
      <form onSubmit={submit} className="space-y-5">
        <h1 className="text-2xl font-bold">{editing ? "Edit question" : "Ask a public question"}</h1>
        {error && <ErrorMessage error={error} />}

        <div className="card space-y-2 p-5">
          <label htmlFor="title" className="label">
            Title
          </label>
          <p className="text-xs text-slate-500">Be specific and imagine you're asking another person.</p>
          <input
            id="title"
            className="input"
            maxLength={200}
            placeholder="e.g. How do I sort a list of dictionaries by a key in Python?"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
          {similar.length > 0 && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm dark:border-amber-900 dark:bg-amber-950/30">
              <p className="mb-1 font-medium text-amber-800 dark:text-amber-300">Similar questions already exist:</p>
              <ul className="list-inside list-disc space-y-0.5">
                {similar.map((s) => (
                  <li key={s.id}>
                    <Link to={`/questions/${s.id}`} target="_blank" className="text-brand-600 hover:underline">
                      {s.title}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="card space-y-2 p-5">
          <label htmlFor="body" className="label">
            What are the details of your problem?
          </label>
          <p className="text-xs text-slate-500">
            Include what you tried, what you expected and what actually happened.
          </p>
          <MarkdownEditor id="body" value={body} onChange={setBody} minLength={20} rows={12} />
          <button
            type="button"
            className="btn-ai"
            disabled={!canUseAi || body.trim().length < 10 || aiBusy !== null}
            onClick={improve}
          >
            {aiBusy === "improve" ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wand2 className="h-4 w-4" />}
            Improve with AI
          </button>
          {improved && (
            <div className="space-y-3 rounded-lg border border-violet-200 bg-violet-50 p-4 dark:border-violet-900 dark:bg-violet-950/30">
              <p className="flex items-center gap-1.5 text-sm font-semibold text-violet-800 dark:text-violet-200">
                <Sparkles className="h-4 w-4" /> AI suggestion
              </p>
              <p className="text-sm font-medium">{improved.title}</p>
              <ul className="list-inside list-disc text-sm text-slate-600 dark:text-slate-300">
                {improved.tips.map((tip) => (
                  <li key={tip}>{tip}</li>
                ))}
              </ul>
              <div className="flex gap-2">
                <button
                  type="button"
                  className="btn-primary"
                  onClick={() => {
                    setTitle(improved.title);
                    setBody(improved.body);
                    setImproved(null);
                  }}
                >
                  Apply suggestion
                </button>
                <button type="button" className="btn-secondary" onClick={() => setImproved(null)}>
                  Dismiss
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="card space-y-2 p-5">
          <label htmlFor="tags" className="label">
            Tags
          </label>
          <p className="text-xs text-slate-500">Add up to 5 tags to describe what your question is about.</p>
          <TagInput id="tags" tags={tags} onChange={setTags} />
          <button type="button" className="btn-secondary" disabled={!canUseAi || aiBusy !== null} onClick={suggestTags}>
            {aiBusy === "tags" ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Sparkles className="h-4 w-4 text-violet-500" />
            )}
            Suggest tags
          </button>
        </div>

        <button className="btn-primary" disabled={busy || title.trim().length < 10 || body.trim().length < 20}>
          {busy ? "Saving…" : editing ? "Save changes" : "Post your question"}
        </button>
      </form>

      <aside className="card h-fit space-y-3 p-5 text-sm">
        <h2 className="flex items-center gap-2 font-semibold">
          <Lightbulb className="h-4 w-4 text-amber-500" /> Writing a good question
        </h2>
        <ol className="list-inside list-decimal space-y-2 text-slate-600 dark:text-slate-400">
          <li>Summarize the problem in a one-line title.</li>
          <li>Describe what you tried and what you expected.</li>
          <li>Add a minimal code sample that reproduces the issue.</li>
          <li>Use AI to polish the wording and pick tags.</li>
        </ol>
      </aside>
    </div>
  );
}
