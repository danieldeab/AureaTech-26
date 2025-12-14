import json, uuid, os
from datetime import datetime, timezone
from app.repository.interfaces.log_repository_interface import ILogRepository
from app.model.log_entry import LogEntry

# Resolve data path to package root, not CWD
_PACKAGE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(_PACKAGE_ROOT, "data")
LOGS_PATH = os.path.join(DATA_DIR, "logs.json")

class LogRepository(ILogRepository):
    def __init__(self, path=LOGS_PATH):
        self.path = path
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"eventos": []}, f, ensure_ascii=False, indent=2)

    def add(self, entry: LogEntry) -> None:
        if not isinstance(entry, LogEntry):
            raise TypeError("LogRepository.add expects a LogEntry object")
        
        with open(self.path, "r", encoding="utf-8") as f:
            db = json.load(f)

        if "eventos" not in db:
            db["eventos"] = []

        db["eventos"].append(entry.to_dict())

        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(db, f, indent=2)

    def get_all(self):
        with open(self.path, "r", encoding="utf-8") as f:
            db = json.load(f)
        return db.get("eventos", [])

    def all(self):
        return self.get_all()
