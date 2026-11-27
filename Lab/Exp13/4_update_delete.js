// Program 4: Update and delete documents
// Run:  node 4_update_delete.js

const { withDb, seed, title } = require("./db");

withDb(async (db) => {
  const students = await seed(db);

  title("1. updateOne + $set: change a field");
  let r = await students.updateOne({ roll: 101 }, { $set: { city: "Delhi", marks: 87 } });
  console.log("matchedCount :", r.matchedCount, "| modifiedCount:", r.modifiedCount);
  console.log(await students.findOne({ roll: 101 }, { projection: { _id: 0, name: 1, city: 1, marks: 1 } }));

  title("2. $inc: increase a number");
  await students.updateOne({ roll: 107 }, { $inc: { marks: 10 } });
  console.log("Vikas now has", (await students.findOne({ roll: 107 })).marks, "marks (41 + 10)");

  title("3. updateMany: change many documents at once");
  r = await students.updateMany({ course: "IT" }, { $inc: { marks: 5 } });
  console.log("IT students matched:", r.matchedCount, "| modified:", r.modifiedCount);
  console.log((await students.find({ course: "IT" }).toArray()).map((s) => s.name + "=" + s.marks).join(", "));

  title("4. Array operators: $push, $addToSet, $pull");
  await students.updateOne({ roll: 101 }, { $push: { skills: "js" } });
  console.log("after $push 'js'        :", (await students.findOne({ roll: 101 })).skills);
  await students.updateOne({ roll: 101 }, { $addToSet: { skills: "js" } });
  console.log("after $addToSet 'js'    :", (await students.findOne({ roll: 101 })).skills, "(already there, so no duplicate)");
  await students.updateOne({ roll: 101 }, { $pull: { skills: "css" } });
  console.log("after $pull 'css'       :", (await students.findOne({ roll: 101 })).skills);

  title("5. $unset: remove a field");
  await students.updateOne({ roll: 102 }, { $unset: { city: "" } });
  console.log("Priya has a city field?", "city" in (await students.findOne({ roll: 102 })));

  title("6. upsert: update if it exists, otherwise insert");
  r = await students.updateOne({ roll: 200 }, { $set: { name: "Mohit", course: "CSE", marks: 70 } }, { upsert: true });
  console.log("matchedCount:", r.matchedCount, "| upsertedCount:", r.upsertedCount, "| upsertedId:", r.upsertedId);
  r = await students.updateOne({ roll: 200 }, { $set: { marks: 75 } }, { upsert: true });
  console.log("second time -> matchedCount:", r.matchedCount, "| upsertedCount:", r.upsertedCount);

  title("7. replaceOne: replace the whole document (the _id stays)");
  await students.replaceOne({ roll: 200 }, { roll: 200, name: "Mohit Sharma", course: "IT", marks: 80 });
  console.log(await students.findOne({ roll: 200 }, { projection: { _id: 0 } }));

  title("8. findOneAndUpdate: update and get the document back");
  const updated = await students.findOneAndUpdate(
    { roll: 105 },
    { $set: { marks: 60 } },
    { returnDocument: "after" }                    // return the NEW version
  );
  console.log("Updated document:", updated.name, updated.marks);

  title("9. deleteOne");
  r = await students.deleteOne({ roll: 200 });
  console.log("deletedCount:", r.deletedCount);

  title("10. deleteMany: remove every student with marks below 50");
  const before = await students.countDocuments();
  r = await students.deleteMany({ marks: { $lt: 50 } });
  console.log("deletedCount:", r.deletedCount, "| documents:", before, "->", await students.countDocuments());

  title("11. Deleting something that does not exist");
  r = await students.deleteOne({ roll: 9999 });
  console.log("deletedCount:", r.deletedCount, "(no error, simply 0)");

  title("12. Final collection");
  (await students.find().sort({ roll: 1 }).toArray()).forEach((s) => console.log("  ", s.roll, s.name, s.course, s.marks));
});
