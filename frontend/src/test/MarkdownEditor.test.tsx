import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import { Markdown } from "../components/Markdown";
import { MarkdownEditor } from "../components/MarkdownEditor";

function Harness() {
  const [value, setValue] = useState("");
  return <MarkdownEditor value={value} onChange={setValue} minLength={20} />;
}

describe("Markdown", () => {
  it("renders Markdown and does not render raw HTML", () => {
    render(<Markdown>{"# Title\n\n**bold** <script>alert(1)</script>\n\n[link](https://example.com)"}</Markdown>);
    expect(screen.getByRole("heading", { name: "Title" })).toBeInTheDocument();
    expect(screen.getByText("bold").tagName).toBe("STRONG");
    expect(document.querySelector("script")).toBeNull();
    expect(screen.getByRole("link", { name: "link" })).toHaveAttribute("rel", "noopener noreferrer nofollow");
  });

  it("switches between write and preview", async () => {
    render(<Harness />);
    await userEvent.type(screen.getByRole("textbox"), "Some *emphasis*");
    expect(screen.getByText(/15\/20\+ chars/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole("tab", { name: "Preview" }));
    expect(screen.getByText("emphasis").tagName).toBe("EM");
  });
});
