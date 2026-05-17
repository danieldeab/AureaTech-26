from __future__ import annotations

from typing import Any

from app.infraestructure.db import get_db


class AutomationRuleRepository:
    def __init__(self):
        self.db = get_db()

    def find_by_community_id(self, community_id: int) -> list[dict[str, Any]]:
        sql = """
            SELECT
                ar.rule_id,
                ar.sensor_id,
                s.community_id,
                s.sensor_type,
                ar.rule_name,
                ar.metric_key,
                ar.comparison_operator,
                ar.threshold_value,
                ar.is_enabled,
                raa.rule_actuator_action_id,
                raa.actuator_id,
                raa.command_type,
                raa.target_state,
                rla.rule_alert_action_id,
                rla.alert_type,
                rla.severity,
                rla.message_template
            FROM automation_rule ar
            INNER JOIN sensor s
                ON s.sensor_id = ar.sensor_id
            LEFT JOIN rule_actuator_action raa
                ON raa.rule_id = ar.rule_id
            LEFT JOIN rule_alert_action rla
                ON rla.rule_id = ar.rule_id
            WHERE s.community_id = %s
            ORDER BY ar.sensor_id ASC, ar.rule_id ASC
        """
        return self.db.execute(sql, (int(community_id),))

    def find_by_sensor_id(self, sensor_id: int) -> list[dict[str, Any]]:
        sql = """
            SELECT
                ar.rule_id,
                ar.sensor_id,
                s.community_id,
                s.sensor_type,
                ar.rule_name,
                ar.metric_key,
                ar.comparison_operator,
                ar.threshold_value,
                ar.is_enabled,
                raa.rule_actuator_action_id,
                raa.actuator_id,
                raa.command_type,
                raa.target_state,
                rla.rule_alert_action_id,
                rla.alert_type,
                rla.severity,
                rla.message_template
            FROM automation_rule ar
            INNER JOIN sensor s
                ON s.sensor_id = ar.sensor_id
            LEFT JOIN rule_actuator_action raa
                ON raa.rule_id = ar.rule_id
            LEFT JOIN rule_alert_action rla
                ON rla.rule_id = ar.rule_id
            WHERE ar.sensor_id = %s
            ORDER BY ar.rule_id ASC
        """
        return self.db.execute(sql, (int(sensor_id),))
