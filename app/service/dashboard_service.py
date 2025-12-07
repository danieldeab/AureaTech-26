# app/service/dashboard_service.py
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.user import User
from app.repository.log_repository import LogRepository
from app.repository.alert_repository import AlertRepository
from app.repository.sensor_repository import SensorRepository
from app.service.actuator_service import getActuatorStates

# Instancias de repositorios
log_repo = LogRepository()
alert_repo = AlertRepository()

class DashboardDTO:
    """Data Transfer Object para el resumen del dashboard."""
    
    def __init__(self):
        self.user_info: Dict[str, Any] = {}
        self.sensors_summary: Dict[str, Any] = {}
        self.actuators_summary: Dict[str, Any] = {}
        self.alerts_summary: Dict[str, Any] = {}
        self.recent_logs: List[Dict] = []
        self.statistics: Dict[str, Any] = {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el DTO a diccionario."""
        return {
            "user_info": self.user_info,
            "sensors_summary": self.sensors_summary,
            "actuators_summary": self.actuators_summary,
            "alerts_summary": self.alerts_summary,
            "recent_logs": self.recent_logs,
            "statistics": self.statistics
        }


class LogEntry:
    """Representa una entrada de log."""
    
    def __init__(self, id: str, ts: int, event_type: str, user_id: str = None, 
                 description: str = "", metadata: Dict = None):
        self.id = id
        self.ts = ts
        self.event_type = event_type
        self.user_id = user_id
        self.description = description
        self.metadata = metadata or {}
        self.timestamp_formatted = datetime.fromtimestamp(ts).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la entrada de log a diccionario."""
        return {
            "id": self.id,
            "ts": self.ts,
            "timestamp": self.timestamp_formatted,
            "event_type": self.event_type,
            "user_id": self.user_id,
            "description": self.description,
            "metadata": self.metadata
        }


def getDashboardSummary(user: User) -> DashboardDTO:
    """
    Genera un resumen completo del dashboard para un usuario específico.
    
    Args:
        user: Usuario para el cual generar el resumen
        
    Returns:
        DashboardDTO con toda la información del dashboard
    """
    dashboard = DashboardDTO()
    
    # 1. Información del usuario
    dashboard.user_info = {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role.value if hasattr(user.role, 'value') else str(user.role)
    }
    
    # 2. Resumen de sensores
    try:
        sensor_repo = SensorRepository()
        all_sensors = sensor_repo.findAll()
        
        # Filtrar sensores del usuario
        user_sensors = [s for s in all_sensors if str(s.user_id) == str(user.id)]
        
        # Obtener lecturas recientes
        recent_readings = []
        for sensor in user_sensors:
            readings = sensor_repo.findById(str(sensor.id))
            if readings and hasattr(readings, 'readings') and readings.readings:
                recent_readings.extend(readings.readings[-5:])  # Últimas 5 lecturas
        
        dashboard.sensors_summary = {
            "total_sensors": len(user_sensors),
            "active_sensors": len([s for s in user_sensors if getattr(s, 'is_active', True)]),
            "recent_readings_count": len(recent_readings),
            "sensor_types": list(set([s.type for s in user_sensors]))
        }
    except Exception as e:
        dashboard.sensors_summary = {
            "total_sensors": 0,
            "active_sensors": 0,
            "recent_readings_count": 0,
            "sensor_types": [],
            "error": str(e)
        }
    
    # 3. Resumen de actuadores
    try:
        actuators = getActuatorStates()
        active_actuators = [a for a in actuators if a._state]
        
        dashboard.actuators_summary = {
            "total_actuators": len(actuators),
            "active_actuators": len(active_actuators),
            "inactive_actuators": len(actuators) - len(active_actuators),
            "actuator_types": list(set([a._type for a in actuators]))
        }
    except Exception as e:
        dashboard.actuators_summary = {
            "total_actuators": 0,
            "active_actuators": 0,
            "inactive_actuators": 0,
            "actuator_types": [],
            "error": str(e)
        }
    
    # 4. Resumen de alertas
    try:
        all_alerts = alert_repo.get_all()
        user_alerts = [a for a in all_alerts if str(a.target_user_id) == str(user.id)]
        unread_alerts = [a for a in user_alerts if not a.read_status]
        
        # Contar por severidad
        severity_count = {}
        for alert in user_alerts:
            severity = alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity)
            severity_count[severity] = severity_count.get(severity, 0) + 1
        
        dashboard.alerts_summary = {
            "total_alerts": len(user_alerts),
            "unread_alerts": len(unread_alerts),
            "read_alerts": len(user_alerts) - len(unread_alerts),
            "by_severity": severity_count,
            "recent_alerts": [a.to_dict() for a in user_alerts[:5]]
        }
    except Exception as e:
        dashboard.alerts_summary = {
            "total_alerts": 0,
            "unread_alerts": 0,
            "read_alerts": 0,
            "by_severity": {},
            "recent_alerts": [],
            "error": str(e)
        }
    
    # 5. Logs recientes del usuario
    try:
        all_logs = log_repo.all()
        user_logs = [log for log in all_logs if log.get("user_id") == str(user.id)]
        user_logs.sort(key=lambda x: x.get("ts", 0), reverse=True)
        
        dashboard.recent_logs = user_logs[:10]  # Últimos 10 logs
    except Exception as e:
        dashboard.recent_logs = []
    
    # 6. Estadísticas generales
    dashboard.statistics = {
        "total_events": len(dashboard.recent_logs),
        "last_activity": datetime.now().isoformat(),
        "system_status": "operational"
    }
    
    return dashboard


