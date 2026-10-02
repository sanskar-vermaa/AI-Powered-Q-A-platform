# Changelog

## 1.1.0

- Deploy to Vercel (static frontend + Python function, Neon Postgres) and Render (Blueprint with PostgreSQL)
- Accept `postgres://` database URLs handed out by hosting platforms
- Docker image binds to `$PORT` when the platform sets it
- Dependabot, issue templates and a pull request template

## 1.0.0

First release.

- Community Q&A: questions, answers, comments, votes, accepted answers, tags, search, bookmarks
- AI: AI-generated answers, question improvement, tag suggestions, thread summaries, streaming chat assistant, duplicate detection; offline mode without an API key
- Reputation, badges, notifications and leaderboard
- Moderation queue with flags, staff roles and account suspension
- React + TypeScript frontend with dark mode and responsive layout
- Oracle, PostgreSQL and SQLite support; Docker image and docker-compose with Oracle
- CI running backend tests on SQLite and Oracle, frontend tests, and a Docker smoke test
