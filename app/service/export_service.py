# app/service/export_service.py
from __future__ import annotations

import csv
import json
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Iterable, Set

from app.model.user import User
from app.model.enums import RoleEnum
from app.service.audit_log_service import AuditLogService
from app.service.error_service import ErrorService
from app.repository.error_repository import ErrorRepository
from app.repository.log_repository import LogRepository
from app.repository.reading_repository import ReadingRepository
from app.repository.sensor_repository import SensorRepository

# Directorio para exportaciones temporales
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "exports")
os.makedirs(EXPORT_DIR, exist_ok=True)


class ExportService:
    """
    Servicio de exportación de logs y lecturas, con control por rol/comunidad.

    - ADMIN:
        - all_communities=True  -> exporta todas las comunidades
        - all_communities=False -> sólo su comunidad
    - TECHNICIAN / NEIGHBOR:
        - siempre restringidos a su community_id
    """

    def __init__(
        self,
        log_repo: LogRepository | None = None,
        error_repo: ErrorRepository | None = None,
        reading_repo: ReadingRepository | None = None,
        sensor_repo: SensorRepository | None = None,
        audit_log_service: AuditLogService | None = None,
        error_service: ErrorService | None = None,
    ):
        self._log_repo = log_repo or LogRepository()
        self._error_repo = error_repo or ErrorRepository()
        self._reading_repo = reading_repo or ReadingRepository()
        self._sensor_repo = sensor_repo or SensorRepository()
        self._audit_log_service = audit_log_service or AuditLogService(self._log_repo)
        self._error_service = error_service or ErrorService()

    # ------------------------------------------------------
    # Helpers de ámbito de comunidad
    # ------------------------------------------------------
    def _allowed_communities_for_user(
        self,
        user: User,
        all_communities: bool,
    ) -> Optional[Set[int]]:
        """
        Devuelve:
        - None -> sin restricción (ADMIN con all_communities=True)
        - {cid} -> conjunto de comunidades permitidas
        """
        if user.role == RoleEnum.ADMIN and all_communities:
            return None  # sin filtro de comunidad

        cid = getattr(user, "community_id", None)
        if cid is None:
            return None
        return {int(cid)}

    def _actor_id(self, user: User) -> int:
        try:
            return int(getattr(user, "id", 1))
        except Exception:
            return 1

    def _actor_role(self, user: User) -> RoleEnum:
        role = getattr(user, "role", RoleEnum.ADMIN)
        if isinstance(role, RoleEnum):
            return role
        try:
            return RoleEnum(str(role))
        except ValueError:
            return RoleEnum.ADMIN

    def _metadata(
        self,
        *,
        user: User,
        filters: Dict[str, Any],
        export_type: str,
        row_count: int,
    ) -> Dict[str, Any]:
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": self._actor_id(user),
            "role": self._actor_role(user).value,
            "export_type": export_type,
            "filters": filters,
            "schema_version": "drivers-v1",
            "row_count": row_count,
        }

    # ------------------------------------------------------
    # Exportación de LOGS
    # ------------------------------------------------------
    def export_logs_for_user(
        self,
        user: User,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json",
        *,
        all_communities: bool = False,
    ) -> str:
        """
        Exporta logs respetando el ámbito de comunidad según el rol del usuario.
        """
        try:
            filters = filters or {}
            allowed_communities = self._allowed_communities_for_user(user, all_communities)

            search_filters = dict(filters)
            if allowed_communities is not None:
                if len(allowed_communities) == 1:
                    search_filters["community_id"] = next(iter(allowed_communities))
                else:
                    search_filters["community_id"] = next(iter(allowed_communities))
            filtered_logs = self._log_repo.search(search_filters)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata = self._metadata(
                user=user,
                filters=search_filters,
                export_type="audit_logs",
                row_count=len(filtered_logs),
            )
            if format.lower() == "csv":
                filename = f"logs_export_{timestamp}.csv"
                filepath = os.path.join(EXPORT_DIR, filename)
                _export_logs_to_csv(filtered_logs, filepath, metadata=metadata)
            else:
                filename = f"logs_export_{timestamp}.json"
                filepath = os.path.join(EXPORT_DIR, filename)
                _export_logs_to_json(filtered_logs, filepath, metadata=metadata)

            self._audit_log_service.log(
                actor_id=self._actor_id(user),
                actor_role=self._actor_role(user),
                category="EXPORT",
                action="export_requested",
                details=f"audit_logs format={format.lower()} records={len(filtered_logs)}",
                community_id=getattr(user, "community_id", None),
                target_entity_type="audit_log",
            )
            return filepath
        except Exception as exc:
            self._error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(user.id) if getattr(user, "id", None) is not None else None,
                community_id=getattr(user, "community_id", None),
                target_entity_type="audit_log",
            )
            raise

    def export_error_events_for_user(
        self,
        user: User,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json",
        *,
        all_communities: bool = False,
    ) -> str:
        try:
            filters = filters or {}
            allowed_communities = self._allowed_communities_for_user(user, all_communities)
            search_filters = dict(filters)
            if allowed_communities is not None:
                if len(allowed_communities) == 1:
                    search_filters["community_id"] = next(iter(allowed_communities))
                else:
                    search_filters["community_id"] = next(iter(allowed_communities))

            events = self._error_repo.search(search_filters)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            metadata = self._metadata(
                user=user,
                filters=search_filters,
                export_type="error_events",
                row_count=len(events),
            )
            if format.lower() == "csv":
                filename = f"errors_export_{timestamp}.csv"
                filepath = os.path.join(EXPORT_DIR, filename)
                _export_error_events_to_csv(events, filepath, metadata=metadata)
            else:
                filename = f"errors_export_{timestamp}.json"
                filepath = os.path.join(EXPORT_DIR, filename)
                _export_error_events_to_json(events, filepath, metadata=metadata)

            self._audit_log_service.log(
                actor_id=self._actor_id(user),
                actor_role=self._actor_role(user),
                category="EXPORT",
                action="export_requested",
                details=f"error_events format={format.lower()} records={len(events)}",
                community_id=getattr(user, "community_id", None),
                target_entity_type="error_event",
            )
            return filepath
        except Exception as exc:
            self._error_service.capture_exception(
                exc,
                source_layer="SERVICE",
                user_id=int(user.id) if getattr(user, "id", None) is not None else None,
                community_id=getattr(user, "community_id", None),
                target_entity_type="error_event",
            )
            raise

    def export_logs_as_admin(
        self,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json",
    ) -> str:
        """
        Helper para el código legacy: exporta como si fuera un ADMIN con acceso a todas las comunidades.
        No mira ningún usuario real.
        """
        class _FakeAdmin:
            role = RoleEnum.ADMIN
            community_id: Optional[int] = None

        return self.export_logs_for_user(
            user=_FakeAdmin(),  # type: ignore[arg-type]
            filters=filters,
            format=format,
            all_communities=True,
        )

    # ------------------------------------------------------
    # Exportación de LECTURAS
    # ------------------------------------------------------
    def _collect_flat_readings(self) -> List[Dict[str, Any]]:
        sensors = {str(s.sensor_id): s for s in self._sensor_repo.get_all()}
        flat: List[Dict[str, Any]] = []

        for r in self._reading_repo.get_all():
            sensor_id = str(getattr(r, "sensor_id", ""))
            sensor = sensors.get(sensor_id)
            community_id = getattr(sensor, "from_community_id", None) if sensor else None

            flat.append(
                {
                    "sensor_id": sensor_id,
                    "timestamp": getattr(r, "timestamp", None).isoformat()
                    if getattr(r, "timestamp", None)
                    else "",
                    "value": getattr(r, "value", None),
                    "unit": getattr(r, "unit", ""),
                    "type": getattr(sensor, "type", "") if sensor else "",
                    "community_id": community_id,
                }
            )

        return flat

    def export_readings_for_user(
        self,
        user: User,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json",
        *,
        all_communities: bool = False,
    ) -> str:
        """
        Exporta lecturas respetando el ámbito de comunidad según el rol del usuario.
        """
        filters = filters or {}
        allowed_communities = self._allowed_communities_for_user(user, all_communities)

        # Aplanamos todas las lecturas con info de comunidad
        all_readings = self._collect_flat_readings()

        filtered_readings = _filter_readings(all_readings, filters, allowed_communities)
        filtered_readings.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metadata = self._metadata(
            user=user,
            filters=filters,
            export_type="readings",
            row_count=len(filtered_readings),
        )
        if format.lower() == "csv":
            filename = f"readings_export_{timestamp}.csv"
            filepath = os.path.join(EXPORT_DIR, filename)
            _export_readings_to_csv(filtered_readings, filepath, metadata=metadata)
        else:
            filename = f"readings_export_{timestamp}.json"
            filepath = os.path.join(EXPORT_DIR, filename)
            _export_readings_to_json(filtered_readings, filepath, metadata=metadata)

        return filepath

    def export_readings_as_admin(
        self,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json",
    ) -> str:
        """
        Helper legacy: exporta todas las lecturas sin filtro de comunidad.
        """
        class _FakeAdmin:
            role = RoleEnum.ADMIN
            community_id: Optional[int] = None

        return self.export_readings_for_user(
            user=_FakeAdmin(),  # type: ignore[arg-type]
            filters=filters,
            format=format,
            all_communities=True,
        )


