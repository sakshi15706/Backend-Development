// Program 1: Connect to MongoDB from Node.js
// Run:  node 1_connect.js

const { withDb, title, MONGO_URL, DB_NAME } = require("./db");

withDb(async (db, client) => {
  console.log("Connected to MongoDB at", MONGO_URL);
  console.log("Using database       :", db.databaseName);

  title("1. Ping the server");
  const ping = await db.command({ ping: 1 });
  console.log("ping result:", ping);                    // { ok: 1 } means the server answered

  title("2. Server information");
  const info = await db.admin().serverInfo();
  console.log("MongoDB version:", info.version);

  title("3. Databases on the server");
  const list = await client.db().admin().listDatabases();
  list.databases.forEach((d) => console.log("  -", d.name));

  title("4. Collections in " + DB_NAME);
  const collections = await db.listCollections().toArray();
  if (collections.length === 0) {
    console.log("  (none yet: a database and collection are created when the first document is inserted)");
  }
  collections.forEach((c) => console.log("  -", c.name));

  title("5. Get a collection object");
  const students = db.collection("students");
  console.log("Collection name:", students.collectionName);
  console.log("Documents in it:", await students.countDocuments());
});
