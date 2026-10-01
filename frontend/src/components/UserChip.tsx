import { Bot } from "lucide-react";
import { Link } from "react-router-dom";

import type { User } from "../api/types";
import { compactNumber, timeAgo } from "../utils/format";
import { Avatar } from "./Avatar";

interface Props {
  user: User | null;
  action: string;
  date: string;
  ai?: boolean;
}

export function UserChip({ user, action, date, ai }: Props) {
  return (
    <div className="flex items-center gap-2 text-xs text-slate-500 dark:text-slate-400">
      {ai || !user ? (
        <span className="inline-flex h-6 w-6 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white">
          <Bot className="h-3.5 w-3.5" />
        </span>
      ) : (
        <Avatar name={user.username} size="sm" />
      )}
      <span>
        {ai || !user ? (
          <span className="font-medium text-violet-600 dark:text-violet-300">AI Assistant</span>
        ) : (
          <>
            <Link
              to={`/users/${user.username}`}
              className="font-medium text-brand-600 hover:underline dark:text-brand-100"
            >
              {user.username}
            </Link>{" "}
            <span title="reputation">· {compactNumber(user.reputation)}</span>
          </>
        )}{" "}
        {action} <time dateTime={date}>{timeAgo(date)}</time>
      </span>
    </div>
  );
}
