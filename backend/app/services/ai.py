"""AI provider abstraction.

`ClaudeProvider` talks to the Anthropic API; `MockProvider` produces deterministic
output so the platform works (and tests run) without an API key.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Protocol

from app.config import Settings, get_settings
from app.utils.text import excerpt, normalize_tags, tokenize

logger = logging.getLogger(__name__)

ANSWER_SYSTEM_PROMPT = (
    "You are an expert assistant on a community Q&A platform, similar to Stack Overflow. "
    "Write a clear, accurate, well-structured answer to the user's question in GitHub-flavored "
    "Markdown. Lead with the direct answer, then explain the reasoning. Include code examples "
    "in fenced code blocks when they help. If the question is ambiguous, state your assumptions. "
    "If you are not sure about something, say so rather than guessing."
)

CHAT_SYSTEM_PROMPT = (
    "You are the AI assistant of a community Q&A platform. Help users understand technical "
    "topics, debug problems, and write good questions. Answer in GitHub-flavored Markdown and "
    "keep answers focused."
)

TAGS_SYSTEM_PROMPT = (
    "You assign topic tags to questions on a Q&A platform. Reply with a JSON array of 1 to 5 "
    "short lowercase tags (for example [\"python\", \"fastapi\", \"sqlalchemy\"]) and nothing else. "
    "Prefer well-known technology names. Use hyphens instead of spaces."
)

IMPROVE_SYSTEM_PROMPT = (
    "You help users improve questions before they post them on a Q&A platform. Rewrite the "
    "question so it is specific, has a descriptive title, and includes what the user tried and "
    "what they expected. Keep the author's meaning and do not invent facts such as error "
    "messages or versions they did not mention. Reply with a JSON object with keys \"title\" "
    "(string), \"body\" (Markdown string) and \"tips\" (array of short strings explaining what "
    "you changed) and nothing else."
)

SUMMARY_SYSTEM_PROMPT = (
    "Summarize a Q&A thread for a reader who wants the gist quickly. In 3 to 6 Markdown bullet "
    "points state the problem, the main proposed solutions, and which answer was accepted or "
    "most upvoted. Do not add information that is not in the thread."
)


class AIError(Exception):
    """Raised when the AI provider cannot produce a response."""


@dataclass
class ChatTurn:
    role: str
    content: str


class AIProvider(Protocol):
    name: str

    def answer_question(self, title: str, body: str, tags: list[str]) -> str: ...

    def suggest_tags(self, title: str, body: str) -> list[str]: ...

    def improve_question(self, title: str, body: str) -> dict: ...

    def summarize_thread(self, thread: str) -> str: ...

    def chat(self, history: list[ChatTurn]) -> str: ...

    def stream_chat(self, history: list[ChatTurn]) -> Iterator[str]: ...


def format_question(title: str, body: str, tags: list[str]) -> str:
    tag_line = f"\nTags: {', '.join(tags)}" if tags else ""
    return f"Title: {title}{tag_line}\n\n{body}"


def _extract_json(text: str):
    """Parse the first JSON value in a model reply, tolerating surrounding prose or fences."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    for opener, closer in (("[", "]"), ("{", "}")):
        start, end = text.find(opener), text.rfind(closer)
        if start != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise AIError("AI response was not valid JSON")


class ClaudeProvider:
    name = "claude"

    def __init__(self, settings: Settings):
        import anthropic

        self._anthropic = anthropic
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self.model = settings.ai_model
        self.effort = settings.ai_effort
        self.max_tokens = settings.ai_max_tokens

    def _request_kwargs(self, system: str, messages: list[dict]) -> dict:
        return {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": system,
            "messages": messages,
            "output_config": {"effort": self.effort},
            # On a safety decline, let the API re-run the request on its recommended fallback model.
            "betas": ["server-side-fallback-2026-07-01"],
            "fallbacks": "default",
        }

    def _complete(self, system: str, messages: list[dict]) -> str:
        try:
            with self.client.beta.messages.stream(**self._request_kwargs(system, messages)) as stream:
                message = stream.get_final_message()
        except self._anthropic.APIStatusError as exc:
            logger.warning("Anthropic API error %s: %s", exc.status_code, exc.message)
            raise AIError(f"AI service returned an error ({exc.status_code})") from exc
        except self._anthropic.APIConnectionError as exc:
            raise AIError("Could not reach the AI service") from exc

        if message.stop_reason == "refusal":
            raise AIError("The AI declined to answer this request")
        text = "".join(block.text for block in message.content if block.type == "text").strip()
        if not text:
            raise AIError("AI returned an empty response")
        return text

    def answer_question(self, title: str, body: str, tags: list[str]) -> str:
        return self._complete(ANSWER_SYSTEM_PROMPT, [{"role": "user", "content": format_question(title, body, tags)}])

    def suggest_tags(self, title: str, body: str) -> list[str]:
        reply = self._complete(TAGS_SYSTEM_PROMPT, [{"role": "user", "content": format_question(title, body, [])}])
        data = _extract_json(reply)
        if not isinstance(data, list):
            raise AIError("AI returned tags in an unexpected format")
        return normalize_tags([str(t) for t in data])

    def improve_question(self, title: str, body: str) -> dict:
        reply = self._complete(IMPROVE_SYSTEM_PROMPT, [{"role": "user", "content": format_question(title, body, [])}])
        data = _extract_json(reply)
        if not isinstance(data, dict) or "title" not in data or "body" not in data:
            raise AIError("AI returned an unexpected format")
        tips = data.get("tips") or []
        return {"title": str(data["title"])[:200], "body": str(data["body"]), "tips": [str(t) for t in tips][:10]}

    def summarize_thread(self, thread: str) -> str:
        return self._complete(SUMMARY_SYSTEM_PROMPT, [{"role": "user", "content": thread}])

    def chat(self, history: list[ChatTurn]) -> str:
        return self._complete(CHAT_SYSTEM_PROMPT, [{"role": t.role, "content": t.content} for t in history])

    def stream_chat(self, history: list[ChatTurn]) -> Iterator[str]:
        kwargs = self._request_kwargs(CHAT_SYSTEM_PROMPT, [{"role": t.role, "content": t.content} for t in history])
        try:
            with self.client.beta.messages.stream(**kwargs) as stream:
                yield from stream.text_stream
                if stream.get_final_message().stop_reason == "refusal":
                    raise AIError("The AI declined to answer this request")
        except self._anthropic.APIStatusError as exc:
            raise AIError(f"AI service returned an error ({exc.status_code})") from exc
        except self._anthropic.APIConnectionError as exc:
            raise AIError("Could not reach the AI service") from exc