# ------------------------------------------------------
# Helpers puros (filtrado y export)
# ------------------------------------------------------
def _parse_timestamp(value: Any) -> Optional[int]:
    """Convierte un valor a timestamp Unix."""
    if not value:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return int(dt.timestamp())
        except Exception:
            try:
                return int(value)
            except Exception:
                return None

    return None


def _normalize_community_id(raw: Any) -> Optional[int]:
    if raw is None:
        return None
    try:
        return int(raw)
    except Exception:
        return None


def _filter_logs(
    logs: Iterable[Dict[str, Any]],
    range: Optional[Dict[str, Any]],
    allowed_communities: Optional[Set[int]],
) -> List[Dict[str, Any]]:
    """
    Filtra logs según:
      - rango temporal
      - user_id (opcional)
      - event_type (opcional)
      - allowed_communities (None = sin filtro)
    """
    if not range:
        range = {}

    start_ts = _parse_timestamp(range.get("start_date"))
    end_ts = _parse_timestamp(range.get("end_date"))
    user_id = range.get("user_id")
    event_type = range.get("event_type")

    filtered: List[Dict[str, Any]] = []

    for log in logs:
        log_ts = log.get("ts", 0)

        # --- Filtro temporal ---
        if start_ts is not None and log_ts < start_ts:
            continue
        if end_ts is not None and log_ts > end_ts:
            continue

        # --- Filtro por usuario ---
        if user_id and log.get("user_id") != str(user_id):
            continue

        # --- Filtro por tipo de evento ---
        if event_type and log.get("event_type") != event_type:
            continue

        # --- Filtro por comunidad ---
        if allowed_communities is not None:
            # intentamos 'community_id' directo o dentro de metadata
            cid_raw = log.get("community_id")
            if cid_raw is None and isinstance(log.get("metadata"), dict):
                cid_raw = log["metadata"].get("community_id")

            cid = _normalize_community_id(cid_raw)
            if cid is None or cid not in allowed_communities:
                continue

        filtered.append(log)

    return filtered


