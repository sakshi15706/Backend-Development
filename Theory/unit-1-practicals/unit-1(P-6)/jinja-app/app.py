"""P-6B: Server-side rendering with Flask + Jinja2."""
from datetime import datetime

from flask import Flask, abort, render_template

app = Flask(__name__)

students = [
    {"name": "Aman", "sap": 590010001, "marks": 88},
    {"name": "Riya", "sap": 590010002, "marks": 72},
    {"name": "Neha", "sap": 590010003, "marks": 35},
]


@app.template_filter("grade")
def grade(marks):
    """Custom Jinja2 filter."""
    if marks >= 75:
        return "Distinction"
    return "Pass" if marks >= 40 else "Fail"


@app.context_processor
def inject_now():
    return {"now": datetime.now().strftime("%H:%M:%S")}


@app.route("/")
def index():
    return render_template("index.html", title="Home", user="Student")


@app.route("/students")
def student_list():
    return render_template("students.html", title="Students", students=students)


@app.route("/students/<int:sap>")
def student_detail(sap):
    student = next((s for s in students if s["sap"] == sap), None)
    if student is None:
        abort(404)
    return render_template("student.html", title=student["name"], student=student)


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html", title="Not found"), 404


if __name__ == "__main__":
    app.run(debug=True, port=5001)
