# app/service/actuator_service.py
import json
import os
from datetime import datetime, timezone
from typing import List, Optional
from app.model.actuator import Actuator
from app.models.user import User

# Define rutas relativas
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
ACTUATORS_PATH = os.path.join(DATA_DIR, "actuators.json")

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

def _save_actuators(actuators_list: List[dict]):
    """Guarda la lista de actuadores en el archivo JSON."""
    data = {"actuators": actuators_list}
    with open(ACTUATORS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def toggleActuator(actuatorId: str, user: User) -> Optional[Actuator]:
    """
    Cambia el estado de un actuador (True/False).
    Retorna el actuador actualizado o None si no se encuentra.
    """
    data = _safe_read(ACTUATORS_PATH, {"actuators": []})
    actuators_list = data.get("actuators", [])
    
    for act_dict in actuators_list:
        if act_dict.get("_id") == actuatorId:
            # Toggle el estado
            act_dict["_state"] = not act_dict.get("_state", False)
            act_dict["_lastChangedAt"] = datetime.now(timezone.utc).isoformat()
            
            # Guardar cambios
            _save_actuators(actuators_list)
            
            # Retornar objeto Actuator
            actuator = Actuator(type=act_dict["_type"], state=act_dict["_state"])
            actuator._id = act_dict["_id"]
            actuator._lastChangedAt = datetime.fromisoformat(act_dict["_lastChangedAt"])
            return actuator
    
    return None

def getActuatorStates() -> List[Actuator]:
    """
    Retorna una lista con todos los actuadores y sus estados actuales.
    """
    data = _safe_read(ACTUATORS_PATH, {"actuators": []})
    actuators_list = data.get("actuators", [])
    
    result = []
    for act_dict in actuators_list:
        actuator = Actuator(type=act_dict["_type"], state=act_dict.get("_state", False))
        actuator._id = act_dict["_id"]
        actuator._lastChangedAt = datetime.fromisoformat(act_dict["_lastChangedAt"])
        result.append(actuator)
    
    return result