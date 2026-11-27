// db.js: shared helpers used by every program in this experiment.
//
// - connection URL, database name and sample data are kept in one place
// - withDb() opens ONE MongoClient, runs the program, and always closes it
// - seed() empties the "students" collection and inserts the sample students,
//   so each program can be run again and again with the same starting data

const { MongoClient, ObjectId } = require("mongodb");

// Use the URL given by the examiner, or the default local one
const MONGO_URL = process.env.MONGO_URL || "mongodb://127.0.0.1:27017";
const DB_NAME = "exp13_lab";

async function withDb(work) {
  // serverSelectionTimeoutMS: give up after 4 seconds if MongoDB is not running
  const client = new MongoClient(MONGO_URL, { serverSelectionTimeoutMS: 4000 });
  try {
    await client.connect();
    const db = client.db(DB_NAME);
    await work(db, client);
  } catch (err) {
    console.error("\nError:", err.message);
    if (/ECONNREFUSED|server selection|timed out/i.test(err.message)) {
      console.error("MongoDB is not reachable at " + MONGO_URL + ". Start the MongoDB service and try again.");
    }
    process.exitCode = 1;
  } finally {
    await client.close();                      // always release the connection
  }
}

const sampleStudents = [
  { name: "Rahul",  roll: 101, course: "CSE", marks: 85, city: "Meerut", skills: ["html", "css"] },
  { name: "Priya",  roll: 102, course: "CSE", marks: 92, city: "Delhi",  skills: ["js", "node"] },
  { name: "Amit",   roll: 103, course: "IT",  marks: 74, city: "Meerut", skills: ["python"] },
  { name: "Neha",   roll: 104, course: "IT",  marks: 66, city: "Noida",  skills: ["java", "sql"] },
  { name: "Karan",  roll: 105, course: "ECE", marks: 58, city: "Delhi",  skills: ["c"] },
  { name: "Sneha",  roll: 106, course: "CSE", marks: 88, city: "Noida",  skills: ["js", "react", "node"] },
  { name: "Vikas",  roll: 107, course: "ECE", marks: 41, city: "Meerut", skills: [] },
  { name: "Anjali", roll: 108, course: "IT",  marks: 79, city: "Delhi",  skills: ["python", "sql"] }
];

// Reset the collection to the sample data and return it
async function seed(db) {
  const students = db.collection("students");
  await students.deleteMany({});
  await students.dropIndexes().catch(() => {});          // remove old indexes (ignore if none)
  await students.insertMany(sampleStudents.map((s) => ({ ...s, createdAt: new Date() })));
  return students;
}

// Print a title line for each step of a program
function title(text) {
  console.log("\n=== " + text + " ===");
}

module.exports = { withDb, seed, title, ObjectId, MONGO_URL, DB_NAME };
