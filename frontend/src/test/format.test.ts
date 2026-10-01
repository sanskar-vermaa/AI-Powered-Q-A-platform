import { describe, expect, it } from "vitest";

import { avatarColor, compactNumber, initials, pluralize, timeAgo, wasEdited } from "../utils/format";

describe("format utilities", () => {
  const now = new Date("2026-06-15T12:00:00Z");

  it("formats relative times", () => {
    expect(timeAgo("2026-06-15T11:59:30Z", now)).toBe("just now");
    expect(timeAgo("2026-06-15T11:55:00Z", now)).toBe("5 minutes ago");
    expect(timeAgo("2026-06-14T12:00:00Z", now)).toBe("yesterday");
    expect(timeAgo("2025-06-15T12:00:00Z", now)).toBe("last year");
  });

  it("compacts large numbers", () => {
    expect(compactNumber(999)).toBe("999");
    expect(compactNumber(1500)).toBe("1.5K");
  });

  it("pluralizes", () => {
    expect(pluralize(1, "answer")).toBe("1 answer");
    expect(pluralize(3, "answer")).toBe("3 answers");
    expect(pluralize(0, "reply", "replies")).toBe("0 replies");
  });

  it("detects real edits only", () => {
    expect(wasEdited("2026-06-15T12:00:00.000Z", "2026-06-15T12:00:00.004Z")).toBe(false);
    expect(wasEdited("2026-06-15T12:00:00Z", "2026-06-15T12:05:00Z")).toBe(true);
  });

  it("builds avatar initials and stable colors", () => {
    expect(initials("alice")).toBe("AL");
    expect(avatarColor("alice")).toBe(avatarColor("alice"));
  });
});
