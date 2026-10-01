import { afterEach, describe, expect, it, vi } from "vitest";

import { parseSseBlock, streamChat } from "../api/stream";

function sseResponse(chunks: string[]): Response {
  const encoder = new TextEncoder();
  const body = new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(encoder.encode(chunk));
      controller.close();
    },
  });
  return new Response(body, { status: 200, headers: { "Content-Type": "text/event-stream" } });
}

describe("server-sent events", () => {
  afterEach(() => vi.unstubAllGlobals());

  it("parses a block", () => {
    expect(parseSseBlock('event: delta\ndata: {"text":"hi"}')).toEqual({ event: "delta", data: { text: "hi" } });
    expect(parseSseBlock("event: ping")).toBeNull();
    expect(parseSseBlock("data: not-json")).toBeNull();
  });

  it("streams deltas split across network chunks", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        sseResponse([
          'event: start\ndata: {"conversation_id": 7}\n\nevent: del',
          'ta\ndata: {"text": "Hel"}\n\nevent: delta\ndata: {"text": "lo"}\n\n',
          'event: done\ndata: {"message_id": 1}\n\n',
        ]),
      ),
    );
    const deltas: string[] = [];
    const started: number[] = [];
    const id = await streamChat("hi", undefined, { onStart: (n) => started.push(n), onDelta: (t) => deltas.push(t) });
    expect(id).toBe(7);
    expect(started).toEqual([7]);
    expect(deltas.join("")).toBe("Hello");
  });

  it("throws on an error event", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => sseResponse(['event: error\ndata: {"detail": "AI down"}\n\n'])),
    );
    await expect(streamChat("hi", 1, { onDelta: () => undefined })).rejects.toThrow("AI down");
  });

  it("throws when the request is rejected", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => new Response(JSON.stringify({ detail: "Not authenticated" }), { status: 401 })),
    );
    await expect(streamChat("hi", undefined, { onDelta: () => undefined })).rejects.toMatchObject({ status: 401 });
  });
});