def getLogs(range: Optional[Dict[str, Any]] = None) -> List[LogEntry]:
    """
    Obtiene logs filtrados por rango de tiempo o criterios específicos.
    
    Args:
        range: Diccionario con criterios de filtrado:
            - start_date: fecha inicio (timestamp o ISO string)
            - end_date: fecha fin (timestamp o ISO string)
            - user_id: ID del usuario
            - event_type: tipo de evento
            - limit: número máximo de resultados
            
    Returns:
        Lista de LogEntry filtrados
    """
    all_logs = log_repo.all()
    filtered_logs = []
    
    # Si no hay rango, devolver todos los logs
    if not range:
        range = {}
    
    # Obtener parámetros de filtrado
    start_date = range.get("start_date")
    end_date = range.get("end_date")
    user_id = range.get("user_id")
    event_type = range.get("event_type")
    limit = range.get("limit", 100)
    
    # Convertir fechas si es necesario
    start_ts = None
    end_ts = None
    
    if start_date:
        if isinstance(start_date, str):
            try:
                start_ts = int(datetime.fromisoformat(start_date).timestamp())
            except:
                # Si es un timestamp string
                start_ts = int(start_date)
        else:
            start_ts = int(start_date)
    
    if end_date:
        if isinstance(end_date, str):
            try:
                end_ts = int(datetime.fromisoformat(end_date).timestamp())
            except:
                end_ts = int(end_date)
        else:
            end_ts = int(end_date)
    
    # Filtrar logs
    for log in all_logs:
        log_ts = log.get("ts", 0)
        
        # Filtro por fecha
        if start_ts and log_ts < start_ts:
            continue
        if end_ts and log_ts > end_ts:
            continue
        
        # Filtro por usuario
        if user_id and log.get("user_id") != str(user_id):
            continue
        
        # Filtro por tipo de evento
        if event_type and log.get("event_type") != event_type:
            continue
        
        # Crear objeto LogEntry
        log_entry = LogEntry(
            id=log.get("id", ""),
            ts=log_ts,
            event_type=log.get("event_type", "unknown"),
            user_id=log.get("user_id"),
            description=log.get("description", ""),
            metadata=log.get("metadata", {})
        )
        
        filtered_logs.append(log_entry)
    
    # Ordenar por timestamp descendente (más recientes primero)
    filtered_logs.sort(key=lambda x: x.ts, reverse=True)
    
    # Aplicar límite
    return filtered_logs[:limit]