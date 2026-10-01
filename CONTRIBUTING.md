# Contributing

## Setup

```bash
make install
make seed
make dev-backend   # terminal 1
make dev-frontend  # terminal 2
```

## Before opening a pull request

```bash
make lint
make test
```

- Backend code is linted and formatted with **ruff** (`make format` fixes most issues).
- Frontend code is type-checked with **TypeScript** and formatted with **prettier**.
- Add or update tests for behaviour you change: `backend/tests/` (pytest) and `frontend/src/test/` (Vitest + Testing Library).
- Database changes must work on SQLite and Oracle. Run `make test-oracle` with the Oracle container from `docker compose up oracle`.

## Commit messages

Use the imperative mood and keep the first line under about 72 characters, e.g. `Add tag suggestions to the ask page`.
