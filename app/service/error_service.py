from __future__ import annotations

import traceback
from typing import Optional

from app.repository.error_repository import ErrorRepository


class ErrorService:
    def __init__(self, error_repository: ErrorRepository | None = None):
        self.error_repository = error_repository or ErrorRepository()

    def capture_exception(
        self,
        exc: Exception,
        *,
        severity: str = "ERROR",
        source_layer: str = "SERVICE",
        user_id: Optional[int] = None,
        community_id: Optional[int] = None,
        target_entity_type: Optional[str] = None,
        target_entity_id: Optional[int] = None,
    ) -> int:
        stacktrace = self._sanitize_stacktrace(traceback.format_exc())
        return self.error_repository.add(
            {
                "exception_type": exc.__class__.__name__,
                "severity": severity,
                "message": str(exc),
                "source_layer": source_layer,
                "stacktrace": stacktrace,
                "user_id": user_id,
                "community_id": community_id,
                "target_entity_type": target_entity_type,
                "target_entity_id": target_entity_id,
            }
        )

    def _sanitize_stacktrace(self, raw_stacktrace: str) -> str:
        if not raw_stacktrace:
            return ""
        # Keep stacktrace bounded and avoid accidental leakage in exports/UI.
        return raw_stacktrace[:8000]
