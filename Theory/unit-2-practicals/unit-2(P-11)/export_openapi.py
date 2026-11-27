"""Writes the OpenAPI spec to docs/openapi.json (commit it with your repo, and import it into Postman).

    python export_openapi.py
"""
import json
from pathlib import Path

from app.main import app

out = Path(__file__).with_name("docs")
out.mkdir(exist_ok=True)
(out / "openapi.json").write_text(json.dumps(app.openapi(), indent=2) + "\n", encoding="utf-8")
print("wrote docs/openapi.json")
