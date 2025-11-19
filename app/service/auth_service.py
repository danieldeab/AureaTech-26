# app/models/auth_service.py
# this one should get deprecated
import json, os, time
from app.models.user import User

# Define rutas relativas
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_PATH = os.path.join(DATA_DIR, "usuarios.json")
LOGS_PATH  = os.path.join(DATA_DIR, "logs.json")

def _safe_read(path, default):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(default, f, ensure_ascii=False, indent=2)
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default

def read_users():
    """Devuelve dict con todos los usuarios."""
    return _safe_read(USERS_PATH, {"usuarios": []})

def save_user(u: User):
    """Guarda un usuario si no existe."""
    data = read_users()
    if not any(x["email"] == u.email for x in data["usuarios"]):
        data["usuarios"].append(u.to_dict())
        with open(USERS_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

def write_log(evento, email, rol):
    """Registra eventos de login/logout."""
    data = _safe_read(LOGS_PATH, {"eventos": []})
    data["eventos"].append({
        "ts": int(time.time()),
        "evento": evento,
        "email": email,
        "rol": rol
    })
    with open(LOGS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
