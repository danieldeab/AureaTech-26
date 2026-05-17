"""
Deprecated JSON-era alerts controller.

Second-semester runtime persistence is DB-backed. Alert reads/writes now go
through app.repository.alert_repository.AlertRepository and
app.service.alert_service.AlertService.
"""


class LegacyJsonAlertsControllerDisabled(RuntimeError):
    pass


class UserRepository:
    def __init__(self):
        raise LegacyJsonAlertsControllerDisabled(
            "data/usuarios.json is no longer a runtime store. "
            "Use app.repository.user_repository.UserRepository instead."
        )
