import json, uuid, os
from datetime import datetime
from app.repository.interfaces.log_repository_interface import ILogRepository

class LogRepository(ILogRepository):
    def __init__(self, path="data/logs.json"):
        self.path = path
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({"eventos": []}, f)

    def add(self, entry: dict):
        entry["id"] = str(uuid.uuid4())
        entry["ts"] = int(datetime.now().timestamp())

        with open(self.path, "r") as f:
            db = json.load(f)

        if "eventos" not in db:
            db["eventos"] = []

        db["eventos"].append(entry)

        with open(self.path, "w") as f:
            json.dump(db, f, indent=2)

    def all(self):
        with open(self.path, "r") as f:
            db = json.load(f)

        return db.get("eventos", [])