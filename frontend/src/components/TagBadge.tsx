import { Link } from "react-router-dom";

export function TagBadge({ name }: { name: string }) {
  return (
    <Link
      to={`/questions?tag=${encodeURIComponent(name)}`}
      className="inline-block rounded-md bg-brand-50 px-2 py-0.5 text-xs font-medium text-brand-700 hover:bg-brand-100 dark:bg-brand-500/15 dark:text-brand-100 dark:hover:bg-brand-500/25"
    >
      {name}
    </Link>
  );
}
