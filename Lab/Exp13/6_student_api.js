// Program 6: A REST API for students, stored in MongoDB (Express + MongoDB driver)
// Run:  npm install      then      node 6_student_api.js
//
//   GET    /students                 list (filters: ?course=CSE&minMarks=70&sort=marks&order=desc&page=1&limit=5)
//   GET    /students/:id             one student
//   POST   /students                 add     {"name":"Ravi","roll":109,"course":"IT","marks":80}
//   PUT    /students/:id             update  {"marks":90}
//   DELETE /students/:id             delete
//   GET    /stats                    average marks per course

const express = require("express");
const { MongoClient, ObjectId } = require("mongodb");

const PORT = process.env.PORT || 3000;
const MONGO_URL = process.env.MONGO_URL || "mongodb://127.0.0.1:27017";

const app = express();
app.use(express.json());

let students;                                       // set once the database is connected

// ---------- helpers ----------
const COURSES = ["CSE", "IT", "ECE"];

// Check the body of a request and return a list of error messages
function validate(body, requireAll) {
  const errors = [];
  const has = (k) => body[k] !== undefined;

  if (requireAll || has("name")) {
    if (typeof body.name !== "string" || body.name.trim().length < 2) errors.push("name must have at least 2 characters");
  }
  if (requireAll || has("roll")) {
    if (!Number.isInteger(body.roll) || body.roll <= 0) errors.push("roll must be a positive whole number");
  }
  if (requireAll || has("course")) {
    if (!COURSES.includes(body.course)) errors.push("course must be one of " + COURSES.join(", "));
  }
  if (requireAll || has("marks")) {
    if (typeof body.marks !== "number" || body.marks < 0 || body.marks > 100) errors.push("marks must be a number from 0 to 100");
  }
  return errors;
}

// Only these fields may be saved (ignores anything else sent by the user)
function pick(body) {
  const out = {};
  ["name", "roll", "course", "marks", "city"].forEach((k) => { if (body[k] !== undefined) out[k] = body[k]; });
  if (out.name) out.name = out.name.trim();
  return out;
}

function badId(res) {
  return res.status(400).json({ error: "Invalid id" });
}

// ---------- routes ----------
app.get("/students", async (req, res, next) => {
  try {
    const filter = {};
    if (req.query.course) filter.course = req.query.course;
    if (req.query.minMarks) filter.marks = { $gte: Number(req.query.minMarks) };

    const sortField = ["name", "roll", "marks"].includes(req.query.sort) ? req.query.sort : "roll";
    const sortOrder = req.query.order === "desc" ? -1 : 1;
    const limit = Math.min(Math.max(parseInt(req.query.limit) || 10, 1), 50);
    const page = Math.max(parseInt(req.query.page) || 1, 1);

    const total = await students.countDocuments(filter);
    const data = await students.find(filter)
      .sort({ [sortField]: sortOrder })
      .skip((page - 1) * limit)
      .limit(limit)
      .toArray();

    res.json({ total, page, limit, data });
  } catch (err) { next(err); }
});

app.get("/stats", async (req, res, next) => {
  try {
    const stats = await students.aggregate([
      { $group: { _id: "$course", students: { $sum: 1 }, average: { $avg: "$marks" } } },
      { $sort: { _id: 1 } }
    ]).toArray();
    res.json(stats);
  } catch (err) { next(err); }
});

app.get("/students/:id", async (req, res, next) => {
  try {
    if (!ObjectId.isValid(req.params.id)) return badId(res);
    const student = await students.findOne({ _id: new ObjectId(req.params.id) });
    if (!student) return res.status(404).json({ error: "Student not found" });
    res.json(student);
  } catch (err) { next(err); }
});

app.post("/students", async (req, res, next) => {
  try {
    const errors = validate(req.body, true);
    if (errors.length) return res.status(400).json({ errors });

    const doc = { ...pick(req.body), createdAt: new Date() };    // date is made by the server
    const result = await students.insertOne(doc);
    res.status(201).json({ _id: result.insertedId, ...doc });
  } catch (err) { next(err); }
});

app.put("/students/:id", async (req, res, next) => {
  try {
    if (!ObjectId.isValid(req.params.id)) return badId(res);
    const errors = validate(req.body, false);
    if (errors.length) return res.status(400).json({ errors });

    const changes = pick(req.body);
    if (Object.keys(changes).length === 0) return res.status(400).json({ error: "Nothing to update" });

    const updated = await students.findOneAndUpdate(
      { _id: new ObjectId(req.params.id) },
      { $set: { ...changes, updatedAt: new Date() } },
      { returnDocument: "after" }
    );
    if (!updated) return res.status(404).json({ error: "Student not found" });
    res.json(updated);
  } catch (err) { next(err); }
});

app.delete("/students/:id", async (req, res, next) => {
  try {
    if (!ObjectId.isValid(req.params.id)) return badId(res);
    const result = await students.deleteOne({ _id: new ObjectId(req.params.id) });
    if (result.deletedCount === 0) return res.status(404).json({ error: "Student not found" });
    res.json({ message: "Deleted", id: req.params.id });
  } catch (err) { next(err); }
});

// Unknown URL
app.use((req, res) => res.status(404).json({ error: "Not found" }));

// Error handler: invalid JSON body, duplicate roll number, anything unexpected
app.use((err, req, res, next) => {
  if (err.type === "entity.parse.failed") return res.status(400).json({ error: "Invalid JSON" });
  if (err.code === 11000) return res.status(409).json({ error: "A student with this roll number already exists" });
  console.error(err);
  res.status(500).json({ error: "Server error" });
});

// ---------- start: connect to MongoDB first, then listen ----------
async function start() {
  const client = new MongoClient(MONGO_URL, { serverSelectionTimeoutMS: 4000 });
  await client.connect();
  students = client.db("exp13_lab").collection("students_api");
  await students.createIndex({ roll: 1 }, { unique: true });     // no two students with the same roll
  console.log("Connected to MongoDB");

  app.listen(PORT, () => console.log("API running at http://localhost:" + PORT + "/students"));
}

start().catch((err) => {
  console.error("Could not start:", err.message);
  process.exit(1);
});
