// P-6A: Server-side rendering with EJS
const express = require("express");
const path = require("path");

const app = express();
const PORT = process.env.PORT || 3000;

app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "views"));
app.use(express.static(path.join(__dirname, "public")));

const students = [
  { name: "Aman", sap: 590010001, marks: 88 },
  { name: "Riya", sap: 590010002, marks: 72 },
  { name: "Neha", sap: 590010003, marks: 35 },
];

app.get("/", (req, res) => {
  res.render("index", { title: "Home", user: "Student" });
});

app.get("/students", (req, res) => {
  res.render("students", { title: "Students", students });
});

app.get("/students/:sap", (req, res) => {
  const student = students.find((s) => String(s.sap) === req.params.sap);
  if (!student) return res.status(404).render("404", { title: "Not found" });
  res.render("student", { title: student.name, student });
});

app.use((req, res) => res.status(404).render("404", { title: "Not found" }));

app.listen(PORT, () => console.log(`EJS app running at http://localhost:${PORT}`));
