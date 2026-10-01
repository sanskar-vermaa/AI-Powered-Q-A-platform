import { ChevronLeft, ChevronRight } from "lucide-react";

interface Props {
  page: number;
  pages: number;
  onChange: (page: number) => void;
}

export function pageWindow(page: number, pages: number): (number | "…")[] {
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1);
  const result: (number | "…")[] = [1];
  const start = Math.max(2, page - 1);
  const end = Math.min(pages - 1, page + 1);
  if (start > 2) result.push("…");
  for (let i = start; i <= end; i++) result.push(i);
  if (end < pages - 1) result.push("…");
  result.push(pages);
  return result;
}

export function Pagination({ page, pages, onChange }: Props) {
  if (pages <= 1) return null;
  return (
    <nav className="flex items-center justify-center gap-1" aria-label="Pagination">
      <button
        className="btn-ghost px-2"
        disabled={page <= 1}
        onClick={() => onChange(page - 1)}
        aria-label="Previous page"
      >
        <ChevronLeft className="h-4 w-4" />
      </button>
      {pageWindow(page, pages).map((item, index) =>
        item === "…" ? (
          <span key={`gap-${index}`} className="px-2 text-slate-400">
            …
          </span>
        ) : (
          <button
            key={item}
            aria-current={item === page ? "page" : undefined}
            className={item === page ? "btn-primary px-3" : "btn-ghost px-3"}
            onClick={() => onChange(item)}
          >
            {item}
          </button>
        ),
      )}
      <button
        className="btn-ghost px-2"
        disabled={page >= pages}
        onClick={() => onChange(page + 1)}
        aria-label="Next page"
      >
        <ChevronRight className="h-4 w-4" />
      </button>
    </nav>
  );
}
