# app/service/alert_service.py
from typing import List, Optional
from uuid import UUID
from app.model.alert import Alert
from app.model.sensor import Reading
from app.model.enums import SeverityEnum
from app.repository.alert_repository import AlertRepository

# Instancia del repositorio
alert_repo = AlertRepository()

def evaluate(reading: Reading) -> Optional[Alert]:
    """
    Evalúa una lectura de sensor y genera una alerta si se cumplen ciertas condiciones.
    
    Args:
        reading: Objeto Reading con los datos del sensor
        
    Returns:
        Alert si se generó una alerta, None en caso contrario
    """
    alert = None
    
    # Lógica de evaluación según el tipo de sensor
    sensor_type = getattr(reading, 'sensor_type', '').lower()
    value = getattr(reading, 'value', 0)
    sensor_id = getattr(reading, 'sensor_id', None)
    user_id = getattr(reading, 'user_id', None)
    
    if not user_id:
        return None
    
    # Temperatura
    if sensor_type == 'temperature':
        if value > 30:
            alert = Alert.new(
                type='high_temperature',
                severity=SeverityEnum.HIGH,
                message=f'Temperatura crítica detectada: {value}°C',
                target_user_id=user_id
            )
        elif value < 10:
            alert = Alert.new(
                type='low_temperature',
                severity=SeverityEnum.MEDIUM,
                message=f'Temperatura baja detectada: {value}°C',
                target_user_id=user_id
            )
    
    # Humedad
    elif sensor_type == 'humidity':
        if value > 80:
            alert = Alert.new(
                type='high_humidity',
                severity=SeverityEnum.MEDIUM,
                message=f'Humedad alta detectada: {value}%',
                target_user_id=user_id
            )
        elif value < 20:
            alert = Alert.new(
                type='low_humidity',
                severity=SeverityEnum.LOW,
                message=f'Humedad baja detectada: {value}%',
                target_user_id=user_id
            )
    
    # Calidad del aire
    elif sensor_type == 'air_quality':
        if value > 150:
            alert = Alert.new(
                type='poor_air_quality',
                severity=SeverityEnum.HIGH,
                message=f'Calidad del aire deficiente: {value} AQI',
                target_user_id=user_id
            )
    
    # Luminosidad
    elif sensor_type == 'light':
        if value < 100:
            alert = Alert.new(
                type='low_light',
                severity=SeverityEnum.LOW,
                message=f'Nivel de luz bajo: {value} lux',
                target_user_id=user_id
            )
    
    # Si se generó una alerta, guardarla en el repositorio
    if alert:
        alert_repo.add_alert(alert)
        alert_repo.save()
    
    return alert


def markRead(alertId: str, userId: str) -> None:
    """
    Marca una alerta como leída por un usuario específico.
    
    Args:
        alertId: ID de la alerta a marcar como leída
        userId: ID del usuario que lee la alerta
    """
    try:
        alert_uuid = UUID(alertId) if isinstance(alertId, str) else alertId
    except (ValueError, AttributeError):
        return
    
    alert = alert_repo.find_by_id(str(alert_uuid))
    
    if alert:
        # Verificar que el usuario es el destinatario de la alerta
        target_id = alert.target_user_id
        try:
            user_uuid = UUID(userId) if isinstance(userId, str) else userId
        except (ValueError, AttributeError):
            return
        
        if str(target_id) == str(user_uuid):
            alert.read_status = True
            alert_repo.save()


def getAlerts(userId: str) -> List[Alert]:
    """
    Obtiene todas las alertas de un usuario específico.
    
    Args:
        userId: ID del usuario
        
    Returns:
        Lista de alertas del usuario
    """
    try:
        user_uuid = UUID(userId) if isinstance(userId, str) else userId
    except (ValueError, AttributeError):
        return []
    
    all_alerts = alert_repo.get_all()
    
    # Filtrar alertas por usuario
    user_alerts = [
        alert for alert in all_alerts 
        if str(alert.target_user_id) == str(user_uuid)
    ]
    
    # Ordenar por timestamp (más recientes primero)
    user_alerts.sort(key=lambda x: x.timestamp, reverse=True)
    
    return user_alerts