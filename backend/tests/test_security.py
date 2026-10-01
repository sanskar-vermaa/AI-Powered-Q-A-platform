from app.security import create_access_token, decode_access_token, hash_password, verify_password


def test_hash_and_verify_password():
    hashed = hash_password("hunter2abc")
    assert hashed != "hunter2abc"
    assert verify_password("hunter2abc", hashed)
    assert not verify_password("wrong", hashed)


def test_verify_password_with_malformed_hash():
    assert not verify_password("anything", "not-a-bcrypt-hash")


def test_token_round_trip():
    token = create_access_token(42)
    assert decode_access_token(token) == "42"


def test_expired_token_is_rejected():
    token = create_access_token(1, expires_minutes=-1)
    assert decode_access_token(token) is None


def test_tampered_token_is_rejected():
    token = create_access_token(1)
    assert decode_access_token(token[:-2] + "xx") is None
