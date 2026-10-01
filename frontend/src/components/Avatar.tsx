import { avatarColor, initials } from "../utils/format";

export function Avatar({ name, size = "md" }: { name: string; size?: "sm" | "md" | "lg" }) {
  const sizes = { sm: "h-6 w-6 text-[10px]", md: "h-8 w-8 text-xs", lg: "h-16 w-16 text-xl" };
  return (
    <span
      aria-hidden
      className={`inline-flex shrink-0 items-center justify-center rounded-full font-semibold text-white ${sizes[size]} ${avatarColor(name)}`}
    >
      {initials(name)}
    </span>
  );
}
