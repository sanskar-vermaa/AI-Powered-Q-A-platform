import { X } from "lucide-react";
import { useState, type KeyboardEvent } from "react";

interface Props {
  id?: string;
  tags: string[];
  onChange: (tags: string[]) => void;
  max?: number;
}

export function normalizeTag(raw: string): string {
  return raw
    .trim()
    .toLowerCase()
    .replace(/\s+/g, "-")
    .replace(/[^a-z0-9+#.-]/g, "")
    .replace(/^[-.]+|[-.]+$/g, "")
    .slice(0, 35);
}

export function TagInput({ id, tags, onChange, max = 5 }: Props) {
  const [draft, setDraft] = useState("");

  function add(raw: string) {
    const tag = normalizeTag(raw);
    if (tag && !tags.includes(tag) && tags.length < max) onChange([...tags, tag]);
    setDraft("");
  }

  function onKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === "Enter" || event.key === "," || event.key === " ") {
      event.preventDefault();
      add(draft);
    } else if (event.key === "Backspace" && !draft && tags.length) {
      onChange(tags.slice(0, -1));
    }
  }

  return (
    <div className="input flex flex-wrap items-center gap-1.5">
      {tags.map((tag) => (
        <span
          key={tag}
          className="inline-flex items-center gap-1 rounded-md bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 dark:bg-brand-500/15 dark:text-brand-100"
        >
          {tag}
          <button type="button" aria-label={`Remove ${tag}`} onClick={() => onChange(tags.filter((t) => t !== tag))}>
            <X className="h-3 w-3" />
          </button>
        </span>
      ))}
      <input
        id={id}
        className="min-w-[8rem] flex-1 border-0 bg-transparent p-0 text-sm focus:outline-none focus:ring-0"
        value={draft}
        placeholder={tags.length >= max ? `Maximum ${max} tags` : "Add a tag and press Enter"}
        disabled={tags.length >= max}
        onChange={(event) => setDraft(event.target.value)}
        onKeyDown={onKeyDown}
        onBlur={() => draft && add(draft)}
      />
    </div>
  );
}
