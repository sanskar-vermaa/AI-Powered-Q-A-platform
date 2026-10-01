import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import type { QuestionSummary } from "../api/types";
import { QuestionCard } from "../components/QuestionCard";
import { sampleUser } from "./utils";

const question: QuestionSummary = {
  id: 5,
  title: "How do I center a div?",
  excerpt: "I tried everything.",
  author: sampleUser,
  tags: ["css", "html"],
  score: 1,
  views: 1200,
  answer_count: 2,
  has_accepted_answer: true,
  created_at: new Date().toISOString(),
};

describe("QuestionCard", () => {
  it("shows the title, stats, tags and author", () => {
    render(
      <MemoryRouter>
        <QuestionCard question={question} />
      </MemoryRouter>,
    );
    expect(screen.getByRole("link", { name: question.title })).toHaveAttribute("href", "/questions/5");
    expect(screen.getByText("vote")).toBeInTheDocument();
    expect(screen.getByText("answers")).toBeInTheDocument();
    expect(screen.getByText("1.2K")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "css" })).toHaveAttribute("href", "/questions?tag=css");
    expect(screen.getByRole("link", { name: "alice" })).toBeInTheDocument();
  });
});
