// Program 3: Find documents (Read): filters, operators, projection, sort, limit, skip
// Run:  node 3_find.js

const { withDb, seed, title } = require("./db");

// Print a list of students in one line each
const show = (list) => list.forEach((s) => console.log("  ", s.roll, s.name, s.course, s.marks, s.city));

withDb(async (db) => {
  const students = await seed(db);               // resets to 8 sample students
  console.log("Sample data ready:", await students.countDocuments(), "students");

  title("1. find() with no filter: all documents");
  show(await students.find().toArray());

  title("2. findOne(): the first match");
  console.log(await students.findOne({ roll: 103 }));

  title("3. Equality filter: course is IT");
  show(await students.find({ course: "IT" }).toArray());

  title("4. Comparison operators: $gt, $gte, $lt, $lte, $ne");
  console.log("marks > 80:");               show(await students.find({ marks: { $gt: 80 } }).toArray());
  console.log("marks between 60 and 80:");  show(await students.find({ marks: { $gte: 60, $lte: 80 } }).toArray());
  console.log("course not CSE:");           show(await students.find({ course: { $ne: "CSE" } }).toArray());

  title("5. $in: value is in a list");
  show(await students.find({ city: { $in: ["Delhi", "Noida"] } }).toArray());

  title("6. Logical operators: $and, $or");
  console.log("CSE and marks >= 90:");
  show(await students.find({ $and: [{ course: "CSE" }, { marks: { $gte: 90 } }] }).toArray());
  console.log("ECE or marks < 60:");
  show(await students.find({ $or: [{ course: "ECE" }, { marks: { $lt: 60 } }] }).toArray());

  title("7. Regular expression: name starts with S");
  show(await students.find({ name: /^S/ }).toArray());

  title("8. Arrays: students who know 'node' / have no skills");
  show(await students.find({ skills: "node" }).toArray());
  console.log("skills array empty:");
  show(await students.find({ skills: { $size: 0 } }).toArray());

  title("9. $exists: documents that have a field");
  console.log("students with a 'skills' field:", await students.countDocuments({ skills: { $exists: true } }));

  title("10. Projection: choose the fields to return");
  console.log(await students.find({ roll: { $lte: 102 } }).project({ name: 1, marks: 1, _id: 0 }).toArray());

  title("11. sort(): highest marks first");
  show(await students.find().sort({ marks: -1 }).toArray());

  title("12. limit(): top 3 students");
  show(await students.find().sort({ marks: -1 }).limit(3).toArray());

  title("13. skip() + limit(): pagination (2 per page, page 2)");
  const pageSize = 2, page = 2;
  show(await students.find().sort({ roll: 1 }).skip((page - 1) * pageSize).limit(pageSize).toArray());

  title("14. Counting and distinct values");
  console.log("countDocuments (CSE):", await students.countDocuments({ course: "CSE" }));
  console.log("estimatedDocumentCount:", await students.estimatedDocumentCount());
  console.log("distinct courses:", await students.distinct("course"));
  console.log("distinct cities :", await students.distinct("city"));

  title("15. Looping over a cursor");
  const cursor = students.find({ course: "ECE" });
  for await (const s of cursor) {
    console.log("  cursor ->", s.name);
  }
});
