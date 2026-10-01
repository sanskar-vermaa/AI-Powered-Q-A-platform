"""Populate the database with demo content.

Usage: python -m app.seed [--reset]
"""

import argparse

from sqlalchemy import func, select

from app.database import Base, SessionLocal, engine, init_db
from app.models import Answer, Comment, Question, Tag, User
from app.security import hash_password
from app.services import badges
from app.services.tags import get_or_create_tags

DEMO_PASSWORD = "demo12345"

USERS = [
    ("admin", "admin", "Site administrator."),
    ("priya", "moderator", "Backend engineer. Python, PostgreSQL and distributed systems."),
    ("marcus", "user", "Frontend developer who loves TypeScript and React."),
    ("lena", "user", "Data scientist working with pandas and scikit-learn."),
    ("diego", "user", "DevOps engineer: Docker, Kubernetes, CI/CD."),
]

TAG_DESCRIPTIONS = {
    "python": "A high-level, general-purpose programming language.",
    "javascript": "The programming language of the web.",
    "typescript": "A typed superset of JavaScript that compiles to plain JavaScript.",
    "react": "A JavaScript library for building user interfaces.",
    "docker": "A platform for packaging applications into containers.",
    "sql": "Structured Query Language for relational databases.",
    "fastapi": "A modern, fast web framework for building APIs with Python.",
    "pandas": "A Python library for data analysis and manipulation.",
}

QUESTIONS = [
    {
        "author": "marcus",
        "title": "How do I type the props of a React component that forwards a ref?",
        "body": "I'm using `forwardRef` with TypeScript and I can't get the generic types right.\n\n"
        "```tsx\nconst Input = forwardRef((props, ref) => <input ref={ref} {...props} />);\n```\n\n"
        "TypeScript says `props` is implicitly `any`. What is the correct way to type this?",
        "tags": ["react", "typescript"],
        "answers": [
            (
                "priya",
                "Pass the ref type and the props type as generics to `forwardRef`:\n\n"
                "```tsx\ntype InputProps = React.InputHTMLAttributes<HTMLInputElement>;\n\n"
                "const Input = forwardRef<HTMLInputElement, InputProps>((props, ref) => (\n"
                "  <input ref={ref} {...props} />\n));\n```\n\n"
                "Note the order: the ref type comes first, then the props.",
            )
        ],
        "accept": 0,
        "comments": [("lena", "Note that in React 19 you can accept `ref` as a regular prop instead.")],
    },
    {
        "author": "lena",
        "title": "Why does pandas raise SettingWithCopyWarning when I filter and assign?",
        "body": "This line triggers a `SettingWithCopyWarning`:\n\n"
        "```python\ndf[df['age'] > 30]['group'] = 'senior'\n```\n\nThe column is not updated either. Why?",
        "tags": ["python", "pandas"],
        "answers": [
            (
                "priya",
                "Chained indexing creates a temporary copy, so the assignment is applied to that copy. "
                "Use a single `.loc` call:\n\n```python\ndf.loc[df['age'] > 30, 'group'] = 'senior'\n```",
            )
        ],
        "accept": 0,
        "comments": [],
    },
    {
        "author": "diego",
        "title": "How can I make my Docker image for a Python app smaller?",
        "body": "My image based on `python:3.12` is over 1 GB. What are the best practices to reduce the size?",
        "tags": ["docker", "python"],
        "answers": [
            (
                "marcus",
                "A few things that usually help the most:\n\n"
                "1. Use `python:3.12-slim` as the base image.\n"
                "2. Use a multi-stage build so build tools don't end up in the final image.\n"
                "3. Install dependencies with `pip install --no-cache-dir`.\n"
                "4. Add a `.dockerignore` for `.git`, virtualenvs and caches.",
            )
        ],
        "accept": None,
        "comments": [],
    },
    {
        "author": "priya",
        "title": "What is the difference between async and sync path operations in FastAPI?",
        "body": "When should I declare my endpoint with `async def` and when with plain `def`? "
        "Does it affect performance?",
        "tags": ["python", "fastapi"],
        "answers": [],
        "accept": None,
        "comments": [("diego", "Are you calling a blocking database driver inside the endpoint?")],
    },
    {
        "author": "marcus",
        "title": "How do I find duplicate rows in a SQL table?",
        "body": "I have a `users` table and I suspect some emails were inserted twice. "
        "How can I list the duplicated emails and how many times each appears?",
        "tags": ["sql"],
        "answers": [
            (
                "lena",
                "Group by the column and keep the groups with more than one row:\n\n"
                "```sql\nSELECT email, COUNT(*) AS occurrences\nFROM users\nGROUP BY email\n"
                "HAVING COUNT(*) > 1\nORDER BY occurrences DESC;\n```",
            )
        ],
        "accept": 0,
        "comments": [],
    },
]


def reset_database() -> None:
    import app.models  # noqa: F401

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def seed() -> bool:
    """Insert demo content. Returns False if the database already has users."""
    init_db()
    with SessionLocal() as db:
        if db.scalar(select(func.count(User.id))):
            return False

        users = {}
        for username, role, bio in USERS:
            user = User(
                username=username,
                email=f"{username}@example.com",
                hashed_password=hash_password(DEMO_PASSWORD),
                role=role,
                bio=bio,
                reputation=1,
            )
            db.add(user)
            users[username] = user
        db.flush()

        for spec in QUESTIONS:
            question = Question(title=spec["title"], body=spec["body"], author_id=users[spec["author"]].id)
            question.tags = get_or_create_tags(db, spec["tags"])
            db.add(question)
            db.flush()
            answers = []
            for author, body in spec["answers"]:
                answer = Answer(body=body, question_id=question.id, author_id=users[author].id, score=2)
                users[author].reputation += 20
                db.add(answer)
                answers.append(answer)
            db.flush()
            if spec["accept"] is not None:
                accepted = answers[spec["accept"]]
                question.accepted_answer_id = accepted.id
                accepted.author.reputation += 15
            for author, body in spec["comments"]:
                db.add(Comment(body=body, author_id=users[author].id, question_id=question.id))
            question.score = len(spec["answers"]) + 1
            users[spec["author"]].reputation += 5 * question.score

        for tag in db.scalars(select(Tag)):
            tag.description = TAG_DESCRIPTIONS.get(tag.name, "")
        for user in users.values():
            badges.evaluate(db, user)
        db.commit()
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reset", action="store_true", help="drop and recreate all tables first")
    args = parser.parse_args()
    if args.reset:
        reset_database()
    if seed():
        print(f"Seeded demo data. Log in as any of {[u for u, *_ in USERS]} with password '{DEMO_PASSWORD}'.")
    else:
        print("Database already contains users; skipping. Use --reset to start over.")


if __name__ == "__main__":
    main()
