from app.utils.text import excerpt, jaccard, normalize_tag, normalize_tags, tokenize


def test_normalize_tag_lowercases_and_hyphenates():
    assert normalize_tag("  Machine Learning ") == "machine-learning"


def test_normalize_tag_keeps_language_symbols():
    assert normalize_tag("C++") == "c++"
    assert normalize_tag("C#") == "c#"
    assert normalize_tag("Node.js") == "node.js"


def test_normalize_tag_strips_invalid_characters():
    assert normalize_tag("py$th@on!") == "python"
    assert normalize_tag("---") == ""


def test_normalize_tags_dedupes_and_limits():
    assert normalize_tags(["Python", "python", "SQL", "", "a", "b", "c", "d"]) == ["python", "sql", "a", "b", "c"]


def test_tokenize_drops_stopwords():
    assert tokenize("How do I sort a list in Python?") == {"sort", "list", "python"}


def test_jaccard():
    assert jaccard({"a", "b"}, {"b", "c"}) == 1 / 3
    assert jaccard(set(), {"a"}) == 0.0


def test_excerpt_truncates_and_flattens_whitespace():
    assert excerpt("one\n\ntwo   three") == "one two three"
    long = "word " * 100
    result = excerpt(long, 20)
    assert len(result) <= 20
    assert result.endswith("…")
