# app/service/sensor_service.py
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID
from app.model.sensor import Sensor, Reading
from app.repository.reading_repository import ReadingRepository

# Instancia del repositorio
reading_repo = ReadingRepository()


def getSensorReadings(filters: Optional[Dict[str, Any]] = None) -> List[Reading]:
    """
    Obtiene lecturas de sensores aplicando filtros opcionales.
    
    Args:
        filters: Diccionario con criterios de filtrado:
            - sensor_id: ID del sensor (UUID o string)
            - start_date: fecha inicio (datetime o ISO string)
            - end_date: fecha fin (datetime o ISO string)
            - sensor_type: tipo de sensor
            - min_value: valor mínimo
            - max_value: valor máximo
            - limit: número máximo de resultados
            
    Returns:
        Lista de objetos Reading filtrados
    """
    if not filters:
        filters = {}
    
    sensor_id = filters.get("sensor_id")
    start_date = filters.get("start_date")
    end_date = filters.get("end_date")
    sensor_type = filters.get("sensor_type")
    min_value = filters.get("min_value")
    max_value = filters.get("max_value")
    limit = filters.get("limit", 1000)
    
    all_readings = []
    
    # Si se especifica un sensor_id, obtener solo sus lecturas
    if sensor_id:
        try:
            sensor_uuid = UUID(sensor_id) if isinstance(sensor_id, str) else sensor_id
            sensor_data = reading_repo.findById(str(sensor_uuid))
            
            if sensor_data and hasattr(sensor_data, 'readings'):
                all_readings.extend(sensor_data.readings)
        except (ValueError, AttributeError):
            pass
    else:
        # Obtener lecturas de todos los sensores
        try:
            all_sensors = reading_repo.findAll()
            for sensor in all_sensors:
                if hasattr(sensor, 'readings'):
                    all_readings.extend(sensor.readings)
        except Exception as e:
            print(f"Error obteniendo lecturas: {e}")
    
    # Aplicar filtros
    filtered_readings = []
    
    for reading in all_readings:
        # Filtro por tipo de sensor
        if sensor_type and hasattr(reading, 'sensor_type'):
            if reading.sensor_type != sensor_type:
                continue
        
        # Filtro por rango de fechas
        if start_date:
            reading_time = getattr(reading, 'timestamp', None)
            if reading_time:
                if isinstance(start_date, str):
                    start_date = datetime.fromisoformat(start_date)
                if reading_time < start_date:
                    continue
        
        if end_date:
            reading_time = getattr(reading, 'timestamp', None)
            if reading_time:
                if isinstance(end_date, str):
                    end_date = datetime.fromisoformat(end_date)
                if reading_time > end_date:
                    continue
        
        # Filtro por valor mínimo
        if min_value is not None:
            reading_value = getattr(reading, 'value', None)
            if reading_value is not None and reading_value < min_value:
                continue
        
        # Filtro por valor máximo
        if max_value is not None:
            reading_value = getattr(reading, 'value', None)
            if reading_value is not None and reading_value > max_value:
                continue
        
        filtered_readings.append(reading)
    
    # Ordenar por timestamp (más recientes primero)
    filtered_readings.sort(
        key=lambda x: getattr(x, 'timestamp', datetime.min),
        reverse=True
    )
    
    # Aplicar límite
    return filtered_readings[:limit]


