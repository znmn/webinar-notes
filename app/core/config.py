import os
from pathlib import Path


def _load_env_file() -> None:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if not env_path.exists():
        return

    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _get_env(name: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        raise ValueError(f"Environment variable '{name}' is required")
    return value


def _get_env_with_default(name: str, default: str) -> str:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    return value.strip()


_load_env_file()

DATABASE_URL = _get_env("DATABASE_URL")
SECRET = _get_env("SECRET")
ALGORITHM = _get_env("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_get_env("ACCESS_TOKEN_EXPIRE_MINUTES"))
LOG_LEVEL = _get_env_with_default("LOG_LEVEL", "INFO").upper()
ALLOWED_CATEGORY = ["work", "personal", "finance", "learning", "other"]
