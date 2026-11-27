"""Exports the API as a Postman collection plus Development and Production environments.

    python generate_postman.py

Output (folder `postman/`):
    Student_Management_API.postman_collection.json
    Development.postman_environment.json
    Production.postman_environment.json

Everything is generated from the live OpenAPI spec (app.openapi()), so the collection never drifts away
from the code. Import all three files in Postman (Import button), pick an environment in the top-right
dropdown, then run the collection.
"""
import json
import re
import uuid
from pathlib import Path

from main import app

OUT = Path(__file__).with_name("postman")
NS = uuid.UUID("6f1c2f5e-0000-4000-8000-000000000010")      # fixed namespace -> same ids on every run
SCHEMA = "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
FOLDER_ORDER = ["v2", "v1 (deprecated)", "meta"]
QUERY_DEFAULTS = {"page": "1", "limit": "10", "branch": "CSE", "search": "aarav", "department_id": "1"}


def pid(*parts: str) -> str:
    return str(uuid.uuid5(NS, "|".join(parts)))


# ----------------------------------------------------------------- request bodies
def resolve(spec: dict, schema: dict) -> dict:
    if "$ref" in schema:
        name = schema["$ref"].split("/")[-1]
        return spec["components"]["schemas"][name]
    return schema


def example_for(spec: dict, schema: dict):
    schema = resolve(spec, schema)
    if schema.get("examples"):
        return schema["examples"][0]
    if "example" in schema:
        return schema["example"]
    props = schema.get("properties", {})
    return {k: example_for(spec, v) if "$ref" in v or v.get("type") == "object" else v.get("default", "string")
            for k, v in props.items()}


def request_body(spec: dict, operation: dict):
    media = operation.get("requestBody", {}).get("content", {}).get("application/json")
    if not media:
        return None
    if media.get("examples"):                                   # named examples from openapi_examples
        first = next(iter(media["examples"].values()))
        body = first["value"]
    else:
        body = example_for(spec, media["schema"])
    body = dict(body)
    if "email" in body:
        body["email"] = "{{$randomEmail}}"                      # Postman dynamic variable: re-runnable, no 409
    return json.dumps(body, indent=2)


# ----------------------------------------------------------------- one request
def expected_status(operation: dict) -> str:
    return next(code for code in operation["responses"] if code.startswith("2"))


def test_script(method: str, path: str, operation: dict) -> list[str]:
    status = int(expected_status(operation))
    lines = [
        f'pm.test("Status code is {status}", function () {{ pm.response.to.have.status({status}); }});',
        'pm.test("Responds in under 1000 ms", function () { pm.expect(pm.response.responseTime).to.be.below(1000); });',
    ]
    if status != 204:
        lines.append('pm.test("Body is JSON", function () { pm.response.to.be.json; });')
    if operation.get("deprecated"):
        lines += [
            'pm.test("Deprecation headers are present", function () {',
            '    pm.expect(pm.response.headers.has("Deprecation")).to.be.true;',
            '    pm.expect(pm.response.headers.has("Sunset")).to.be.true;',
            '    pm.expect(pm.response.headers.get("Link")).to.include("successor-version");',
            '});',
        ]
    if path == "/api/v2/students" and method == "get":
        lines += ['pm.test("Has pagination fields", function () {',
                  '    const b = pm.response.json();',
                  '    pm.expect(b).to.have.all.keys("items", "page", "limit", "total", "total_pages", "links");',
                  '});']
    if method == "post" and path.endswith("/students"):
        lines.append('pm.collectionVariables.set("student_id", pm.response.json().id);   // reuse in later requests')
    return lines


def build_item(spec: dict, method: str, path: str, operation: dict) -> dict:
    parts = [p for p in path.strip("/").split("/")]
    url_path = [f":{p[1:-1]}" if p.startswith("{") else p for p in parts]
    query = []
    for param in operation.get("parameters", []):
        if param["in"] == "query":
            value = QUERY_DEFAULTS.get(param["name"], str(param["schema"].get("default", "")))
            query.append({"key": param["name"], "value": value,
                          "disabled": param["name"] not in ("page", "limit"),
                          "description": param.get("description", "")})
    variables = [{"key": p["name"], "value": "{{student_id}}", "description": p.get("description", "")}
                 for p in operation.get("parameters", []) if p["in"] == "path"]
    raw = "{{base_url}}/" + "/".join(url_path)
    enabled = [f"{q['key']}={q['value']}" for q in query if not q["disabled"]]
    if enabled:
        raw += "?" + "&".join(enabled)
    url = {"raw": raw, "host": ["{{base_url}}"], "path": url_path}
    if query:
        url["query"] = query
    if variables:
        url["variable"] = variables

    request = {"method": method.upper(), "header": [], "url": url,
               "description": operation.get("description") or operation.get("summary", "")}
    body = request_body(spec, operation)
    if body:
        request["header"].append({"key": "Content-Type", "value": "application/json"})
        request["body"] = {"mode": "raw", "raw": body, "options": {"raw": {"language": "json"}}}

    name = f"{operation.get('summary') or operation['operationId']}"
    if operation.get("deprecated"):
        name += " [deprecated]"
    return {"id": pid("req", method, path), "name": name,
            "event": [{"listen": "test", "script": {"type": "text/javascript",
                                                    "exec": test_script(method, path, operation)}}],
            "request": request}


def sort_key(method: str, path: str):
    order = {"post": 0, "get": 1, "put": 2, "patch": 2, "delete": 3}
    return (order.get(method, 9), "{" in path, path)       # create first, then list, then get-by-id


# ----------------------------------------------------------------- collection and environments
def build_collection(spec: dict) -> dict:
    folders: dict[str, list] = {}
    for path, methods in spec["paths"].items():
        for method, op in methods.items():
            folders.setdefault(op["tags"][0], []).append((method, path, op))
    items = []
    for tag in sorted(folders, key=lambda t: FOLDER_ORDER.index(t) if t in FOLDER_ORDER else 99):
        ops = sorted(folders[tag], key=lambda x: sort_key(x[0], x[1]))
        tag_info = next((t for t in spec.get("tags", []) if t["name"] == tag), {})
        items.append({"id": pid("folder", tag), "name": tag, "description": tag_info.get("description", ""),
                      "item": [build_item(spec, m, p, o) for m, p, o in ops]})
    info = spec["info"]
    return {
        "info": {"_postman_id": pid("collection"), "name": info["title"], "description": info.get("description", ""),
                 "schema": SCHEMA},
        "item": items,
        "variable": [{"key": "base_url", "value": "http://127.0.0.1:8000", "type": "string"},
                     {"key": "student_id", "value": "1", "type": "string"}],
    }


def build_environment(name: str, base_url: str) -> dict:
    return {"id": pid("env", name), "name": name,
            "values": [{"key": "base_url", "value": base_url, "type": "default", "enabled": True}],
            "_postman_variable_scope": "environment"}


def generate() -> dict[str, dict]:
    spec = app.openapi()
    return {
        "Student_Management_API.postman_collection.json": build_collection(spec),
        "Development.postman_environment.json": build_environment("Development", "http://127.0.0.1:8000"),
        "Production.postman_environment.json": build_environment("Production", "https://your-app.onrender.com"),
    }


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    for filename, content in generate().items():
        (OUT / filename).write_text(json.dumps(content, indent=2) + "\n", encoding="utf-8")
        print("wrote", OUT.name + "/" + filename)
    print("\nImport the three files into Postman, select the 'Development' environment, then run the collection.")
