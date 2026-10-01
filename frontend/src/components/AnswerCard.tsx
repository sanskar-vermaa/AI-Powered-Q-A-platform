import { Bot, CheckCircle2, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

import { api } from "../api/endpoints";
import type { Answer } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useAsync } from "../hooks/useAsync";
import { CommentList } from "./CommentList";
import { FlagButton } from "./FlagButton";
import { Markdown } from "./Markdown";
import { MarkdownEditor } from "./MarkdownEditor";
import { UserChip } from "./UserChip";
import { VoteControls } from "./VoteControls";

interface Props {
  answer: Answer;
  questionAuthorId: number;
  onAccept: (answerId: number) => void;
  onDeleted: (answerId: number) => void;
}

export function AnswerCard({ answer: initial, questionAuthorId, onAccept, onDeleted }: Props) {
  const { user } = useAuth();
  const toast = useToast();
  const [answer, setAnswer] = useState(initial);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState(initial.body);
  const comments = useAsync(() => api.answers.comments(answer.id), [answer.id]);

  const isStaff = !!user && user.role !== "user";
  const isOwner = !!user && answer.author?.id === user.id;
  const canEdit = answer.is_ai ? isStaff : isOwner || isStaff;
  const canDelete = isOwner || isStaff || (answer.is_ai && user?.id === questionAuthorId);
  const canAccept = user?.id === questionAuthorId;

  async function save() {
    try {
      setAnswer(await api.answers.update(answer.id, draft));
      setEditing(false);
      toast.success("Answer updated");
    } catch (error) {
      toast.error(error);
    }
  }

  async function remove() {
    if (!confirm("Delete this answer?")) return;
    try {
      await api.answers.remove(answer.id);
      onDeleted(answer.id);
    } catch (error) {
      toast.error(error);
    }
  }

  const border = initial.is_accepted
    ? "border-emerald-500 ring-1 ring-emerald-500/30"
    : answer.is_ai
      ? "border-violet-300 dark:border-violet-800"
      : "";

  return (
    <article className={`card flex gap-4 p-5 ${border}`} id={`answer-${answer.id}`}>
      <div className="flex flex-col items-center gap-3">
        <VoteControls
          score={answer.score}
          myVote={answer.my_vote}
          disabled={isOwner}
          onVote={(value) => api.answers.vote(answer.id, value)}
        />
        {(canAccept || initial.is_accepted) && (
          <button
            title={initial.is_accepted ? "Accepted answer" : "Accept this answer"}
            aria-label={initial.is_accepted ? "Unaccept answer" : "Accept answer"}
            disabled={!canAccept}
            onClick={() => onAccept(answer.id)}
            className={
              initial.is_accepted ? "text-emerald-500" : "text-slate-300 hover:text-emerald-500 dark:text-slate-600"
            }
          >
            <CheckCircle2 className="h-7 w-7" />
          </button>
        )}
      </div>
      <div className="min-w-0 flex-1">
        {answer.is_ai && (
          <div className="mb-3 inline-flex items-center gap-1.5 rounded-full bg-violet-100 px-2.5 py-1 text-xs font-medium text-violet-700 dark:bg-violet-500/15 dark:text-violet-200">
            <Bot className="h-3.5 w-3.5" /> AI-generated answer — verify before relying on it
          </div>
        )}
        {editing ? (
          <div className="space-y-2">
            <MarkdownEditor value={draft} onChange={setDraft} minLength={20} />
            <div className="flex gap-2">
              <button className="btn-primary" disabled={draft.trim().length < 20} onClick={save}>
                Save
              </button>
              <button className="btn-secondary" onClick={() => setEditing(false)}>
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <Markdown>{answer.body}</Markdown>
        )}
        <div className="mt-4 flex flex-wrap items-center justify-between gap-2">
          <div className="flex gap-1">
            {canEdit && !editing && (
              <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setEditing(true)}>
                <Pencil className="h-3.5 w-3.5" /> Edit
              </button>
            )}
            {canDelete && (
              <button className="btn-ghost px-2 py-1 text-xs text-red-600" onClick={remove}>
                <Trash2 className="h-3.5 w-3.5" /> Delete
              </button>
            )}
            {!isOwner && <FlagButton targetType="answer" targetId={answer.id} />}
          </div>
          <UserChip user={answer.author} ai={answer.is_ai} action="answered" date={answer.created_at} />
        </div>
        {comments.data && (
          <CommentList
            comments={comments.data}
            onAdd={(body) => api.answers.addComment(answer.id, body)}
            onDelete={(id) => api.comments.remove(id)}
          />
        )}
      </div>
    </article>
  );
}
