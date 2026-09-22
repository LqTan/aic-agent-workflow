import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

# Force planner to local + demo engine so unit tests don't depend on dev
# .env vars (e.g. a real MiniMax key would otherwise trigger llm:* plans).
os.environ["KIS_DEMO_MODE"] = os.getenv("KIS_DEMO_MODE", "true")
os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "sqlite:///:memory:")
os.environ["KIS_LLM_API_KEY"] = ""
os.environ["KIS_LLM_ENDPOINT"] = ""
os.environ["KIS_LLM_MODEL"] = ""


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    from app.core.config import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
