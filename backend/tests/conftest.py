"""CI conftest: stubs heavy ML deps and sets SQLite DATABASE_URL."""
import os
import sys
import tempfile
from types import ModuleType
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# --- SQLite test database ---
_TEST_DB_FILE = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_TEST_DB_FILE.close()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_TEST_DB_FILE.name}")
os.environ.setdefault("JWT_SECRET", "ci-test-secret")
os.environ.setdefault("ENVIRONMENT", "test")

# --- Stub torch and transformers so imports don’t fail in CI ---
for _mod_name in [
    "torch",
    "torch.nn",
    "torch.optim",
    "transformers",
    "transformers.pipelines",
    "transformers.models",
]:
    if _mod_name not in sys.modules:
        _stub = ModuleType(_mod_name)
        _stub.__spec__ = None  # type: ignore[attr-defined]
        sys.modules[_mod_name] = _stub

# Make torch.Tensor, torch.load etc accessible as MagicMock attributes
sys.modules["torch"].Tensor = MagicMock()  # type: ignore[attr-defined]
sys.modules["torch"].load = MagicMock()    # type: ignore[attr-defined]
sys.modules["torch"].save = MagicMock()    # type: ignore[attr-defined]
sys.modules["transformers"].pipeline = MagicMock()  # type: ignore[attr-defined]
sys.modules["transformers"].AutoTokenizer = MagicMock()  # type: ignore[attr-defined]
sys.modules["transformers"].AutoModelForSequenceClassification = MagicMock()  # type: ignore[attr-defined]

@pytest.fixture()
def client():
    """Provide a TestClient wired to a fresh in-memory SQLite DB."""
    from app.db.session import Base, get_db
    from app.main import app

    engine_test = create_engine(
        os.environ["DATABASE_URL"],
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)
    Base.metadata.create_all(bind=engine_test)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine_test)

