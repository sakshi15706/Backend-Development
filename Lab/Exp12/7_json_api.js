// Program 7: A REST API (JSON) for students using only the http module
// Run:  node 7_json_api.js
//
// GET    /students        list all
// GET    /students/1      one student
// POST   /students        add   (JSON body: {"name":"Ravi","marks":80})
// PUT    /students/1      update (JSON body)
// DELETE /students/1      delete

const http = require("http");

const PORT = 3000;

// Data is kept in memory (it resets when the server restarts)
let students = [
  { id: 1, name: "Rahul", marks: 85 },
  { id: 2, name: "Priya", marks: 92 },
  { id: 3, name: "Amit", marks: 74 }
];
let nextId = 4;

function sendJson(res, status, data) {
  res.writeHead(status, { "Content-Type": "application/json" });
  res.end(JSON.stringify(data, null, 2));
}

// Read the whole request body and give it back as an object
function readBody(req, callback) {
  let body = "";
  req.on("data", (chunk) => { body += chunk; });
  req.on("end", () => {
    try {
      callback(null, body ? JSON.parse(body) : {});
    } catch (e) {
      callback(new Error("Invalid JSON"));
    }
  });
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://" + req.headers.host);
  const parts = url.pathname.split("/").filter(Boolean);   // "/students/2" -> ["students","2"]
  const id = parts[1] ? Number(parts[1]) : null;
  console.log(req.method + " " + url.pathname);

  if (parts[0] !== "students") {
    sendJson(res, 404, { error: "Use /students" });
    return;
  }

  // GET /students  (supports ?minMarks=80)
  if (req.method === "GET" && id === null) {
    const min = Number(url.searchParams.get("minMarks") || 0);
    sendJson(res, 200, students.filter((s) => s.marks >= min));

  // GET /students/:id
  } else if (req.method === "GET") {
    const s = students.find((x) => x.id === id);
    s ? sendJson(res, 200, s) : sendJson(res, 404, { error: "Student not found" });

  // POST /students
  } else if (req.method === "POST" && id === null) {
    readBody(req, (err, data) => {
      if (err) { return sendJson(res, 400, { error: err.message }); }
      if (!data.name || typeof data.marks !== "number") {
        return sendJson(res, 400, { error: "name and numeric marks are required" });
      }
      const student = { id: nextId++, name: data.name, marks: data.marks };
      students.push(student);
      sendJson(res, 201, student);
    });

  // PUT /students/:id
  } else if (req.method === "PUT" && id !== null) {
    readBody(req, (err, data) => {
      if (err) { return sendJson(res, 400, { error: err.message }); }
      const s = students.find((x) => x.id === id);
      if (!s) { return sendJson(res, 404, { error: "Student not found" }); }
      if (data.name) { s.name = data.name; }
      if (typeof data.marks === "number") { s.marks = data.marks; }
      sendJson(res, 200, s);
    });

  // DELETE /students/:id
  } else if (req.method === "DELETE" && id !== null) {
    const before = students.length;
    students = students.filter((x) => x.id !== id);
    students.length < before
      ? sendJson(res, 200, { message: "Deleted student " + id })
      : sendJson(res, 404, { error: "Student not found" });

  } else {
    sendJson(res, 405, { error: "Method not allowed" });
  }
});

server.listen(PORT, () => console.log("API running at http://localhost:" + PORT + "/students"));
