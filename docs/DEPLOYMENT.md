# Deployment guide

The app ships as one Docker image that serves both the API and the React frontend on port 8000.

## Checklist

1. **Set a strong `SECRET_KEY`**: `python -c "import secrets; print(secrets.token_urlsafe(48))"`. The app logs a warning on startup while the development key is in use.
2. **Choose a database.** Use Oracle or PostgreSQL in production; SQLite suits a single small instance.
3. **Set `ANTHROPIC_API_KEY`** to enable real AI responses (otherwise the app runs in offline AI mode).
4. **Put the app behind HTTPS** (a load balancer or a reverse proxy such as Nginx or Caddy). The container runs uvicorn with `--proxy-headers`.
5. **Register the admin account first.** The first account created becomes the administrator.

## Oracle Database

```bash
docker compose up --build -d
```

This starts Oracle Database Free (`gvenzl/oracle-free`) with an application user, waits for its healthcheck, then starts the app with:

```
DATABASE_URL=oracle+oracledb://qa:qa_password@oracle:1521/?service_name=FREEPDB1
```

For an existing Oracle instance (on-premises, Oracle Cloud Autonomous Database, etc.), set `DATABASE_URL` to your connection string. The `python-oracledb` driver runs in thin mode, so no Oracle Client libraries are needed. Tables are created automatically on first start.

## PostgreSQL

```
DATABASE_URL=postgresql+psycopg2://user:password@host:5432/dbname
```

## Running without Docker

```bash
cd frontend && npm ci && npm run build
cd ../backend && pip install -r requirements.txt
FRONTEND_DIST=../frontend/dist uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Operations

- **Health check:** `GET /api/health` returns `{"status": "ok"}`; the Docker image has a built-in `HEALTHCHECK`.
- **Demo data:** `python -m app.seed` (add `--reset` to wipe and recreate all tables first, never in production).
- **Scaling:** the API is stateless apart from the AI rate limiter, which is per process. With several instances, put rate limiting at the gateway as well.
- **Backups:** back up the database volume (`oracle-data` in docker-compose).
