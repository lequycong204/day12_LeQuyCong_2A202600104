from src.auth import create_access_token, decode_token, verify_password


def test_password_verification() -> None:
    assert verify_password("admin123", "admin123") is True
    assert verify_password("admin123", "wrong") is False


def test_jwt_roundtrip() -> None:
    token = create_access_token({"sub": "admin", "role": "admin"}, "secret", 30)
    claims = decode_token(token, "secret")
    assert claims["sub"] == "admin"
    assert claims["role"] == "admin"
