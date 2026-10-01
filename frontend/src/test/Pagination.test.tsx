import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi } from "vitest";

import { pageWindow, Pagination } from "../components/Pagination";

describe("Pagination", () => {
  it("computes a compact page window", () => {
    expect(pageWindow(1, 5)).toEqual([1, 2, 3, 4, 5]);
    expect(pageWindow(5, 20)).toEqual([1, "…", 4, 5, 6, "…", 20]);
    expect(pageWindow(1, 20)).toEqual([1, 2, "…", 20]);
    expect(pageWindow(20, 20)).toEqual([1, "…", 19, 20]);
  });

  it("renders nothing for a single page", () => {
    const { container } = render(<Pagination page={1} pages={1} onChange={() => undefined} />);
    expect(container).toBeEmptyDOMElement();
  });

  it("navigates between pages", async () => {
    const onChange = vi.fn();
    render(<Pagination page={2} pages={4} onChange={onChange} />);
    expect(screen.getByRole("button", { name: "2" })).toHaveAttribute("aria-current", "page");
    await userEvent.click(screen.getByLabelText("Next page"));
    await userEvent.click(screen.getByRole("button", { name: "4" }));
    expect(onChange.mock.calls).toEqual([[3], [4]]);
  });
});
