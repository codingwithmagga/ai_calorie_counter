import json
from pathlib import Path

from app.main import app

if __name__ == "__main__":
    path = Path(__file__).resolve().parent.parent / "openapi.json"
    path.write_text(json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n")
