import { render } from "@testing-library/react";
import type { ReactElement } from "react";
import { MemoryRouter } from "react-router-dom";
import { vi } from "vitest";

import { AuthProvider } from "../context/AuthContext";
import { ThemeProvider } from "../context/ThemeContext";
import { ToastProvider } from "../context/ToastContext";

export function renderWithProviders(ui: ReactElement, { route = "/" }: { route?: string } = {}) {
  return render(
    <ThemeProvider>
      <ToastProvider>
        <AuthProvider>
          <MemoryRouter initialEntries={[route]}>{ui}</MemoryRouter>
        </AuthProvider>
      </ToastProvider>
    </ThemeProvider>,
  );
}

export function jsonResponse(body: unknown, status = 200): Response {
  return new Response(status === 204 ? null : JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

/** Mock fetch with a routing table: "METHOD /path" -> response body (or a function). */
export function mockFetch(routes: Record<string, unknown | ((init?: RequestInit) => Response)>) {
  const fn = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = typeof input === "string" ? input : input.toString();
    const path = url.split("?")[0];
    const key = `${init?.method ?? "GET"} ${path}`;
    if (!(key in routes)) return jsonResponse({ detail: `unmocked ${key}` }, 404);
    const handler = routes[key];
    return typeof handler === "function" ? (handler as (init?: RequestInit) => Response)(init) : jsonResponse(handler);
  });
  vi.stubGlobal("fetch", fn);
  return fn;
}

export const sampleUser = {
  id: 1,
  username: "alice",
  bio: "",
  reputation: 42,
  role: "user" as const,
  created_at: "2026-01-01T00:00:00Z",
};
