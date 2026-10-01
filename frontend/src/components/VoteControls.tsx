import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

interface Props {
  score: number;
  myVote: number;
  onVote: (value: number) => Promise<{ score: number; my_vote: number }>;
  disabled?: boolean;
}

export function VoteControls({ score, myVote, onVote, disabled }: Props) {
  const { user } = useAuth();
  const toast = useToast();
  const [state, setState] = useState({ score, myVote });
  const [busy, setBusy] = useState(false);

  async function vote(direction: 1 | -1) {
    if (!user) {
      toast.error("Log in to vote");
      return;
    }
    const value = state.myVote === direction ? 0 : direction;
    setBusy(true);
    try {
      const result = await onVote(value);
      setState({ score: result.score, myVote: result.my_vote });
    } catch (error) {
      toast.error(error);
    } finally {
      setBusy(false);
    }
  }

  const arrow = (active: boolean) =>
    `rounded-full border p-1.5 transition disabled:opacity-40 ${
      active
        ? "border-brand-500 bg-brand-50 text-brand-600 dark:bg-brand-500/20 dark:text-brand-100"
        : "border-slate-300 text-slate-500 hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
    }`;

  return (
    <div className="flex flex-col items-center gap-1">
      <button
        type="button"
        aria-label="Upvote"
        className={arrow(state.myVote === 1)}
        disabled={busy || disabled}
        onClick={() => vote(1)}
      >
        <ChevronUp className="h-5 w-5" />
      </button>
      <span className="text-lg font-semibold tabular-nums" data-testid="score">
        {state.score}
      </span>
      <button
        type="button"
        aria-label="Downvote"
        className={arrow(state.myVote === -1)}
        disabled={busy || disabled}
        onClick={() => vote(-1)}
      >
        <ChevronDown className="h-5 w-5" />
      </button>
    </div>
  );
}
