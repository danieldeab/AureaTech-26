import json
import uuid
from pathlib import Path
from datetime import datetime

class ChatRepository:
    def __init__(
        self,
        chats_path="data/chats.json",
        messages_path="data/chat_messages.json",
    ):
        self.chats_path = Path(chats_path)
        self.messages_path = Path(messages_path)

    def _read_json(self, path: Path) -> list:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_json(self, path: Path, data: list) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def get_threads_for_technician(self, technician_id: str) -> list[dict]:
        chats = self._read_json(self.chats_path)
        return [c for c in chats if c.get("technician_id") == technician_id]

    def get_chat_by_id(self, chat_id: str) -> dict | None:
        chats = self._read_json(self.chats_path)
        return next((c for c in chats if c.get("id") == chat_id), None)

    def get_messages(self, chat_id: str) -> list[dict]:
        msgs = self._read_json(self.messages_path)
        return [m for m in msgs if m.get("chat_id") == chat_id]

    def create_chat(self, community_id, faq_id, title, neighbor_id, technician_id) -> str:
        chats = self._read_json(self.chats_path)
        chat_id = str(uuid.uuid4())
        chats.append({
            "id": chat_id,
            "community_id": community_id,
            "faq_id": faq_id,
            "title": title,
            "neighbor_id": neighbor_id,
            "technician_id": technician_id,
            "status": "OPEN",
            "created_at": datetime.now().isoformat(),
            "resolved_at": None,
        })
        self._write_json(self.chats_path, chats)
        return chat_id

    def add_message(self, chat_id, sender_id, sender_role, text) -> None:
        msgs = self._read_json(self.messages_path)
        msgs.append({
            "id": str(uuid.uuid4()),
            "chat_id": chat_id,
            "sender_id": sender_id,
            "sender_role": sender_role,
            "text": text,
            "timestamp": datetime.now().isoformat(),
        })
        self._write_json(self.messages_path, msgs)

    def resolve_chat(self, chat_id: str) -> None:
        chats = self._read_json(self.chats_path)
        for c in chats:
            if c.get("id") == chat_id:
                c["status"] = "RESOLVED"
                c["resolved_at"] = datetime.now().isoformat()
                break
        self._write_json(self.chats_path, chats)