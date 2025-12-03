# app/service/user_service.py
import json
import os
from typing import Optional, Dict, Any
from app.models.user import User, RoleEnum
from uuid import UUID

# Define rutas relativas
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
USERS_PATH = os.path.join(DATA_DIR, "usuarios.json")

def _safe_read(path, default):
    """Lee archivo JSON de forma segura, creándolo si no existe."""
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

def _save_users(users_list: list):
    """Guarda la lista de usuarios en el archivo JSON."""
    data = {"usuarios": users_list}
    with open(USERS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _dict_to_user(user_dict: dict) -> User:
    """Convierte un diccionario en objeto User."""
    user = User(
        name=user_dict["name"],
        email=user_dict["email"],
        password=user_dict["password_hash"],  # Asumiendo que User acepta password
        role=RoleEnum[user_dict["role"]] if isinstance(user_dict["role"], str) else user_dict["role"]
    )
    user.id = UUID(user_dict["id"]) if isinstance(user_dict["id"], str) else user_dict["id"]
    user.password_hash = user_dict["password_hash"]
    user.picture_path = user_dict.get("picture_path")
    user.picture_url = user_dict.get("picture_url")
    return user

def changeRole(userId: str, newRole: RoleEnum, adminId: str) -> Optional[User]:
    """
    Cambia el rol de un usuario.
    
    Args:
        userId: ID del usuario a modificar
        newRole: Nuevo rol a asignar
        adminId: ID del administrador que realiza el cambio
        
    Returns:
        Usuario actualizado o None si no se encuentra
    """
    data = _safe_read(USERS_PATH, {"usuarios": []})
    users_list = data.get("usuarios", [])
    
    # Verificar que el admin existe y tiene permisos (opcional)
    admin_exists = any(u.get("id") == adminId for u in users_list)
    if not admin_exists:
        return None
    
    # Buscar y actualizar el usuario
    for user_dict in users_list:
        if user_dict.get("id") == userId:
            # Actualizar rol
            user_dict["role"] = newRole.name if isinstance(newRole, RoleEnum) else newRole
            
            # Guardar cambios
            _save_users(users_list)
            
            # Retornar objeto User actualizado
            return _dict_to_user(user_dict)
    
    return None

def updateProfile(userId: str, patch: Dict[str, Any]) -> Optional[User]:
    """
    Actualiza el perfil de un usuario con los campos proporcionados en patch.
    
    Args:
        userId: ID del usuario a actualizar
        patch: Diccionario con los campos a actualizar (name, picture_path, picture_url, etc.)
        
    Returns:
        Usuario actualizado o None si no se encuentra
    """
    data = _safe_read(USERS_PATH, {"usuarios": []})
    users_list = data.get("usuarios", [])
    
    for user_dict in users_list:
        if user_dict.get("id") == userId:
            # Actualizar solo los campos proporcionados en patch
            allowed_fields = ["name", "picture_path", "picture_url", "email"]
            
            for key, value in patch.items():
                if key in allowed_fields:
                    user_dict[key] = value
            
            # Guardar cambios
            _save_users(users_list)
            
            # Retornar objeto User actualizado
            return _dict_to_user(user_dict)
    
    return None