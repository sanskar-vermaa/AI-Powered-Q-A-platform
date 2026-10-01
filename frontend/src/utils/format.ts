const UNITS: [Intl.RelativeTimeFormatUnit, number][] = [
  ["year", 365 * 24 * 3600],
  ["month", 30 * 24 * 3600],
  ["week", 7 * 24 * 3600],
  ["day", 24 * 3600],
  ["hour", 3600],
  ["minute", 60],
];

const relative = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

export function timeAgo(iso: string, now: Date = new Date()): string {
  const seconds = Math.round((new Date(iso).getTime() - now.getTime()) / 1000);
  for (const [unit, size] of UNITS) {
    if (Math.abs(seconds) >= size) return relative.format(Math.round(seconds / size), unit);
  }
  return "just now";
}

/** True when a post was changed noticeably after it was created (ignores same-request timestamp jitter). */
export function wasEdited(createdAt: string, updatedAt: string, thresholdSeconds = 60): boolean {
  return new Date(updatedAt).getTime() - new Date(createdAt).getTime() > thresholdSeconds * 1000;
}

export function compactNumber(value: number): string {
  return new Intl.NumberFormat("en", { notation: "compact", maximumFractionDigits: 1 }).format(value);
}

export function pluralize(count: number, singular: string, plural = `${singular}s`): string {
  return `${compactNumber(count)} ${count === 1 ? singular : plural}`;
}

export function initials(name: string): string {
  return name.slice(0, 2).toUpperCase();
}

/** Deterministic avatar color for a username. */
export function avatarColor(name: string): string {
  const colors = ["bg-indigo-500", "bg-emerald-500", "bg-amber-500", "bg-rose-500", "bg-sky-500", "bg-violet-500"];
  let hash = 0;
  for (const char of name) hash = (hash * 31 + char.charCodeAt(0)) >>> 0;
  return colors[hash % colors.length];
}
