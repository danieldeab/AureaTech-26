from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable

from app.model.enums import RoleEnum, SeverityEnum


class AutomationRuleService:
    def __init__(
        self,
        rule_repository,
        *,
        alert_service,
        actuator_service=None,
        user_repository=None,
        audit_log_service=None,
        error_service=None,
    ):
        self.rule_repository = rule_repository
        self.alert_service = alert_service
        self.actuator_service = actuator_service
        self.user_repository = user_repository
        self.audit_log_service = audit_log_service
        self.error_service = error_service

    def evaluate_reading(
        self,
        reading,
        *,
        sensor_type: str,
        community_id: int,
        recipient_user_ids: list[int] | None = None,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        try:
            rows = self.rule_repository.find_by_sensor_id(int(reading.sensor_id))
            matched = []
            alerts = []
            actuator_results = []

            for rule in self._group_rules(rows):
                if not self._is_enabled(rule) or not self._matches(rule, float(reading.value)):
                    continue

                matched.append(rule)
                recipients = self._resolve_recipients(
                    community_id=int(community_id),
                    explicit_recipients=recipient_user_ids,
                    user_id=user_id,
                )

                for alert_action in rule["alert_actions"]:
                    alerts.append(
                        self.alert_service.create_and_deliver_alert(
                            community_id=int(community_id),
                            recipients=recipients,
                            alert_type=str(alert_action["alert_type"]),
                            severity=self._severity(alert_action["severity"]),
                            message=self._format_message(
                                str(alert_action["message_template"]),
                                rule=rule,
                                reading=reading,
                                sensor_type=sensor_type,
                            ),
                            rule_alert_action_id=int(alert_action["rule_alert_action_id"]),
                        )
                    )

                for actuator_action in rule["actuator_actions"]:
                    if not self.actuator_service:
                        continue
                    actuator_results.append(
                        self.actuator_service.apply_rule_action(
                            actuator_id=actuator_action["actuator_id"],
                            command_type=str(actuator_action["command_type"]),
                            target_state=actuator_action["target_state"],
                            rule_id=int(rule["rule_id"]),
                            community_id=int(community_id),
                        )
                    )

                self._log_rule_execution(rule, community_id)

            return {
                "matched_rules": matched,
                "alerts": alerts,
                "actuators": actuator_results,
            }
        except Exception as exc:
            if self.error_service:
                self.error_service.capture_exception(
                    exc,
                    severity="ERROR",
                    source_layer="AUTOMATION",
                    community_id=int(community_id),
                    target_entity_type="sensor",
                    target_entity_id=int(reading.sensor_id),
                )
            raise

    def _group_rules(self, rows: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
        grouped: dict[int, dict[str, Any]] = {}
        seen_alert_actions: dict[int, set[int]] = defaultdict(set)
        seen_actuator_actions: dict[int, set[int]] = defaultdict(set)

        for row in rows:
            rule_id = int(row["rule_id"])
            rule = grouped.setdefault(
                rule_id,
                {
                    "rule_id": rule_id,
                    "sensor_id": row["sensor_id"],
                    "rule_name": row["rule_name"],
                    "metric_key": row.get("metric_key"),
                    "comparison_operator": row["comparison_operator"],
                    "threshold_value": row["threshold_value"],
                    "is_enabled": row["is_enabled"],
                    "alert_actions": [],
                    "actuator_actions": [],
                },
            )

            alert_action_id = row.get("rule_alert_action_id")
            if alert_action_id is not None and int(alert_action_id) not in seen_alert_actions[rule_id]:
                seen_alert_actions[rule_id].add(int(alert_action_id))
                rule["alert_actions"].append(
                    {
                        "rule_alert_action_id": int(alert_action_id),
                        "alert_type": row["alert_type"],
                        "severity": row["severity"],
                        "message_template": row["message_template"],
                    }
                )

            actuator_action_id = row.get("rule_actuator_action_id")
            if actuator_action_id is not None and int(actuator_action_id) not in seen_actuator_actions[rule_id]:
                seen_actuator_actions[rule_id].add(int(actuator_action_id))
                rule["actuator_actions"].append(
                    {
                        "rule_actuator_action_id": int(actuator_action_id),
                        "actuator_id": row["actuator_id"],
                        "command_type": row["command_type"],
                        "target_state": row["target_state"],
                    }
                )

        return list(grouped.values())

    def _matches(self, rule: dict[str, Any], value: float) -> bool:
        threshold = float(rule["threshold_value"])
        operator = str(rule["comparison_operator"]).strip()
        if operator == ">":
            return value > threshold
        if operator == ">=":
            return value >= threshold
        if operator == "<":
            return value < threshold
        if operator == "<=":
            return value <= threshold
        if operator in {"=", "=="}:
            return value == threshold
        if operator in {"!=", "<>"}:
            return value != threshold
        raise ValueError(f"Unsupported comparison operator: {operator!r}")

    def _is_enabled(self, rule: dict[str, Any]) -> bool:
        return str(rule.get("is_enabled", "1")).strip().upper() not in {"0", "FALSE", "NO"}

    def _severity(self, value) -> SeverityEnum:
        try:
            return SeverityEnum(str(value).upper())
        except ValueError:
            return SeverityEnum.WARN

    def _resolve_recipients(
        self,
        *,
        community_id: int,
        explicit_recipients: list[int] | None,
        user_id: int | None,
    ) -> list[int]:
        if explicit_recipients is not None:
            return [int(uid) for uid in explicit_recipients]
        if user_id is not None:
            return [int(user_id)]
        if not self.user_repository:
            return []

        finder = getattr(self.user_repository, "find_by_community_id", None)
        if not callable(finder):
            return []

        return [
            int(user.id)
            for user in finder(int(community_id))
            if getattr(user, "id", None) is not None
            and getattr(user, "role", None) in {RoleEnum.ADMIN, RoleEnum.TECHNICIAN, RoleEnum.NEIGHBOR}
        ]

    def _format_message(self, template: str, *, rule: dict[str, Any], reading, sensor_type: str) -> str:
        value = float(reading.value)
        base = template.format(
            value=value,
            unit=getattr(reading, "unit", ""),
            sensor_id=reading.sensor_id,
            sensor_type=sensor_type,
            threshold=rule["threshold_value"],
            rule_name=rule["rule_name"],
        )
        if "{value" in template or str(round(value, 2)) in base:
            return base
        return f"{base}: {round(value, 2)} {getattr(reading, 'unit', '')}".strip()

    def _log_rule_execution(self, rule: dict[str, Any], community_id: int) -> None:
        if not self.audit_log_service:
            return
        self.audit_log_service.log(
            actor_id=1,
            actor_role=RoleEnum.ADMIN,
            category="AUTOMATION",
            action="rule_triggered",
            details=f"Rule {rule['rule_id']} triggered: {rule['rule_name']}",
            community_id=int(community_id),
            target_entity_type="automation_rule",
            target_entity_id=int(rule["rule_id"]),
        )
