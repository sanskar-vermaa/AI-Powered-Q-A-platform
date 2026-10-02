import pytest

from app.database import normalize_database_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("postgres://u:p@host:5432/db", "postgresql+psycopg2://u:p@host:5432/db"),
        ("postgresql://u:p@host/db", "postgresql+psycopg2://u:p@host/db"),
        ("postgresql+psycopg2://u:p@host/db", "postgresql+psycopg2://u:p@host/db"),
        ("sqlite:///./qa.db", "sqlite:///./qa.db"),
        (
            "oracle+oracledb://qa:pw@db:1521/?service_name=FREEPDB1",
            "oracle+oracledb://qa:pw@db:1521/?service_name=FREEPDB1",
        ),
    ],
)
def test_normalize_database_url(raw, expected):
    assert normalize_database_url(raw) == expected
