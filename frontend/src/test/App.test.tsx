import { screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { AppRoutes } from "../App";
import { mockFetch, renderWithProviders, sampleUser } from "./utils";

const emptyPage = { items: [], total: 0, page: 1, page_size: 15, pages: 0 };

describe("App routes", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("renders the questions page", async () => {
    mockFetch({
      "GET /api/questions": {
        ...emptyPage,
        items: [
          {
            id: 1,
            title: "First question title",
            excerpt: "Body",
            author: sampleUser,
            tags: ["python"],
            score: 0,
            views: 0,
            answer_count: 0,
            has_accepted_answer: false,
            created_at: new Date().toISOString(),
          },
        ],
        total: 1,
        pages: 1,
      },
    });
    renderWithProviders(<AppRoutes />, { route: "/questions" });
    expect(await screen.findByRole("heading", { name: "All questions" })).toBeInTheDocument();
    expect(await screen.findByText("First question title")).toBeInTheDocument();
    expect(screen.getByText("1 question")).toBeInTheDocument();
  });

  it("shows a 404 page for unknown routes", async () => {
    mockFetch({});
    renderWithProviders(<AppRoutes />, { route: "/nope" });
    expect(await screen.findByText("Page not found")).toBeInTheDocument();
  });

  it("redirects anonymous users away from protected pages", async () => {
    mockFetch({ "GET /api/questions": emptyPage });
    renderWithProviders(<AppRoutes />, { route: "/ask" });
    expect(await screen.findByRole("heading", { name: "Welcome back" })).toBeInTheDocument();
  });

  it("hides moderation links from regular users", async () => {
    mockFetch({
      "GET /api/stats": { users: 0, questions: 0, answers: 0, ai_answers: 0, tags: 0, answered_ratio: 0 },
      "GET /api/questions": emptyPage,
    });
    renderWithProviders(<AppRoutes />, { route: "/" });
    expect(await screen.findByText("No questions yet")).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Moderation" })).toBeNull();
  });
});