def simulateReading(sensor: Sensor) -> Reading:
    """
    Simula una lectura de sensor basada en su tipo y umbrales configurados.
    Genera valores realistas según el tipo de sensor.
    
    Args:
        sensor: Objeto Sensor del cual simular una lectura
        
    Returns:
        Objeto Reading con los datos simulados
    """
    sensor_type = sensor.type.lower()
    thresholds = sensor.thresholds
    
    # Obtener umbrales o usar valores por defecto
    min_threshold = thresholds.get("min", None)
    max_threshold = thresholds.get("max", None)
    
    # Generar valor según el tipo de sensor
    if sensor_type == "temperature":
        # Temperatura: -10°C a 45°C, típicamente 18-28°C
        if min_threshold is None:
            min_threshold = 15.0
        if max_threshold is None:
            max_threshold = 30.0
        
        # Añadir variación aleatoria
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 4
        value = base_value + random.uniform(-variation, variation)
        value = round(value, 1)
        unit = "°C"
        
    elif sensor_type == "humidity":
        # Humedad: 0-100%, típicamente 30-70%
        if min_threshold is None:
            min_threshold = 30.0
        if max_threshold is None:
            max_threshold = 70.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 4
        value = base_value + random.uniform(-variation, variation)
        value = max(0, min(100, round(value, 1)))  # Limitar entre 0-100
        unit = "%"
        
    elif sensor_type == "light" or sensor_type == "luminosity":
        # Luminosidad: 0-10000 lux
        if min_threshold is None:
            min_threshold = 100.0
        if max_threshold is None:
            max_threshold = 1000.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 3
        value = base_value + random.uniform(-variation, variation)
        value = max(0, round(value, 0))
        unit = "lux"
        
    elif sensor_type == "air_quality" or sensor_type == "co2":
        # Calidad del aire (CO2): 400-2000 ppm
        if min_threshold is None:
            min_threshold = 400.0
        if max_threshold is None:
            max_threshold = 1000.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 4
        value = base_value + random.uniform(-variation, variation)
        value = max(400, round(value, 0))
        unit = "ppm"
        
    elif sensor_type == "pressure":
        # Presión atmosférica: 980-1050 hPa
        if min_threshold is None:
            min_threshold = 1000.0
        if max_threshold is None:
            max_threshold = 1025.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 6
        value = base_value + random.uniform(-variation, variation)
        value = round(value, 1)
        unit = "hPa"
        
    elif sensor_type == "motion" or sensor_type == "presence":
        # Sensor de movimiento: 0 o 1 (booleano)
        value = random.choice([0, 1])
        unit = "boolean"
        
    elif sensor_type == "sound" or sensor_type == "noise":
        # Nivel de sonido: 30-90 dB
        if min_threshold is None:
            min_threshold = 40.0
        if max_threshold is None:
            max_threshold = 70.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 4
        value = base_value + random.uniform(-variation, variation)
        value = max(0, round(value, 1))
        unit = "dB"
        
    elif sensor_type == "distance":
        # Distancia: 0-400 cm
        if min_threshold is None:
            min_threshold = 10.0
        if max_threshold is None:
            max_threshold = 200.0
        
        base_value = (min_threshold + max_threshold) / 2
        variation = (max_threshold - min_threshold) / 3
        value = base_value + random.uniform(-variation, variation)
        value = max(0, round(value, 1))
        unit = "cm"
        
    else:
        # Sensor genérico: valor entre umbrales o 0-100
        if min_threshold is None:
            min_threshold = 0.0
        if max_threshold is None:
            max_threshold = 100.0
        
        value = random.uniform(min_threshold, max_threshold)
        value = round(value, 2)
        unit = "units"
    
    # Crear objeto Reading
    reading = Reading(
        sensor_id=sensor.id,
        timestamp=datetime.now(),
        value=value,
        unit=unit,
        sensor_type=sensor_type
    )
    
    # Guardar la lectura en el repositorio
    try:
        reading_repo.save(sensor.id, reading)
    except Exception as e:
        print(f"Error guardando lectura simulada: {e}")
    
    return reading


# Clase auxiliar Reading si no existe en el modelo
class Reading:
    """Representa una lectura de sensor."""
    
    def __init__(self, sensor_id: UUID, timestamp: datetime, value: float, 
                 unit: str, sensor_type: str = "generic"):
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.value = value
        self.unit = unit
        self.sensor_type = sensor_type
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la lectura a diccionario."""
        return {
            "sensor_id": str(self.sensor_id),
            "timestamp": self.timestamp.isoformat(),
            "value": self.value,
            "unit": self.unit,
            "sensor_type": self.sensor_type
        }
    
    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Reading":
        """Crea una lectura desde un diccionario."""
        return Reading(
            sensor_id=UUID(d["sensor_id"]),
            timestamp=datetime.fromisoformat(d["timestamp"]),
            value=d["value"],
            unit=d["unit"],
            sensor_type=d.get("sensor_type", "generic")
        )