import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { setToken } from "../api/client";
import { VoteControls } from "../components/VoteControls";
import { useAuth } from "../context/AuthContext";
import { mockFetch, renderWithProviders, sampleUser } from "./utils";

/** Render the controls only once the session has been restored. */
function WhenLoggedIn({ onVote }: { onVote: (value: number) => Promise<{ score: number; my_vote: number }> }) {
  const { user } = useAuth();
  return user ? <VoteControls score={3} myVote={0} onVote={onVote} /> : null;
}

describe("VoteControls", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("asks anonymous users to log in", async () => {
    mockFetch({});
    const onVote = vi.fn();
    renderWithProviders(<VoteControls score={3} myVote={0} onVote={onVote} />);
    await userEvent.click(screen.getByLabelText("Upvote"));
    expect(onVote).not.toHaveBeenCalled();
    expect(await screen.findByText("Log in to vote")).toBeInTheDocument();
  });

  it("toggles votes for signed-in users", async () => {
    setToken("tok");
    mockFetch({ "GET /api/auth/me": { ...sampleUser, email: "a@example.com" } });
    const onVote = vi
      .fn()
      .mockResolvedValueOnce({ score: 4, my_vote: 1 })
      .mockResolvedValueOnce({ score: 3, my_vote: 0 });
    renderWithProviders(<WhenLoggedIn onVote={onVote} />);

    await userEvent.click(await screen.findByLabelText("Upvote"));
    expect(onVote).toHaveBeenCalledWith(1);
    await waitFor(() => expect(screen.getByTestId("score")).toHaveTextContent("4"));

    await userEvent.click(screen.getByLabelText("Upvote"));
    expect(onVote).toHaveBeenLastCalledWith(0);
    await waitFor(() => expect(screen.getByTestId("score")).toHaveTextContent("3"));
  });
});
