import re

_TAG_RE = re.compile(r"[^a-z0-9+#.\-]")
_WORD_RE = re.compile(r"[a-z0-9+#]+")

STOPWORDS = frozenset(
    "a an and are as at be but by can do does for from how i if in is it my of on or "
    "so that the this to was what when where which while who why with you your".split()
)


def normalize_tag(raw: str) -> str:
    """Lowercase a tag and strip characters that are not allowed in tag names."""
    tag = raw.strip().lower().replace(" ", "-")
    tag = _TAG_RE.sub("", tag)
    return tag.strip("-.")[:35]


def normalize_tags(raw_tags: list[str], limit: int = 5) -> list[str]:
    seen: list[str] = []
    for raw in raw_tags:
        tag = normalize_tag(raw)
        if tag and tag not in seen:
            seen.append(tag)
    return seen[:limit]


def tokenize(text: str) -> set[str]:
    return {w for w in _WORD_RE.findall(text.lower()) if w not in STOPWORDS and len(w) > 1}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


_CODE_FENCE_RE = re.compile(r"```.*?(```|$)", re.DOTALL)
_MARKDOWN_RE = re.compile(r"[`*_#>~]|!?\[([^\]]*)\]\([^)]*\)")


def strip_markdown(text: str) -> str:
    """Reduce Markdown to plain text for previews: drop code blocks, keep link text."""
    text = _CODE_FENCE_RE.sub(" ", text)
    return _MARKDOWN_RE.sub(lambda m: m.group(1) or "", text)


def excerpt(text: str, length: int = 200) -> str:
    flat = " ".join(strip_markdown(text).split())
    if len(flat) <= length:
        return flat
    return flat[: length - 1].rstrip() + "…"
