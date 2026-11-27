-- P-3 Part 5: SQL queries (table: students, see models.py)

-- 1. Find all students enrolled after August 2024
SELECT id, name, branch, enrollment_date
FROM students
WHERE enrollment_date >= '2024-09-01'
ORDER BY enrollment_date;

-- 2. Count students in each branch
SELECT branch, COUNT(*) AS student_count
FROM students
GROUP BY branch
ORDER BY student_count DESC;

-- 3. Find students who are enrolled in more than 3 courses
--    Uses the junction table enrollments(student_id, course_id) from Unit 2 P-2 / P-6.
SELECT s.id, s.name, COUNT(e.course_id) AS course_count
FROM students s
JOIN enrollments e ON e.student_id = s.id
GROUP BY s.id, s.name
HAVING COUNT(e.course_id) > 3;
