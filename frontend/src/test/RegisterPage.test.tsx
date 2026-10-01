import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RegisterPage, validatePassword } from "../pages/RegisterPage";
import { mockFetch, renderWithProviders } from "./utils";

describe("RegisterPage", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("validates passwords like the backend", () => {
    expect(validatePassword("short1")).toMatch(/at least 8/);
    expect(validatePassword("lettersonly")).toMatch(/letter and a digit/);
    expect(validatePassword("letters123")).toBeUndefined();
  });

  it("blocks invalid input before calling the API", async () => {
    const fetchMock = mockFetch({});
    renderWithProviders(<RegisterPage />, { route: "/register" });
    await userEvent.type(screen.getByLabelText("Username"), "bad name");
    await userEvent.type(screen.getByLabelText("Email"), "a@example.com");
    await userEvent.type(screen.getByLabelText("Password"), "password123");
    await userEvent.click(screen.getByRole("button", { name: "Sign up" }));
    expect(await screen.findByRole("alert")).toHaveTextContent("Username must be");
    expect(fetchMock.mock.calls.filter(([url]) => String(url).includes("register"))).toHaveLength(0);
  });
});