def _filter_readings(
    readings: Iterable[Dict[str, Any]],
    range: Optional[Dict[str, Any]],
    allowed_communities: Optional[Set[int]],
) -> List[Dict[str, Any]]:
    """
    Filtra lecturas según:
      - rango temporal
      - sensor_id (opcional)
      - user_id (si estuviese en el dict)
      - allowed_communities (None = sin filtro)
    """
    if not range:
        range = {}

    start_date = range.get("start_date")
    end_date = range.get("end_date")
    user_id = range.get("user_id")
    sensor_id_filter = range.get("sensor_id")

    # Convertimos fechas ISO a datetime para comparar
    if isinstance(start_date, str):
        try:
            start_date = datetime.fromisoformat(start_date)
        except Exception:
            start_date = None
    if isinstance(end_date, str):
        try:
            end_date = datetime.fromisoformat(end_date)
        except Exception:
            end_date = None

    filtered: List[Dict[str, Any]] = []

    for r in readings:
        # --- Filtro por sensor ---
        if sensor_id_filter and r.get("sensor_id") != str(sensor_id_filter):
            continue

        # --- Filtro temporal ---
        ts_str = r.get("timestamp", "")
        if ts_str:
            try:
                ts_dt = datetime.fromisoformat(ts_str)
                if start_date and ts_dt < start_date:
                    continue
                if end_date and ts_dt > end_date:
                    continue
            except Exception:
                # si no se puede parsear, lo dejamos pasar en cuanto a tiempo
                pass

        # --- Filtro por usuario, si está en el dict ---
        if user_id and r.get("user_id") != str(user_id):
            continue

        # --- Filtro por comunidad ---
        if allowed_communities is not None:
            cid = _normalize_community_id(r.get("community_id"))
            if cid is None or cid not in allowed_communities:
                continue

        filtered.append(r)

    return filtered


