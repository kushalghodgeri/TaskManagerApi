from app.api.deps import get_db as api_get_db
from app.core.config import Settings
from app.core.security import decode_access_token
from app.db.session import get_db as session_get_db


def test_cors_origins_parsing():
    """Test CORS_ORIGINS parser handling string, JSON array, and list inputs."""
    # Comma-separated string
    s1 = Settings(CORS_ORIGINS="http://localhost:3000, http://example.com")
    assert s1.CORS_ORIGINS == ["http://localhost:3000", "http://example.com"]

    # JSON array string
    s2 = Settings(CORS_ORIGINS='["http://localhost:8080", "https://app.test"]')
    assert s2.CORS_ORIGINS == ["http://localhost:8080", "https://app.test"]

    # Invalid JSON string fallback
    s3 = Settings(CORS_ORIGINS="[invalid-json")
    assert s3.CORS_ORIGINS == ["[invalid-json"]

    # Direct list
    s4 = Settings(CORS_ORIGINS=["http://site1.com", "http://site2.com"])
    assert s4.CORS_ORIGINS == ["http://site1.com", "http://site2.com"]

    # Other non-string, non-list type fallback
    s5 = Settings.assemble_cors_origins(12345)
    assert s5 == ["http://localhost:5173"]


def test_get_db_generators():
    """Test get_db session generator in db.session and api.deps."""
    # Test session_get_db generator
    gen1 = session_get_db()
    db1 = next(gen1)
    assert db1 is not None
    try:
        next(gen1)
    except StopIteration:
        pass

    # Test api_get_db generator
    gen2 = api_get_db()
    db2 = next(gen2)
    assert db2 is not None
    try:
        next(gen2)
    except StopIteration:
        pass


def test_decode_invalid_jwt():
    """Test decode_access_token returns None for completely invalid token."""
    res = decode_access_token("not.a.valid.jwt.string")
    assert res is None
