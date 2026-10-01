import time

from app.utils.rate_limit import RateLimiter


def test_allows_up_to_limit():
    limiter = RateLimiter(limit=3, window_seconds=60)
    assert [limiter.allow("k") for _ in range(4)] == [True, True, True, False]


def test_keys_are_independent():
    limiter = RateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("a")
    assert limiter.allow("b")
    assert not limiter.allow("a")


def test_window_expires():
    limiter = RateLimiter(limit=1, window_seconds=0.05)
    assert limiter.allow("k")
    assert not limiter.allow("k")
    time.sleep(0.06)
    assert limiter.allow("k")


def test_reset_clears_state():
    limiter = RateLimiter(limit=1, window_seconds=60)
    limiter.allow("k")
    limiter.reset()
    assert limiter.allow("k")
