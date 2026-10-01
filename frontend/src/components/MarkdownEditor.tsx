import { useState } from "react";

import { Markdown } from "./Markdown";

interface Props {
  id?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  rows?: number;
  minLength?: number;
}

export function MarkdownEditor({ id, value, onChange, placeholder, rows = 10, minLength }: Props) {
  const [tab, setTab] = useState<"write" | "preview">("write");
  const tabClass = (name: string) =>
    `px-3 py-1.5 text-sm font-medium rounded-md ${
      tab === name
        ? "bg-white text-slate-900 shadow-sm dark:bg-slate-800 dark:text-white"
        : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
    }`;

  return (
    <div className="overflow-hidden rounded-lg border border-slate-300 dark:border-slate-700">
      <div className="flex items-center justify-between gap-1 border-b border-slate-200 bg-slate-100 p-1 dark:border-slate-700 dark:bg-slate-900">
        <div className="flex gap-1" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={tab === "write"}
            className={tabClass("write")}
            onClick={() => setTab("write")}
          >
            Write
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={tab === "preview"}
            className={tabClass("preview")}
            onClick={() => setTab("preview")}
          >
            Preview
          </button>
        </div>
        <span className="px-2 text-xs text-slate-400">
          Markdown supported{minLength ? ` · ${value.trim().length}/${minLength}+ chars` : ""}
        </span>
      </div>
      {tab === "write" ? (
        <textarea
          id={id}
          className="block w-full resize-y border-0 bg-white p-3 font-mono text-sm focus:outline-none focus:ring-0 dark:bg-slate-950"
          rows={rows}
          value={value}
          placeholder={placeholder}
          onChange={(event) => onChange(event.target.value)}
        />
      ) : (
        <div className="min-h-[10rem] bg-white p-4 dark:bg-slate-950">
          {value.trim() ? <Markdown>{value}</Markdown> : <p className="text-sm text-slate-400">Nothing to preview.</p>}
        </div>
      )}
    </div>
  );
}
