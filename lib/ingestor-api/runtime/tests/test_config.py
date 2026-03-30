def test_jwks_url_empty_string_treated_as_none(test_environ, monkeypatch):
    """Settings should accept JWKS_URL='' and treat it as None (auth disabled).

    Regression test: Pydantic v2 rejects empty strings for AnyHttpUrl fields,
    so an empty JWKS_URL must be coerced to None before validation.
    """
    monkeypatch.setenv("JWKS_URL", "")
    monkeypatch.setenv("NO_PYDANTIC_SSM_SETTINGS", "1")

    from src.config import Settings

    settings = Settings()
    assert settings.jwks_url is None
