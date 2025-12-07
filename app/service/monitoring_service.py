# app/service/monitoring_service.py
import time
import threading
from typing import List, Optional
from datetime import datetime
from app.service.sensor_service import simulateReading, getSensorReadings
from app.service.alert_service import evaluate, getAlerts
from app.repository.sensor_repository import SensorRepository
from app.repository.log_repository import LogRepository

# Instancias de repositorios
sensor_repo = SensorRepository()
log_repo = LogRepository()

# Variables de control del servicio
_monitoring_active = False
_monitoring_thread: Optional[threading.Thread] = None
_monitoring_interval = 30  # Intervalo en segundos entre cada ciclo de monitoreo


def run() -> None:
    """
    Inicia el servicio de monitoreo continuo.
    
    Este servicio realiza las siguientes tareas de forma periódica:
    1. Simula lecturas de todos los sensores activos
    2. Evalúa cada lectura para generar alertas si es necesario
    3. Registra eventos importantes en el log
    4. Maneja errores de forma robusta para mantener el servicio activo
    
    El servicio se ejecuta en un hilo separado para no bloquear la aplicación.
    """
    global _monitoring_active, _monitoring_thread
    
    # Si ya está activo, no iniciar otro
    if _monitoring_active:
        print("El servicio de monitoreo ya está en ejecución")
        return
    
    # Marcar como activo
    _monitoring_active = True
    
    # Crear y iniciar el hilo de monitoreo
    _monitoring_thread = threading.Thread(target=_monitoring_loop, daemon=True)
    _monitoring_thread.start()
    
    print(f"✓ Servicio de monitoreo iniciado (intervalo: {_monitoring_interval}s)")
    
    # Registrar inicio en el log
    try:
        log_repo.add({
            "event_type": "monitoring_started",
            "description": f"Servicio de monitoreo iniciado con intervalo de {_monitoring_interval} segundos",
            "metadata": {
                "interval": _monitoring_interval,
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Error registrando inicio del monitoreo: {e}")


def stop() -> None:
    """
    Detiene el servicio de monitoreo.
    """
    global _monitoring_active
    
    if not _monitoring_active:
        print("El servicio de monitoreo no está en ejecución")
        return
    
    _monitoring_active = False
    print("✓ Servicio de monitoreo detenido")
    
    # Registrar detención en el log
    try:
        log_repo.add({
            "event_type": "monitoring_stopped",
            "description": "Servicio de monitoreo detenido",
            "metadata": {
                "timestamp": datetime.now().isoformat()
            }
        })
    except Exception as e:
        print(f"Error registrando detención del monitoreo: {e}")


def is_running() -> bool:
    """
    Verifica si el servicio de monitoreo está activo.
    
    Returns:
        True si está activo, False en caso contrario
    """
    return _monitoring_active


def set_interval(seconds: int) -> None:
    """
    Configura el intervalo de monitoreo.
    
    Args:
        seconds: Intervalo en segundos (mínimo 5, máximo 3600)
    """
    global _monitoring_interval
    
    # Validar rango
    if seconds < 5:
        seconds = 5
    elif seconds > 3600:
        seconds = 3600
    
    _monitoring_interval = seconds
    print(f"✓ Intervalo de monitoreo actualizado a {seconds} segundos")


def _monitoring_loop() -> None:
    """
    Bucle principal del servicio de monitoreo.
    Se ejecuta continuamente mientras _monitoring_active sea True.
    """
    cycle_count = 0
    
    print("Iniciando bucle de monitoreo...")
    
    while _monitoring_active:
        try:
            cycle_count += 1
            cycle_start = datetime.now()
            
            print(f"\n--- Ciclo de monitoreo #{cycle_count} - {cycle_start.strftime('%Y-%m-%d %H:%M:%S')} ---")
            
            # 1. Obtener todos los sensores
            sensors = _get_active_sensors()
            
            if not sensors:
                print(" No hay sensores activos para monitorear")
                time.sleep(_monitoring_interval)
                continue
            
            print(f"Monitoreando {len(sensors)} sensores...")
            
            # Contadores de estadísticas
            readings_count = 0
            alerts_count = 0
            errors_count = 0
            
            # 2. Para cada sensor, simular lectura y evaluar alertas
            for sensor in sensors:
                try:
                    # Simular lectura
                    reading = simulateReading(sensor)
                    readings_count += 1
                    
                    print(f"  Sensor {sensor.type} ({sensor.id}): {reading.value} {reading.unit}")
                    
                    # Evaluar si genera alerta
                    alert = evaluate(reading)
                    
                    if alert:
                        alerts_count += 1
                        severity = alert.severity.value if hasattr(alert.severity, 'value') else str(alert.severity)
                        print(f"   ALERTA generada: [{severity}] {alert.message}")
                        
                        # Registrar alerta en el log
                        log_repo.add({
                            "event_type": "alert_generated",
                            "description": f"Alerta generada: {alert.message}",
                            "metadata": {
                                "alert_id": str(alert.id),
                                "sensor_id": str(sensor.id),
                                "sensor_type": sensor.type,
                                "severity": severity,
                                "value": reading.value
                            }
                        })
                
                except Exception as e:
                    errors_count += 1
                    print(f" Error procesando sensor {sensor.id}: {e}")
                    
                    # Registrar error en el log
                    try:
                        log_repo.add({
                            "event_type": "monitoring_error",
                            "description": f"Error al procesar sensor: {str(e)}",
                            "metadata": {
                                "sensor_id": str(sensor.id),
                                "error": str(e)
                            }
                        })
                    except:
                        pass
            
            # 3. Resumen del ciclo
            cycle_duration = (datetime.now() - cycle_start).total_seconds()
            
            print(f"\n✓ Ciclo completado en {cycle_duration:.2f}s")
            print(f"  - Lecturas: {readings_count}")
            print(f"  - Alertas: {alerts_count}")
            print(f"  - Errores: {errors_count}")
            
            # Registrar resumen del ciclo
            try:
                log_repo.add({
                    "event_type": "monitoring_cycle",
                    "description": f"Ciclo de monitoreo #{cycle_count} completado",
                    "metadata": {
                        "cycle": cycle_count,
                        "duration": cycle_duration,
                        "sensors_monitored": len(sensors),
                        "readings_generated": readings_count,
                        "alerts_generated": alerts_count,
                        "errors": errors_count
                    }
                })
            except Exception as e:
                print(f"Error registrando resumen del ciclo: {e}")
            
            # 4. Esperar hasta el próximo ciclo
            print(f"Esperando {_monitoring_interval} segundos hasta el próximo ciclo...\n")
            time.sleep(_monitoring_interval)
        
        except KeyboardInterrupt:
            print("\nMonitoreo interrumpido por el usuario")
            break
        
        except Exception as e:
            print(f"Error crítico en el bucle de monitoreo: {e}")
            errors_count += 1
            
            # Intentar continuar después de un error crítico
            print(f"Reintentando en {_monitoring_interval} segundos...")
            time.sleep(_monitoring_interval)
    
    print("Bucle de monitoreo finalizado")


def _get_active_sensors() -> List:
    """
    Obtiene la lista de sensores activos del repositorio.
    
    Returns:
        Lista de sensores activos
    """
    try:
        all_sensors = sensor_repo.findAll()
        
        # Filtrar solo sensores activos si tienen ese atributo
        active_sensors = [
            sensor for sensor in all_sensors
            if getattr(sensor, 'is_active', True)
        ]
        
        return active_sensors
    
    except Exception as e:
        print(f"Error obteniendo sensores: {e}")
        return []


def get_monitoring_stats() -> dict:
    """
    Obtiene estadísticas del servicio de monitoreo.
    
    Returns:
        Diccionario con estadísticas del servicio
    """
    try:
        # Obtener logs de monitoreo recientes
        all_logs = log_repo.all()
        monitoring_logs = [
            log for log in all_logs
            if log.get("event_type") in ["monitoring_cycle", "alert_generated", "monitoring_error"]
        ]
        
        # Contar por tipo
        cycles = len([l for l in monitoring_logs if l.get("event_type") == "monitoring_cycle"])
        alerts = len([l for l in monitoring_logs if l.get("event_type") == "alert_generated"])
        errors = len([l for l in monitoring_logs if l.get("event_type") == "monitoring_error"])
        
        # Último ciclo
        cycle_logs = [l for l in monitoring_logs if l.get("event_type") == "monitoring_cycle"]
        last_cycle = None
        if cycle_logs:
            cycle_logs.sort(key=lambda x: x.get("ts", 0), reverse=True)
            last_cycle = datetime.fromtimestamp(cycle_logs[0].get("ts", 0)).isoformat()
        
        return {
            "is_running": _monitoring_active,
            "interval_seconds": _monitoring_interval,
            "total_cycles": cycles,
            "total_alerts_generated": alerts,
            "total_errors": errors,
            "last_cycle": last_cycle,
            "monitored_sensors": len(_get_active_sensors())
        }
    
    except Exception as e:
        return {
            "is_running": _monitoring_active,
            "interval_seconds": _monitoring_interval,
            "error": str(e)
        }