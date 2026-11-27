# Programs using MongoDB Database with Node.js

**MongoDB CRUD, Queries, Aggregation, Indexes and a REST API with the Node.js Driver**

*Lab Experiment 13 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

MongoDB is a NoSQL database that stores data as flexible JSON-like documents inside collections, instead of rows inside tables. Node.js talks to MongoDB through the official `mongodb` driver. This experiment contains six Node.js programs that connect to MongoDB, perform all CRUD operations, run queries and aggregations, create indexes, and finally expose the data through a REST API built with Express.

Objectives:

- Connect to a MongoDB server from Node.js with `MongoClient` and close the connection properly.
- Insert documents with `insertOne` and `insertMany`.
- Read documents with filters, operators, projection, sort, limit and skip.
- Update and delete documents with update operators (`$set`, `$inc`, `$push`, `$pull`, `$unset`) and `upsert`.
- Use the aggregation pipeline and indexes.
- Build a REST API (GET, POST, PUT, DELETE) with validation and error handling on top of MongoDB.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Runtime | Node.js (v18 or newer) | Runs the programs |
| Database | MongoDB Community Server | Stores the documents |
| Driver | `mongodb` npm package (v6) | Connects Node.js to MongoDB |
| Web framework | Express 4 | REST API in Program 6 |
| Tools | VS Code, MongoDB Compass, Postman / browser | Writing code, viewing data, testing the API |

## 3. How to Run

1. Install Node.js and MongoDB Community Server. Make sure the MongoDB service is **running** (default address `mongodb://127.0.0.1:27017`).
2. Open the `Exp13` folder in VS Code and open the terminal.
3. Run `npm install` once.
4. Run any program, for example `node 3_find.js` (or `npm run find`).
5. For Program 6 run `node 6_student_api.js` and open `http://localhost:3000/students` in the browser.
6. To use another MongoDB address (for example Atlas), set the variable first: `set MONGO_URL=your-url` (Windows) or `export MONGO_URL=your-url` (Mac/Linux).
7. Open **MongoDB Compass**, connect to the same URL and look at the database `exp13_lab` to see the data.

## 4. Project Structure

```
Exp13/
├── db.js                   shared connection helper + sample data
├── 1_connect.js            connect, ping, list databases
├── 2_insert.js             insertOne, insertMany, duplicate error
├── 3_find.js               find, operators, projection, sort, limit, skip
├── 4_update_delete.js      updateOne/Many, upsert, replace, delete
├── 5_aggregate_index.js    aggregation pipeline, indexes
├── 6_student_api.js        Express REST API with MongoDB
├── package.json
└── Report.md
```

## 5. Programs

### Program 1: Connect to MongoDB (`1_connect.js`)

**Aim:** Connect to the server, check that it answers, and list databases and collections.

| Method | Purpose |
|---|---|
| `new MongoClient(url)` | Creates the client |
| `client.connect()` | Opens the connection |
| `db.command({ ping: 1 })` | Checks that the server is alive |
| `admin().listDatabases()` | Lists all databases |
| `db.listCollections()` | Lists collections of the database |
| `client.close()` | Closes the connection (done in `finally` in `db.js`) |

**Expected result:** The program prints `ping result: { ok: 1 }`, the MongoDB version, the list of databases and the number of documents in `students`.

*Output:* *(screenshot)*

### Program 2: Insert documents (`2_insert.js`)

**Aim:** Create documents.

| Method | Purpose |
|---|---|
| `insertOne(doc)` | Adds one document, returns `insertedId` |
| `insertMany([docs])` | Adds many documents, returns `insertedCount` |

The program also shows: a custom `_id`, the duplicate key error (code `11000`), and that documents of one collection can have different fields (flexible schema, nested objects, arrays).

**Expected result:** Insert counts and ids are printed, the duplicate `_id` gives error code 11000, and 6 documents are listed at the end.

*Output:* *(screenshot)*

### Program 3: Find documents (`3_find.js`)

**Aim:** Read data with queries.

| Feature | Example |
|---|---|
| Equality | `{ course: "IT" }` |
| Comparison | `$gt`, `$gte`, `$lt`, `$lte`, `$ne` |
| List | `$in` |
| Logical | `$and`, `$or` |
| Pattern | `/^S/` |
| Array | `{ skills: "node" }`, `$size` |
| Field check | `$exists` |
| Projection | `.project({ name: 1, marks: 1, _id: 0 })` |
| Order and pages | `.sort()`, `.limit()`, `.skip()` |
| Counting | `countDocuments`, `distinct` |

**Expected result:** Each numbered step prints its matching students, for example `marks > 80` gives Rahul, Priya and Sneha.

*Output:* *(screenshot)*

### Program 4: Update and delete (`4_update_delete.js`)

**Aim:** Change and remove documents.

| Method / operator | Purpose |
|---|---|
| `updateOne`, `updateMany` | Update one or many documents |
| `$set`, `$unset`, `$inc` | Set, remove a field, add to a number |
| `$push`, `$addToSet`, `$pull` | Add, add without duplicate, remove from an array |
| `{ upsert: true }` | Insert if no document matches |
| `replaceOne` | Replace the whole document |
| `findOneAndUpdate` | Update and return the document |
| `deleteOne`, `deleteMany` | Remove documents |

