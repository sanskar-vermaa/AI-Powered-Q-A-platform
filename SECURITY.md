# Security policy

## Reporting a vulnerability

Please report vulnerabilities privately through GitHub's **Security → Report a vulnerability** form for this repository rather than opening a public issue. Include steps to reproduce and the impact. You should receive a response within a few days.

## Security measures in this project

- Passwords hashed with bcrypt; JWT access tokens with expiry
- Role-based authorization checks on every write endpoint
- Suspended accounts are rejected even with a valid token
- User Markdown is rendered without raw HTML, and links get `rel="noopener noreferrer nofollow"`
- The login redirect only accepts same-site relative paths (no open redirects)
- The static file server refuses paths outside the frontend build directory
- Per-user rate limiting on AI endpoints
- The Docker image runs as a non-root user
