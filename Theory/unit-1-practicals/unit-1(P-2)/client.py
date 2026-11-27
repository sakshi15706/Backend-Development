"""Small client that exercises every HTTP method against the Flask API.
Start the server first:  python app.py
Then run:               python client.py
"""
import requests

BASE = "http://localhost:5000"


def show(label, resp):
    print(f"{label:<14} -> {resp.status_code}  {resp.text.strip()}")


show("GET all", requests.get(f"{BASE}/students"))
show("GET one", requests.get(f"{BASE}/students/1"))
show("POST", requests.post(f"{BASE}/students", json={"name": "Neha", "course": "BCA"}))
show("PUT", requests.put(f"{BASE}/students/1", json={"course": "M.Tech"}))
show("DELETE", requests.delete(f"{BASE}/students/2"))
show("GET missing", requests.get(f"{BASE}/students/99"))
show("Query string", requests.get(f"{BASE}/inspect", params={"q": "flask", "page": 2}))