**Expected result:** `matchedCount`, `modifiedCount` and `deletedCount` are printed for each step. The upsert reports `upsertedCount: 1` the first time and `0` the second time. `deleteMany({ marks: { $lt: 50 } })` removes Vikas (41 marks).

*Output:* *(screenshot)*

### Program 5: Aggregation and indexes (`5_aggregate_index.js`)

**Aim:** Process data inside the database and speed up queries.

| Stage / method | Purpose |
|---|---|
| `$match` | Filter documents |
| `$group` | Group and calculate (`$sum`, `$avg`, `$max`, `$min`, `$push`) |
| `$sort`, `$limit` | Order and cut the result |
| `$project` | Choose or calculate fields (`$switch` for grade) |
| `$unwind` | Split an array into separate documents |
| `createIndex` | Creates a normal or unique index |
| `explain()` | Shows whether the index is used (`IXSCAN`) |
| `dropIndex` | Removes an index |

**Expected result:** Average marks per course, top students, grades, skill counts, a unique index error on duplicate `roll` (code 11000), and `Query uses the index (IXSCAN)`.

*Output:* *(screenshot)*

### Program 6: Student REST API (`6_student_api.js`)

**Aim:** Build a complete REST API on MongoDB with Express.

| Method | URL | Action |
|---|---|---|
| GET | `/students` | List with filters, sorting and pages |
| GET | `/students/:id` | One student |
| POST | `/students` | Add a student |
| PUT | `/students/:id` | Update a student |
| DELETE | `/students/:id` | Delete a student |
| GET | `/stats` | Average marks per course (aggregation) |

Important points of the code:

- The server starts listening only after the database is connected.
- `ObjectId.isValid()` is checked so a bad id gives `400`, not a crash.
- The body is validated, and only allowed fields are saved (`pick`).
- `createdAt` and `updatedAt` are set by the server.
- A unique index on `roll` gives `409 Conflict` for duplicates.
- Status codes: `201` created, `400` bad data, `404` not found, `409` duplicate, `500` server error.

Test with the browser or curl:

```
curl http://localhost:3000/students
curl -X POST http://localhost:3000/students -H "Content-Type: application/json" -d "{\"name\":\"Ravi\",\"roll\":109,\"course\":\"IT\",\"marks\":80}"
curl -X PUT http://localhost:3000/students/<id> -H "Content-Type: application/json" -d "{\"marks\":90}"
curl -X DELETE http://localhost:3000/students/<id>
```

**Expected result:** The POST returns status 201 with the new `_id`; a second POST with the same roll returns 409; GET with a wrong id such as `/students/abc` returns 400.

*Output:* *(screenshot)*

## 6. Summary of Programs

| No. | File | Topic | Main methods |
|---|---|---|---|
| 1 | `1_connect.js` | Connection | `MongoClient`, `connect`, `ping`, `close` |
| 2 | `2_insert.js` | Create | `insertOne`, `insertMany` |
| 3 | `3_find.js` | Read | `find`, `findOne`, operators, `sort`, `limit`, `skip` |
| 4 | `4_update_delete.js` | Update, Delete | `updateOne/Many`, `replaceOne`, `deleteOne/Many` |
| 5 | `5_aggregate_index.js` | Aggregation, Index | `aggregate`, `createIndex`, `explain` |
| 6 | `6_student_api.js` | REST API | Express + all CRUD |

## 7. Problems Faced and Solutions

*(Keep only the problems you actually faced.)*

| Problem | Reason | Solution |
|---|---|---|
| `ECONNREFUSED 127.0.0.1:27017` / server selection timed out | MongoDB service is not running | Start the MongoDB service (Services on Windows, `brew services start mongodb-community` on Mac) |
| `Cannot find module 'mongodb'` | Packages not installed | Run `npm install` in the `Exp13` folder |
| Program hangs after printing | Connection was not closed | Call `client.close()` (done in `db.js`) |
| `E11000 duplicate key error` | Same `_id` or unique field inserted twice | Catch the error, check `err.code === 11000` |
| `/students/abc` crashed the server | Invalid ObjectId string | Check `ObjectId.isValid()` first and return 400 |
| Search by id returned nothing | `_id` is an `ObjectId`, not a string | Use `new ObjectId(id)` in the filter |
| Server received an empty `req.body` | JSON parser missing | Add `app.use(express.json())` before the routes |

## 8. Testing

- All files were checked for syntax errors with `node --check`.
- The programs need a running MongoDB server. They were **not run against a live MongoDB in the authoring environment**, so run each program once on your machine and paste your own screenshots under every `*Output:*` line.
- Suggested checks: run each program twice (the sample data is reset every time, so the output is the same); in Program 6 test valid data, missing fields, wrong marks (for example 150), a duplicate roll and an invalid id.

## 9. Limitations and Future Scope

- No login or authentication in the API.
- No automated tests (Jest and Supertest can be added).
- Mongoose with schemas can be used for stricter validation.
- MongoDB Atlas (cloud) can replace the local server, and transactions and text search can be added.

## 10. Conclusion

The experiment showed how Node.js works with MongoDB: connecting with `MongoClient`, performing CRUD, querying with operators, summarising data with aggregation, speeding up queries with indexes, and exposing the data through a validated REST API. Documents, collections and `ObjectId` make MongoDB flexible, and the same driver methods are used in real back-end projects.
