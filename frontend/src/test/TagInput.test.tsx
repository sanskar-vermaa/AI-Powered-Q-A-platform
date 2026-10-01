import { fireEvent, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { useState } from "react";
import { describe, expect, it } from "vitest";

import { normalizeTag, TagInput } from "../components/TagInput";

function Harness({ initial = [] as string[] }) {
  const [tags, setTags] = useState(initial);
  return (
    <>
      <TagInput id="tags" tags={tags} onChange={setTags} max={3} />
      <output data-testid="tags">{tags.join(",")}</output>
    </>
  );
}

describe("TagInput", () => {
  it("normalizes tag text like the backend", () => {
    expect(normalizeTag(" Machine Learning ")).toBe("machine-learning");
    expect(normalizeTag("C++")).toBe("c++");
    expect(normalizeTag("py$thon!")).toBe("python");
  });

  it("adds tags on Enter and removes them", async () => {
    render(<Harness />);
    const input = screen.getByRole("textbox");
    await userEvent.type(input, "React{Enter}TypeScript{Enter}react{Enter}");
    expect(screen.getByTestId("tags")).toHaveTextContent("react,typescript");
    await userEvent.click(screen.getByLabelText("Remove react"));
    expect(screen.getByTestId("tags")).toHaveTextContent("typescript");
  });

  it("removes the last tag with Backspace on empty input", () => {
    render(<Harness initial={["a", "b"]} />);
    fireEvent.keyDown(screen.getByRole("textbox"), { key: "Backspace" });
    expect(screen.getByTestId("tags")).toHaveTextContent("a");
  });

  it("disables input at the maximum", () => {
    render(<Harness initial={["a", "b", "c"]} />);
    expect(screen.getByRole("textbox")).toBeDisabled();
  });
});
