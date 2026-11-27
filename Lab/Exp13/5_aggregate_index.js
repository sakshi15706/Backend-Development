// Program 5: Aggregation and indexes
// Run:  node 5_aggregate_index.js

const { withDb, seed, title } = require("./db");

withDb(async (db) => {
  const students = await seed(db);

  title("1. $group: statistics for every course");
  const byCourse = await students.aggregate([
    { $group: { _id: "$course", students: { $sum: 1 }, average: { $avg: "$marks" }, highest: { $max: "$marks" }, lowest: { $min: "$marks" } } },
    { $sort: { _id: 1 } }
  ]).toArray();
  byCourse.forEach((c) =>
    console.log("  ", c._id, "| students:", c.students, "| avg:", c.average.toFixed(2), "| max:", c.highest, "| min:", c.lowest));

  title("2. $match + $sort + $limit: top 3 students of CSE and IT");
  const top = await students.aggregate([
    { $match: { course: { $in: ["CSE", "IT"] } } },
    { $sort: { marks: -1 } },
    { $limit: 3 },
    { $project: { _id: 0, name: 1, course: 1, marks: 1 } }
  ]).toArray();
  console.log(top);

  title("3. $project with a calculated field (grade)");
  const graded = await students.aggregate([
    { $project: {
        _id: 0, name: 1, marks: 1,
        grade: { $switch: { branches: [
          { case: { $gte: ["$marks", 85] }, then: "A" },
          { case: { $gte: ["$marks", 70] }, then: "B" },
          { case: { $gte: ["$marks", 50] }, then: "C" }
        ], default: "F" } }
    } },
    { $sort: { marks: -1 } }
  ]).toArray();
  graded.forEach((s) => console.log("  ", s.name.padEnd(7), s.marks, s.grade));

  title("4. $unwind: count how many students know each skill");
  const skills = await students.aggregate([
    { $unwind: "$skills" },
    { $group: { _id: "$skills", count: { $sum: 1 } } },
    { $sort: { count: -1, _id: 1 } }
  ]).toArray();
  console.log(skills.map((s) => s._id + "=" + s.count).join(", "));

  title("5. $group by city with a list of names ($push)");
  const cities = await students.aggregate([
    { $group: { _id: "$city", names: { $push: "$name" }, total: { $sum: "$marks" } } },
    { $sort: { _id: 1 } }
  ]).toArray();
  cities.forEach((c) => console.log("  ", c._id, "->", c.names.join(", "), "| total marks:", c.total));

  title("6. Whole-collection summary ($group with _id null)");
  const [summary] = await students.aggregate([
    { $group: { _id: null, count: { $sum: 1 }, average: { $avg: "$marks" } } }
  ]).toArray();
  console.log("students:", summary.count, "| class average:", summary.average.toFixed(2));

  title("7. Indexes: createIndex");
  console.log("Index created:", await students.createIndex({ roll: 1 }, { unique: true }));
  console.log("Index created:", await students.createIndex({ course: 1, marks: -1 }));
  console.log("Indexes on the collection:");
  (await students.indexes()).forEach((i) => console.log("  -", i.name, JSON.stringify(i.key), i.unique ? "(unique)" : ""));

  title("8. A unique index rejects duplicates");
  try {
    await students.insertOne({ name: "Duplicate", roll: 101, course: "CSE", marks: 10 });
  } catch (err) {
    console.log("Error code:", err.code, "(E11000 duplicate key)");
  }
  console.log("Documents still:", await students.countDocuments());

  title("9. Is the index used? (explain)");
  const plan = await students.find({ roll: 103 }).explain("queryPlanner");
  const stage = JSON.stringify(plan.queryPlanner.winningPlan);
  console.log(stage.includes("IXSCAN") ? "Query uses the index (IXSCAN)" : "Collection scan (COLLSCAN)");

  title("10. dropIndex");
  await students.dropIndex("course_1_marks_-1");
  console.log("Dropped index course_1_marks_-1");
});