def _export_logs_to_json(logs: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_records": len(logs),
        "metadata": metadata or {},
        "logs": logs,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def _write_csv_metadata(writer: csv.writer, metadata: Dict[str, Any] | None) -> None:
    metadata = metadata or {}
    writer.writerow(["metadata_key", "metadata_value"])
    for key in ["generated_at", "generated_by", "role", "export_type", "filters", "schema_version", "row_count"]:
        writer.writerow([key, metadata.get(key, "")])
    writer.writerow([])


def _export_logs_to_csv(logs: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    if not logs:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            _write_csv_metadata(writer, metadata)
            writer.writerow(["id", "timestamp", "event_type", "user_id", "description"])
        return

    fieldnames = set()
    for log in logs:
        fieldnames.update(log.keys())
    fieldnames.add("timestamp_readable")
    fieldnames = sorted(fieldnames)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        raw_writer = csv.writer(f)
        _write_csv_metadata(raw_writer, metadata)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for log in logs:
            row = log.copy()
            if "ts" in row:
                row["timestamp_readable"] = datetime.fromtimestamp(row["ts"]).isoformat()
            writer.writerow(row)


def _export_error_events_to_json(events: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_records": len(events),
        "metadata": metadata or {},
        "errors": events,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def _export_error_events_to_csv(events: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    if not events:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            _write_csv_metadata(writer, metadata)
            writer.writerow(["id", "timestamp", "severity", "source_layer", "message"])
        return

    fieldnames = set()
    for event in events:
        fieldnames.update(event.keys())
    fieldnames = sorted(fieldnames)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        raw_writer = csv.writer(f)
        _write_csv_metadata(raw_writer, metadata)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(events)


def _export_readings_to_json(readings: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    export_data = {
        "export_date": datetime.now().isoformat(),
        "total_records": len(readings),
        "metadata": metadata or {},
        "readings": readings,
    }
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)


def _export_readings_to_csv(readings: List[Dict[str, Any]], filepath: str, metadata: Dict[str, Any] | None = None) -> None:
    if not readings:
        with open(filepath, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            _write_csv_metadata(writer, metadata)
            writer.writerow(["sensor_id", "timestamp", "value", "unit", "type"])
        return

    fieldnames = set()
    for r in readings:
        fieldnames.update(r.keys())
    fieldnames = sorted(fieldnames)

    with open(filepath, "w", encoding="utf-8", newline="") as f:
        raw_writer = csv.writer(f)
        _write_csv_metadata(raw_writer, metadata)
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(readings)


# ------------------------------------------------------
# API legacy compatible (las funciones que ya existían)
# ------------------------------------------------------

_default_export_service = ExportService()


def exportLogs(range: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
    """
    Versión legacy: exporta logs sin restricción de comunidad
    (equivalente a ADMIN con all_communities=True).
    """
    return _default_export_service.export_logs_as_admin(filters=range, format=format)


def exportReadings(range: Optional[Dict[str, Any]] = None, format: str = "json") -> str:
    """
    Versión legacy: exporta lecturas sin restricción de comunidad
    (equivalente a ADMIN con all_communities=True).
    """
    return _default_export_service.export_readings_as_admin(filters=range, format=format)
