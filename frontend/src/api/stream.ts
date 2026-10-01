import { ApiError, authHeaders } from "./client";

export interface StreamHandlers {
  onStart?: (conversationId: number) => void;
  onDelta: (text: string) => void;
}

/** Parse one server-sent-event block ("event: x\ndata: {...}"). */
export function parseSseBlock(block: string): { event: string; data: unknown } | null {
  let event = "message";
  const dataLines: string[] = [];
  for (const line of block.split("\n")) {
    if (line.startsWith("event:")) event = line.slice(6).trim();
    else if (line.startsWith("data:")) dataLines.push(line.slice(5).trim());
  }
  if (dataLines.length === 0) return null;
  try {
    return { event, data: JSON.parse(dataLines.join("\n")) };
  } catch {
    return null;
  }
}

/** Send a chat message and stream the assistant's reply. Resolves with the conversation id. */
export async function streamChat(
  message: string,
  conversationId: number | undefined,
  handlers: StreamHandlers,
  signal?: AbortSignal,
): Promise<number> {
  const response = await fetch("/api/chat/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ message, conversation_id: conversationId }),
    signal,
  });
  if (!response.ok || !response.body) {
    const body = await response.json().catch(() => null);
    throw new ApiError(response.status, body?.detail ?? "Chat request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let id = conversationId ?? 0;
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let boundary = buffer.indexOf("\n\n");
    while (boundary !== -1) {
      const parsed = parseSseBlock(buffer.slice(0, boundary));
      buffer = buffer.slice(boundary + 2);
      boundary = buffer.indexOf("\n\n");
      if (!parsed) continue;
      const data = parsed.data as Record<string, unknown>;
      if (parsed.event === "start") {
        id = data.conversation_id as number;
        handlers.onStart?.(id);
      } else if (parsed.event === "delta") {
        handlers.onDelta(data.text as string);
      } else if (parsed.event === "error") {
        throw new ApiError(502, (data.detail as string) ?? "AI error");
      }
    }
  }
  return id;
}
