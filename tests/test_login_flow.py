import json, os, sys, pytest
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.models.auth_service import read_users, save_user, _safe_read, LOGS_PATH
from app.models.auth import UserRepository, AuthController
from app.model.user import User as Usuario
from app.utils.session import Session

DATA_PATH = os.path.join("app", "data", "usuarios.json")

def setup_module(module):
    """Reset JSON before testing."""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump({"usuarios": []}, f)

def test_register_user():
    user = Usuario("demo@test.com", "1234", "vecino")
    save_user(user)
    data = read_users()
    assert any(u["email"] == "demo@test.com" for u in data["usuarios"])

def test_login_valid():
    repo = UserRepository()
    session = Session()
    auth = AuthController(repo, session)
    ok, msg = auth.login("demo@test.com", "1234")
    assert ok

def test_login_invalid():
    repo = UserRepository()
    session = Session()
    auth = AuthController(repo, session)
    ok, msg = auth.login("demo@test.com", "wrong")
    assert not ok

def test_log_file_created():
    log_path = os.path.join("app", "data", "logs.json")
    assert os.path.exists(log_path)

def test_end_to_end_flow(tmp_path):
    """Simulates full register→login→log entry cycle."""
    user = Usuario("e2e@test.com", "9999", "tecnico")
    save_user(user)
    repo = UserRepository()
    session = Session()
    auth = AuthController(repo, session)
    ok, msg = auth.login("e2e@test.com", "9999")
    assert ok
    logs = _safe_read(LOGS_PATH, {"eventos": []})["eventos"]
    assert any(ev["email"] == "e2e@test.com" for ev in logs)