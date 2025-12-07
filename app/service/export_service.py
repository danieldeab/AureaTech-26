# app/service/export_service.py
import csv
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from io import StringIO, BytesIO
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository

# Instancias de repositorios
log_repo = LogRepository()
reading_repo = ReadingRepository()

# Directorio para exportaciones temporales
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


def exportLogs(range: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
    """
    Exporta logs en el formato especificado (JSON o CSV).
    
    Args:
        range: Diccionario con criterios de filtrado:
            - start_date: fecha inicio (timestamp o ISO string)
            - end_date: fecha fin (timestamp o ISO string)
            - user_id: ID del usuario
            - event_type: tipo de evento
        format: Formato de exportación ("json" o "csv")
        
    Returns:
        Ruta del archivo generado
    """
    # Obtener todos los logs
    all_logs = log_repo.all()
    
    # Aplicar filtros si se proporciona un rango
    filtered_logs = _filter_logs(all_logs, range)
    
    # Ordenar por timestamp
    filtered_logs.sort(key=lambda x: x.get("ts", 0), reverse=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "csv":
        filename = f"logs_export_{timestamp}.csv"
        filepath = os.path.join(EXPORT_DIR, filename)
        _export_logs_to_csv(filtered_logs, filepath)
    else:  # JSON por defecto
        filename = f"logs_export_{timestamp}.json"
        filepath = os.path.join(EXPORT_DIR, filename)
        _export_logs_to_json(filtered_logs, filepath)
    
    return filepath


def exportReadings(range: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
    """
    Exporta lecturas de sensores en el formato especificado (JSON o CSV).
    
    Args:
        range: Diccionario con criterios de filtrado:
            - start_date: fecha inicio (timestamp o ISO string)
            - end_date: fecha fin (timestamp o ISO string)
            - sensor_id: ID del sensor
            - user_id: ID del usuario
        format: Formato de exportación ("json" o "csv")
        
    Returns:
        Ruta del archivo generado
    """
    # Obtener todas las lecturas
    sensor_id = range.get("sensor_id") if range else None
    
    if sensor_id:
        # Si se especifica un sensor, obtener sus lecturas
        sensor_data = reading_repo.findById(sensor_id)
        all_readings = []
        
        if sensor_data and hasattr(sensor_data, 'readings'):
            for reading in sensor_data.readings:
                reading_dict = {
                    "sensor_id": str(sensor_id),
                    "timestamp": reading.timestamp.isoformat() if hasattr(reading, 'timestamp') else "",
                    "value": getattr(reading, 'value', None),
                    "unit": getattr(reading, 'unit', ""),
                    "type": getattr(sensor_data, 'type', "")
                }
                all_readings.append(reading_dict)
    else:
        # Obtener todas las lecturas de todos los sensores
        all_readings = _get_all_readings()
    
    # Aplicar filtros si se proporciona un rango
    filtered_readings = _filter_readings(all_readings, range)
    
    # Ordenar por timestamp
    filtered_readings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format.lower() == "csv":
        filename = f"readings_export_{timestamp}.csv"
        filepath = os.path.join(EXPORT_DIR, filename)
        _export_readings_to_csv(filtered_readings, filepath)
    else:  # JSON por defecto
        filename = f"readings_export_{timestamp}.json"
        filepath = os.path.join(EXPORT_DIR, filename)
        _export_readings_to_json(filtered_readings, filepath)
    
    return filepath


def _filter_logs(logs: list, range: Optional[Dict[str, Any]]) -> list:
    """Filtra logs según el rango especificado."""
    if not range:
        return logs
    
    filtered = []
    start_ts = _parse_timestamp(range.get("start_date"))
    end_ts = _parse_timestamp(range.get("end_date"))
    user_id = range.get("user_id")
    event_type = range.get("event_type")
    
    for log in logs:
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
        
        filtered.append(log)
    
    return filtered


def _filter_readings(readings: list, range: Optional[Dict[str, Any]]) -> list:
    """Filtra lecturas según el rango especificado."""
    if not range:
        return readings
    
    filtered = []
    start_date = range.get("start_date")
    end_date = range.get("end_date")
    user_id = range.get("user_id")
    
    # Convertir fechas a formato comparable
    if start_date:
        if isinstance(start_date, str):
            try:
                start_date = datetime.fromisoformat(start_date)
            except:
                start_date = None
    
    if end_date:
        if isinstance(end_date, str):
            try:
                end_date = datetime.fromisoformat(end_date)
            except:
                end_date = None
    
    for reading in readings:
        timestamp_str = reading.get("timestamp", "")
        
        try:
            reading_time = datetime.fromisoformat(timestamp_str)
            
            # Filtro por fecha
            if start_date and reading_time < start_date:
                continue
            if end_date and reading_time > end_date:
                continue
        except:
            pass
        
        # Filtro por usuario (si está disponible en la lectura)
        if user_id and reading.get("user_id") != str(user_id):
            continue
        
        filtered.append(reading)
    
    return filtered


def _parse_timestamp(value: Any) -> Optional[int]:
    """Convierte un valor a timestamp Unix."""
    if not value:
        return None
    
    if isinstance(value, int):
        return value
    
    if isinstance(value, str):
        try:
            # Intentar parsear como ISO string
            dt = datetime.fromisoformat(value)
            return int(dt.timestamp())
        except:
            try:
                # Intentar parsear como timestamp string
                return int(value)
            except:
                return None
    
    return None


def _export_logs_to_json(logs: list, filepath: str):
    """Exporta logs a formato JSON."""
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_records": len(logs),
        "logs": logs
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def _export_logs_to_csv(logs: list, filepath: str):
    """Exporta logs a formato CSV."""
    if not logs:
        # Crear archivo vacío con headers
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "timestamp", "event_type", "user_id", "description"])
        return
    
    # Obtener todas las claves posibles
    fieldnames = set()
    for log in logs:
        fieldnames.update(log.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for log in logs:
            # Convertir timestamp a fecha legible
            row = log.copy()
            if "ts" in row:
                row["timestamp_readable"] = datetime.fromtimestamp(row["ts"]).isoformat()
            writer.writerow(row)


def _export_readings_to_json(readings: list, filepath: str):
    """Exporta lecturas a formato JSON."""
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_records": len(readings),
        "readings": readings
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def _export_readings_to_csv(readings: list, filepath: str):
    """Exporta lecturas a formato CSV."""
    if not readings:
        # Crear archivo vacío con headers
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["sensor_id", "timestamp", "value", "unit", "type"])
        return
    
    # Obtener todas las claves posibles
    fieldnames = set()
    for reading in readings:
        fieldnames.update(reading.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    with open(filepath, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(readings)


def _get_all_readings() -> list:
    """Obtiene todas las lecturas de todos los sensores."""
    all_readings = []
    
    try:
        # Intentar obtener todos los sensores
        all_sensors = reading_repo.findAll()
        
        for sensor in all_sensors:
            sensor_id = getattr(sensor, 'id', None)
            sensor_type = getattr(sensor, 'type', 'unknown')
            
            if hasattr(sensor, 'readings'):
                for reading in sensor.readings:
                    reading_dict = {
                        "sensor_id": str(sensor_id),
                        "timestamp": reading.timestamp.isoformat() if hasattr(reading, 'timestamp') else "",
                        "value": getattr(reading, 'value', None),
                        "unit": getattr(reading, 'unit', ""),
                        "type": sensor_type
                    }
                    all_readings.append(reading_dict)
    except Exception as e:
        print(f"Error obteniendo lecturas: {e}")
    
    return all_readings