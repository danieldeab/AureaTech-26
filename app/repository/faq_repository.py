import json
from pathlib import Path

class FAQRepository:
    def __init__(self, path="data/faqs.json"):
        self.path = Path(path)

    def find_by_community_id(self, community_id: str) -> list[dict]:
        if not self.path.exists():
            return []
        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return [faq for faq in data if faq.get("community_id") == community_id]