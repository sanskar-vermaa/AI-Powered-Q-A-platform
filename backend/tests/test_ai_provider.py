from types import SimpleNamespace

import pytest

from app.config import Settings
from app.services import ai as ai_service
from app.services.ai import AIError, ChatTurn, ClaudeProvider, MockProvider, _extract_json, build_provider


class FakeStream:
    def __init__(self, text, stop_reason="end_turn"):
        self.text = text
        self.stop_reason = stop_reason

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        yield from self.text.split(" ")

    def get_final_message(self):
        blocks = [SimpleNamespace(type="thinking", thinking=""), SimpleNamespace(type="text", text=self.text)]
        return SimpleNamespace(stop_reason=self.stop_reason, content=blocks)


class FakeMessages:
    def __init__(self, reply, stop_reason="end_turn"):
        self.reply = reply
        self.stop_reason = stop_reason
        self.calls = []

    def stream(self, **kwargs):
        self.calls.append(kwargs)
        return FakeStream(self.reply, self.stop_reason)


def claude_with(reply, stop_reason="end_turn"):
    provider = ClaudeProvider(Settings(anthropic_api_key="test-key", ai_provider="claude"))
    messages = FakeMessages(reply, stop_reason)
    provider.client = SimpleNamespace(beta=SimpleNamespace(messages=messages))
    return provider, messages


def test_build_provider_selection():
    assert build_provider(Settings(ai_provider="mock", anthropic_api_key="k")).name == "mock"
    assert build_provider(Settings(ai_provider="auto", anthropic_api_key=None)).name == "mock"
    assert build_provider(Settings(ai_provider="auto", anthropic_api_key="k")).name == "claude"


def test_claude_answer_request_shape():
    provider, messages = claude_with("Use json.loads.")
    assert provider.answer_question("Parse JSON?", "How?", ["python"]) == "Use json.loads."
    call = messages.calls[0]
    assert call["model"] == "claude-opus-5-5"
    assert call["fallbacks"] == "default"
    assert call["betas"] == ["server-side-fallback-2026-07-01"]
    assert call["output_config"] == {"effort": "medium"}
    assert "Tags: python" in call["messages"][0]["content"]


def test_claude_refusal_raises():
    provider, _ = claude_with("", stop_reason="refusal")
    with pytest.raises(AIError):
        provider.answer_question("t", "b", [])


def test_claude_empty_reply_raises():
    provider, _ = claude_with("   ")
    with pytest.raises(AIError):
        provider.chat([ChatTurn("user", "hi")])


def test_claude_suggest_tags_parses_json():
    provider, _ = claude_with('Here you go: ["Python", "FastAPI", "python"]')
    assert provider.suggest_tags("t", "b") == ["python", "fastapi"]


def test_claude_improve_question_parses_fenced_json():
    reply = '```json\n{"title": "How do I X?", "body": "Details", "tips": ["Be specific"]}\n```'
    provider, _ = claude_with(reply)
    assert provider.improve_question("x", "y") == {"title": "How do I X?", "body": "Details", "tips": ["Be specific"]}


def test_claude_improve_question_rejects_bad_shape():
    provider, _ = claude_with('["not", "an", "object"]')
    with pytest.raises(AIError):
        provider.improve_question("x", "y")


def test_claude_stream_chat():
    provider, messages = claude_with("hello there friend")
    assert "".join(provider.stream_chat([ChatTurn("user", "hi")])) == "hellotherefriend"
    assert messages.calls[0]["messages"] == [{"role": "user", "content": "hi"}]


def test_extract_json_errors():
    with pytest.raises(AIError):
        _extract_json("no json here")


def test_mock_provider_is_deterministic():
    mock = MockProvider()
    assert mock.answer_question("T", "B", []) == mock.answer_question("T", "B", [])
    assert mock.suggest_tags("Kubernetes and Docker", "") == ["docker", "kubernetes"]
    assert "".join(mock.stream_chat([ChatTurn("user", "ping")])).strip() == mock.chat([ChatTurn("user", "ping")])


def test_get_ai_provider_is_cached(monkeypatch):
    monkeypatch.setattr(ai_service, "_provider", None)
    assert ai_service.get_ai_provider() is ai_service.get_ai_provider()
