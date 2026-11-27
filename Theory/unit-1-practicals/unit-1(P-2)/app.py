"""P-2: HTTP requests with a Flask API (GET, POST, PUT, DELETE)."""
from flask import Flask, jsonify, request

app = Flask(__name__)

students = [
    {"id": 1, "name": "Aman", "course": "B.Tech CSE"},
    {"id": 2, "name": "Riya", "course": "B.Tech CSE"},
]


def find(student_id):
    return next((s for s in students if s["id"] == student_id), None)


@app.route("/")
def home():
    return jsonify(message="Flask HTTP demo is running")


# GET all
@app.route("/students", methods=["GET"])
def get_students():
    return jsonify(students)


# GET one (+ query string: /students?course=B.Tech CSE handled below)
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    student = find(student_id)
    if not student:
        return jsonify(error="Student not found"), 404
    return jsonify(student)


# POST create
@app.route("/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True) or {}
    if "name" not in data:
        return jsonify(error="'name' is required"), 400
    new = {
        "id": max((s["id"] for s in students), default=0) + 1,
        "name": data["name"],
        "course": data.get("course", "Unknown"),
    }
    students.append(new)
    return jsonify(new), 201


# PUT update
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    student = find(student_id)
    if not student:
        return jsonify(error="Student not found"), 404
    data = request.get_json(silent=True) or {}
    student.update({k: v for k, v in data.items() if k in ("name", "course")})
    return jsonify(student)


# DELETE
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    student = find(student_id)
    if not student:
        return jsonify(error="Student not found"), 404
    students.remove(student)
    return jsonify(message="Deleted", id=student_id)


# Inspect request details (headers, method, query string)
@app.route("/inspect")
def inspect_request():
    return jsonify(
        method=request.method,
        path=request.path,
        query=request.args.to_dict(),
        user_agent=request.headers.get("User-Agent"),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
