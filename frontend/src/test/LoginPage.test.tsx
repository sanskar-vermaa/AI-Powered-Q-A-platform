import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

import { getToken } from "../api/client";
import { LoginPage } from "../pages/LoginPage";
import { jsonResponse, mockFetch, renderWithProviders, sampleUser } from "./utils";

function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/ask" element={<p>Ask page</p>} />
      <Route path="/" element={<p>Home page</p>} />
    </Routes>
  );
}

describe("LoginPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("logs in and redirects to the next page", async () => {
    mockFetch({
      "POST /api/auth/login": { access_token: "tok", token_type: "bearer" },
      "GET /api/auth/me": { ...sampleUser, email: "alice@example.com" },
    });
    renderWithProviders(<App />, { route: "/login?next=/ask" });
    await userEvent.type(screen.getByLabelText("Username or email"), "alice");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Ask page")).toBeInTheDocument();
    expect(getToken()).toBe("tok");
  });

  it("ignores external redirect targets", async () => {
    mockFetch({
      "POST /api/auth/login": { access_token: "tok" },
      "GET /api/auth/me": { ...sampleUser, email: "alice@example.com" },
    });
    renderWithProviders(<App />, { route: "/login?next=//evil.example.com" });
    await userEvent.type(screen.getByLabelText("Username or email"), "alice");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByText("Home page")).toBeInTheDocument();
  });

  it("shows the server error", async () => {
    mockFetch({ "POST /api/auth/login": () => jsonResponse({ detail: "Incorrect username or password" }, 401) });
    renderWithProviders(<App />, { route: "/login" });
    await userEvent.type(screen.getByLabelText("Username or email"), "alice");
    await userEvent.type(screen.getByLabelText("Password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: "Log in" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Incorrect username or password");
  });
});
