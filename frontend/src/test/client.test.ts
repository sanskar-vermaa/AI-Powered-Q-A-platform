import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, getToken, query, request, setToken } from "../api/client";
import { jsonResponse, mockFetch } from "./utils";

describe("api client", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("builds query strings and skips empty values", () => {
    expect(query({ a: 1, b: "", c: undefined, d: "x y" })).toBe("?a=1&d=x+y");
    expect(query({})).toBe("");
  });

  it("stores and clears the token", () => {
    setToken("abc");
    expect(getToken()).toBe("abc");
    setToken(null);
    expect(getToken()).toBeNull();
  });

  it("sends the bearer token and JSON body", async () => {
    setToken("tok");
    const fetchMock = mockFetch({ "POST /api/thing": { ok: true } });
    await expect(request("POST", "/api/thing", { a: 1 })).resolves.toEqual({ ok: true });
    const init = fetchMock.mock.calls[0][1] as RequestInit;
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer tok");
    expect(init.body).toBe('{"a":1}');
  });

  it("returns undefined for 204 responses", async () => {
    mockFetch({ "DELETE /api/thing": () => jsonResponse(null, 204) });
    await expect(request("DELETE", "/api/thing")).resolves.toBeUndefined();
  });

  it("raises ApiError with the server detail", async () => {
    mockFetch({ "GET /api/thing": () => jsonResponse({ detail: "Nope" }, 403) });
    await expect(request("GET", "/api/thing")).rejects.toMatchObject({ status: 403, message: "Nope" });
  });

  it("formats validation errors", async () => {
    mockFetch({
      "POST /api/thing": () =>
        jsonResponse({ detail: [{ loc: ["body", "title"], msg: "String should have at least 10 characters" }] }, 422),
    });
    const error = (await request("POST", "/api/thing", {}).catch((e) => e)) as ApiError;
    expect(error).toBeInstanceOf(ApiError);
    expect(error.message).toBe("title: String should have at least 10 characters");
  });
});