KNOWN_TAGS = (
    "python javascript typescript java go rust c++ c# php ruby kotlin swift sql postgresql mysql "
    "sqlite mongodb redis docker kubernetes aws react vue angular node.js django flask fastapi "
    "git linux bash html css api rest graphql pandas numpy machine-learning testing"
).split()


class MockProvider:
    """Deterministic offline provider used without an API key and in tests."""

    name = "mock"

    def answer_question(self, title: str, body: str, tags: list[str]) -> str:
        topic = ", ".join(tags) if tags else "this topic"
        return (
            f"**AI-generated answer (offline mode)**\n\n"
            f"You asked: *{title}*\n\n"
            f"Here is a general approach for questions about {topic}:\n\n"
            "1. Reproduce the problem with the smallest possible example.\n"
            "2. Read the full error message and stack trace carefully.\n"
            "3. Check the official documentation for the APIs involved.\n"
            "4. Add logging around the failing code to inspect the actual values.\n\n"
            "_Configure `ANTHROPIC_API_KEY` to get real answers from Claude._"
        )

    def suggest_tags(self, title: str, body: str) -> list[str]:
        words = tokenize(f"{title} {body}")
        found = [t for t in KNOWN_TAGS if t in words or t.replace(".", "") in words]
        return normalize_tags(found or sorted(words, key=len, reverse=True)[:3])

    def improve_question(self, title: str, body: str) -> dict:
        clean_title = title.strip().rstrip("?.!")
        clean_title = clean_title[:1].upper() + clean_title[1:]
        if not clean_title.lower().startswith(("how", "why", "what", "when", "which", "can", "is")):
            clean_title = f"How do I fix: {clean_title}"
        improved_body = (
            f"{body.strip()}\n\n"
            "**What I tried:**\n\n- ...\n\n"
            "**Expected behavior:**\n\n...\n\n"
            "**Actual behavior:**\n\n..."
        )
        return {
            "title": f"{clean_title}?"[:200],
            "body": improved_body,
            "tips": [
                "Phrase the title as a specific question.",
                "Describe what you already tried.",
                "State the expected and the actual behavior.",
            ],
        }

    def summarize_thread(self, thread: str) -> str:
        first_line = thread.strip().splitlines()[0] if thread.strip() else "the question"
        answers = thread.count("--- Answer")
        return f"- **Question:** {excerpt(first_line, 150)}\n- **Answers so far:** {answers}"

    def chat(self, history: list[ChatTurn]) -> str:
        last = history[-1].content if history else ""
        return (
            f"(offline mode) You said: \"{excerpt(last, 200)}\". "
            "Set `ANTHROPIC_API_KEY` to chat with Claude."
        )

    def stream_chat(self, history: list[ChatTurn]) -> Iterator[str]:
        for word in self.chat(history).split(" "):
            yield word + " "


_provider: AIProvider | None = None


def build_provider(settings: Settings) -> AIProvider:
    choice = settings.ai_provider.lower()
    if choice == "mock":
        return MockProvider()
    if choice == "claude" or (choice == "auto" and settings.anthropic_api_key):
        return ClaudeProvider(settings)
    return MockProvider()


def get_ai_provider() -> AIProvider:
    global _provider
    if _provider is None:
        _provider = build_provider(get_settings())
    return _provider
