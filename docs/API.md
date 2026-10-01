# API reference

All endpoints are under `/api`. Interactive OpenAPI docs are served at `/docs` (Swagger UI) and `/redoc`.

Authenticated endpoints need `Authorization: Bearer <token>` from `POST /api/auth/login`. Errors use FastAPI's format: `{"detail": "message"}`, or a list of field errors for `422`.

## Auth
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/auth/register` | – | Create an account (the first account becomes admin) |
| POST | `/auth/login` | – | `{username, password}` → `{access_token}`. Username or email accepted |
| GET | `/auth/me` | user | Current user, including email |
| POST | `/auth/change-password` | user | `{current_password, new_password}` |

## Questions
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/questions` | – | Paginated list. Query: `page`, `page_size`, `sort` (`newest`/`active`/`votes`/`views`/`unanswered`), `tag`, `q`, `author` |
| POST | `/questions` | user | `{title, body, tags[]}` |
| GET | `/questions/{id}` | – | Detail; increments views unless `count_view=false` |
| PATCH | `/questions/{id}` | owner/staff | Partial update |
| DELETE | `/questions/{id}` | owner/staff | Deletes the question with its answers and comments |
| POST | `/questions/{id}/accept/{answer_id}` | owner | Accept an answer (call again to unaccept) |
| GET | `/questions/similar?title=&body=` | – | Possible duplicates for a draft |
| GET | `/questions/{id}/related` | – | Related questions |
| POST | `/questions/{id}/vote` | user | `{value: 1 | 0 | -1}` → `{score, my_vote}` |
| PUT/DELETE | `/questions/{id}/bookmark` | user | Add or remove a bookmark |

## Answers and comments
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/questions/{id}/answers` | – | Accepted answer first, then by score |
| POST | `/questions/{id}/answers` | user | `{body}` |
| GET/PATCH/DELETE | `/answers/{id}` | owner/staff | AI answers can be edited by staff; the asker may delete them |
| POST | `/answers/{id}/vote` | user | Same as question votes |
| GET/POST | `/questions/{id}/comments`, `/answers/{id}/comments` | –/user | List or add comments |
| DELETE | `/comments/{id}` | owner/staff | |

## AI
All AI endpoints need a logged-in user and are rate limited per user (20 requests/minute). Provider failures return `502`.

| Method | Path | Description |
| --- | --- | --- |
| GET | `/ai/status` | `{provider, live}` |
| POST | `/ai/questions/{id}/answer` | Post an AI answer (one per question, else `409`) |
| POST | `/ai/suggest-tags` | `{title, body}` → `{tags[]}` |
| POST | `/ai/improve-question` | `{title, body}` → `{title, body, tips[]}` |
| POST | `/ai/questions/{id}/summary` | `{summary}` (Markdown) |
| POST | `/chat` | `{message, conversation_id?}` → `{conversation_id, reply}` |
| POST | `/chat/stream` | Same input; responds with SSE events `start`, `delta`, `done` / `error` |
| GET | `/chat/conversations` | The user's conversations |
| GET/DELETE | `/chat/conversations/{id}` | Conversation with messages, or delete it |

## Users, tags and stats
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| GET | `/users?q=` | – | Users by reputation |
| GET | `/users/{username}` | – | Profile with counts and badges |
| GET | `/users/{username}/answers` | – | Recent answers |
| PATCH | `/users/me` | user | `{bio?, email?}` |
| GET | `/me/bookmarks` | user | Bookmarked questions |
| GET | `/tags?q=&sort=popular|name` | – | Tags with question counts |
| GET | `/tags/{name}` | – | One tag |
| PATCH | `/tags/{name}` | staff | `{description}` |
| GET | `/stats` | – | Site totals |
| GET | `/stats/leaderboard?limit=` | – | Top users |

## Notifications
| Method | Path | Description |
| --- | --- | --- |
| GET | `/notifications?unread_only=` | Newest first |
| GET | `/notifications/unread-count` | `{unread}` |
| POST | `/notifications/{id}/read` | Mark one as read |
| POST | `/notifications/read-all` | Mark all as read |

## Moderation and admin
| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| POST | `/flags` | user | `{target_type, target_id, reason, details?}` |
| GET | `/moderation/flags?status=` | staff | `open` (default), `resolved`, `dismissed` or `all` |
| POST | `/moderation/flags/{id}` | staff | `{status: resolved|dismissed, delete_content?}` |
| PATCH | `/admin/users/{id}` | admin | `{role?, is_active?}` |

## Example

```bash
TOKEN=$(curl -s localhost:8000/api/auth/login -H 'Content-Type: application/json' \
  -d '{"username":"marcus","password":"demo12345"}' | jq -r .access_token)

curl -s localhost:8000/api/questions -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"title":"How do I reverse a list in Python?","body":"I need the items of a list in reverse order.","tags":["python"]}'

curl -N localhost:8000/api/chat/stream -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"message":"Explain Python generators"}'
```
