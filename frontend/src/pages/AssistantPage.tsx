import { Bot, MessageSquarePlus, Send, Square, Trash2 } from "lucide-react";
import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from "react";

import { api } from "../api/endpoints";
import { streamChat } from "../api/stream";
import type { Conversation } from "../api/types";
import { Avatar } from "../components/Avatar";
import { Markdown } from "../components/Markdown";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

interface Message {
  role: "user" | "assistant";
  content: string;
}

const SUGGESTIONS = [
  "Explain the difference between a process and a thread",
  "How do I write a good bug report?",
  "What is the time complexity of Python's sort?",
];

export function AssistantPage() {
  const { user } = useAuth();
  const toast = useToast();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<number>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [streaming, setStreaming] = useState(false);
  const abort = useRef<AbortController | null>(null);
  const pane = useRef<HTMLDivElement>(null);

  useEffect(() => {
    api.chat
      .conversations()
      .then(setConversations)
      .catch(() => undefined);
  }, []);

  useEffect(() => {
    // Scroll only the message pane; scrollIntoView would also scroll the page under the sticky header.
    if (pane.current) pane.current.scrollTop = pane.current.scrollHeight;
  }, [messages]);

  async function openConversation(id: number) {
    try {
      const detail = await api.chat.conversation(id);
      setActiveId(id);
      setMessages(detail.messages.map((m) => ({ role: m.role, content: m.content })));
    } catch (error) {
      toast.error(error);
    }
  }

  async function removeConversation(id: number) {
    try {
      await api.chat.remove(id);
      setConversations((current) => current.filter((c) => c.id !== id));
      if (id === activeId) newChat();
    } catch (error) {
      toast.error(error);
    }
  }

  function newChat() {
    abort.current?.abort();
    setActiveId(undefined);
    setMessages([]);
  }

  async function send(text: string) {
    const message = text.trim();
    if (!message || streaming) return;
    setInput("");
    setMessages((current) => [...current, { role: "user", content: message }, { role: "assistant", content: "" }]);
    setStreaming(true);
    const controller = new AbortController();
    abort.current = controller;
    try {
      const id = await streamChat(
        message,
        activeId,
        {
          onStart: (conversationId) => setActiveId(conversationId),
          onDelta: (delta) =>
            setMessages((current) => {
              const next = [...current];
              const last = next[next.length - 1];
              next[next.length - 1] = { ...last, content: last.content + delta };
              return next;
            }),
        },
        controller.signal,
      );
      if (!conversations.some((c) => c.id === id)) {
        api.chat
          .conversations()
          .then(setConversations)
          .catch(() => undefined);
      }
    } catch (error) {
      if ((error as Error).name !== "AbortError") toast.error(error);
    } finally {
      setStreaming(false);
      abort.current = null;
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault();
    send(input);
  }

  function onKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      send(input);
    }
  }

  return (
    <div className="grid h-[calc(100vh-9rem)] gap-4 md:grid-cols-[14rem_1fr]">
      <aside className="card hidden flex-col overflow-hidden md:flex">
        <div className="border-b border-slate-200 p-3 dark:border-slate-800">
          <button className="btn-primary w-full" onClick={newChat}>
            <MessageSquarePlus className="h-4 w-4" /> New chat
          </button>
        </div>
        <ul className="flex-1 overflow-y-auto p-2 text-sm">
          {conversations.map((c) => (
            <li key={c.id} className="group flex items-center gap-1">
              <button
                className={`flex-1 truncate rounded-md px-2 py-1.5 text-left ${c.id === activeId ? "bg-brand-50 text-brand-700 dark:bg-brand-500/15 dark:text-brand-100" : "hover:bg-slate-100 dark:hover:bg-slate-800"}`}
                onClick={() => openConversation(c.id)}
              >
                {c.title}
              </button>
              <button
                aria-label="Delete conversation"
                className="p-1 text-slate-400 opacity-0 hover:text-red-500 group-hover:opacity-100"
                onClick={() => removeConversation(c.id)}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="card flex min-h-0 flex-col">
        <div ref={pane} className="flex-1 space-y-6 overflow-y-auto p-4 sm:p-6">
          {messages.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-center">
              <span className="rounded-2xl bg-gradient-to-br from-violet-500 to-fuchsia-500 p-4 text-white shadow-lg">
                <Bot className="h-8 w-8" />
              </span>
              <div>
                <h1 className="text-xl font-semibold">AI Assistant</h1>
                <p className="text-sm text-slate-500">
                  Ask anything about programming, debugging, or writing better questions.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-2">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="btn-secondary text-xs" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            messages.map((m, index) => (
              <div key={index} className="flex gap-3">
                {m.role === "user" ? (
                  <Avatar name={user?.username ?? "you"} />
                ) : (
                  <span className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-fuchsia-500 text-white">
                    <Bot className="h-4 w-4" />
                  </span>
                )}
                <div className="min-w-0 flex-1 pt-1">
                  {m.role === "assistant" && !m.content && streaming ? (
                    <span className="inline-flex gap-1" aria-label="Assistant is typing">
                      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.15s]" />
                      <span className="h-2 w-2 animate-bounce rounded-full bg-slate-400 [animation-delay:0.3s]" />
                    </span>
                  ) : (
                    <Markdown>{m.content}</Markdown>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
        <form onSubmit={submit} className="flex items-end gap-2 border-t border-slate-200 p-3 dark:border-slate-800">
          <textarea
            className="input max-h-40 resize-none"
            rows={1}
            placeholder="Message the AI assistant… (Shift+Enter for a new line)"
            aria-label="Message"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={onKeyDown}
          />
          {streaming ? (
            <button
              type="button"
              className="btn-secondary"
              onClick={() => abort.current?.abort()}
              aria-label="Stop generating"
            >
              <Square className="h-4 w-4" />
            </button>
          ) : (
            <button className="btn-primary" disabled={!input.trim()} aria-label="Send message">
              <Send className="h-4 w-4" />
            </button>
          )}
        </form>
      </section>
    </div>
  );
}
