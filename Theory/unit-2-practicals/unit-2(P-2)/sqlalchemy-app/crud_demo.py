"""P-2 Part 3: CRUD with SQLAlchemy.

    python crud_demo.py
"""
from datetime import date

from models import Course, Department, Enrollment, Session, Student, engine, Base, init_db

# start from a clean database every run so the demo is repeatable
Base.metadata.drop_all(engine)
init_db()
session = Session()

# Reference data
cse = Department(name="Computer Science", building="Block A")
ece = Department(name="Electronics", building="Block B")
session.add_all([cse, ece])
session.add_all([
    Course(id="CS301", title="Database Systems", credits=4, department=cse),
    Course(id="CS302", title="Operating Systems", credits=4, department=cse),
])
session.commit()

print("\n--- CREATE: a new student with a department assignment ---")
aarav = Student(name="Aarav", email="aarav@upes.ac.in", branch="CSE",
                enrollment_date=date(2024, 8, 1), department=cse)
session.add(aarav)
session.add_all([
    Student(name="Diya", email="diya@upes.ac.in", branch="ECE", department=ece),
    Student(name="Priya", email="priya@upes.ac.in", branch="CSE", department=cse),
])
session.commit()
print(f"Created {aarav.name} (id={aarav.id}) in department '{aarav.department.name}'")

for course_id in ("CS301", "CS302"):
    course = session.get(Course, course_id)  # load first, then build the Enrollment
    session.add(Enrollment(student=aarav, course=course, semester="Fall 2024"))
session.commit()

print("\n--- READ: all students in a specific branch ---")
branch = "CSE"
for s in session.query(Student).filter(Student.branch == branch).order_by(Student.name):
    print(f"  {s.id}: {s.name} ({s.department.name})")

print("\n--- READ: department -> students (back_populates) ---")
print("  CS department students:", [s.name for s in cse.students])

print("\n--- UPDATE: change a student's branch ---")
aarav.branch = "ECE"
session.commit()
print(f"  {aarav.name} is now in {session.get(Student, aarav.id).branch}")

print("\n--- DELETE: delete a student and verify cascade behaviour ---")
before = session.query(Enrollment).filter_by(student_id=aarav.id).count()
print(f"  enrollments for {aarav.name} before delete: {before}")
student_id = aarav.id
session.delete(aarav)
session.commit()
after = session.query(Enrollment).filter_by(student_id=student_id).count()
print(f"  enrollments for student {student_id} after delete: {after}  (cascade removed them)")
print(f"  courses still present: {session.query(Course).count()}  (cascade does NOT touch courses)")
assert before == 2 and after == 0
print("\nAll CRUD steps completed.")
