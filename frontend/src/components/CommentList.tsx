import { Trash2 } from "lucide-react";
import { useState, type FormEvent } from "react";
import { Link } from "react-router-dom";

import type { Comment } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { timeAgo } from "../utils/format";

interface Props {
  comments: Comment[];
  onAdd: (body: string) => Promise<Comment>;
  onDelete: (id: number) => Promise<void>;
}

export function CommentList({ comments: initial, onAdd, onDelete }: Props) {
  const { user } = useAuth();
  const toast = useToast();
  const [comments, setComments] = useState(initial);
  const [open, setOpen] = useState(false);
  const [body, setBody] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    try {
      const comment = await onAdd(body.trim());
      setComments((current) => [...current, comment]);
      setBody("");
      setOpen(false);
    } catch (error) {
      toast.error(error);
    } finally {
      setBusy(false);
    }
  }

  async function remove(id: number) {
    try {
      await onDelete(id);
      setComments((current) => current.filter((c) => c.id !== id));
    } catch (error) {
      toast.error(error);
    }
  }

  return (
    <div className="mt-4 border-t border-slate-100 pt-2 dark:border-slate-800">
      <ul className="divide-y divide-slate-100 dark:divide-slate-800">
        {comments.map((comment) => (
          <li key={comment.id} className="group flex items-start gap-2 py-2 text-sm">
            <p className="flex-1 text-slate-700 dark:text-slate-300">
              {comment.body} –{" "}
              <Link to={`/users/${comment.author.username}`} className="font-medium text-brand-600 dark:text-brand-100">
                {comment.author.username}
              </Link>{" "}
              <span className="text-xs text-slate-400">{timeAgo(comment.created_at)}</span>
            </p>
            {user && (user.id === comment.author.id || user.role !== "user") && (
              <button
                aria-label="Delete comment"
                className="text-slate-400 opacity-0 hover:text-red-500 group-hover:opacity-100"
                onClick={() => remove(comment.id)}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            )}
          </li>
        ))}
      </ul>
      {user &&
        (open ? (
          <form onSubmit={submit} className="mt-2 flex gap-2">
            <input
              className="input"
              autoFocus
              value={body}
              maxLength={600}
              placeholder="Add a comment…"
              onChange={(event) => setBody(event.target.value)}
            />
            <button className="btn-primary" disabled={busy || body.trim().length < 2}>
              Post
            </button>
          </form>
        ) : (
          <button
            className="mt-1 text-xs font-medium text-slate-500 hover:text-brand-600"
            onClick={() => setOpen(true)}
          >
            Add a comment
          </button>
        ))}
    </div>
  );
}
