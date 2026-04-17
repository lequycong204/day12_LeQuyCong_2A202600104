import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent))
from src.config import load_config


def test_load_config_from_env(monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")
    monkeypatch.setenv("JWT_SECRET", "jwt-secret")
    config = load_config()

    assert config.openai_api_key == "sk-test"
    assert config.openai_model == "gpt-4o-mini"
    assert config.jwt_secret == "jwt-secret"
