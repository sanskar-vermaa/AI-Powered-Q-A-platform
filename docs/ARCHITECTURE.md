# Architecture

## Overview

```
Browser (React SPA) ──HTTP/JSON + SSE──▶ FastAPI ──SQLAlchemy──▶ Oracle / PostgreSQL / SQLite
                                            │
                                            └──Anthropic SDK──▶ Claude API (optional)
```

In production one container serves both the API (`/api/*`) and the built React app; unknown paths fall back to `index.html` so client-side routing works. In development, Vite serves the UI on port 5173 and proxies `/api` to the backend.

## Backend

| Layer | Location | Responsibility |
| --- | --- | --- |
| Routers | `app/routers/` | HTTP endpoints, input validation, permission checks |
| Schemas | `app/schemas/` | Pydantic request and response models |
| Services | `app/services/` | Business rules: AI, reputation, badges, notifications, search, tags |
| Models | `app/models/` | SQLAlchemy 2.0 typed ORM models |
| Serializers | `app/serializers.py` | Builds response dictionaries, batching counts to avoid N+1 queries |

### Authentication and roles
- Passwords are hashed with bcrypt (cost factor set by `BCRYPT_ROUNDS`).
- Login returns a signed JWT (HS256) sent as `Authorization: Bearer <token>`.
- Roles: `user`, `moderator`, `admin`. Suspended users (`is_active = false`) are rejected even with a valid token.

### AI provider layer
`app/services/ai.py` defines an `AIProvider` protocol with two implementations:

- **`ClaudeProvider`** calls the Claude API through the official `anthropic` SDK. Requests stream and collect the final message to avoid HTTP timeouts on long answers, set the reasoning `effort`, and enable server-side refusal fallbacks (`fallbacks: "default"`). A `refusal` stop reason, an empty reply or an API error becomes an `AIError`, which the API returns as `502`.
- **`MockProvider`** returns deterministic text so the product works offline and tests never call the network.

`AI_PROVIDER=auto` picks Claude when `ANTHROPIC_API_KEY` is set. Routes receive the provider through FastAPI dependency injection, so tests swap it out with `app.dependency_overrides`.

The chat assistant streams with server-sent events: `start` (conversation id), `delta` (text chunks), then `done` or `error`. The assistant message is saved when the stream completes.

### Database portability
The same models run on SQLite, PostgreSQL and Oracle. Choices that keep them portable:
- Explicit `Identity()` primary keys (Oracle has no implicit autoincrement).
- Optional text columns are nullable and coerced to `""` in schemas, because Oracle stores empty strings as `NULL`.
- Booleans compare with `== true()` instead of `IS TRUE`, which Oracle does not accept.
- Text (CLOB) columns are never used in `GROUP BY`.
- The circular `questions.accepted_answer_id → answers.id` foreign key is named and created with `use_alter`.
- A `UTCDateTime` column type always returns timezone-aware UTC datetimes.

The whole test suite runs against Oracle in CI to keep this true.

### Reputation and badges
`services/reputation.py` holds the point values. Votes are stored one per user per post, so changing or retracting a vote first reverses the previous effect. `services/badges.py` evaluates badge rules after relevant actions; each badge is awarded at most once.

### Search and duplicate detection
Listing search uses case-insensitive `LIKE` across title and body for every term. Duplicate detection (`services/search.py`) pre-filters candidates by title keywords, then ranks them by weighted Jaccard similarity of stop-word-filtered tokens.

## Frontend

- **React 19 + TypeScript + Vite**, styled with **Tailwind CSS 4** and the typography plugin.
- `src/api/` is a small typed fetch client. It stores the token in `localStorage`, turns FastAPI errors (including validation errors) into readable messages, and parses SSE for the chat stream.
- Contexts provide auth state, theme (dark mode without a flash on load) and toasts.
- Pages are lazy-loaded, so each route downloads only its own code.
- Markdown is rendered with `react-markdown` (raw HTML disabled) and `rehype-highlight`.
