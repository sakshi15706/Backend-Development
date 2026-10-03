// Program 9: The same ideas using the Express framework
// Run:  npm install      (installs express from package.json)
//       node 9_express_server.js      Open: http://localhost:3000

const express = require("express");
const app = express();
const PORT = 3000;

// Middleware: runs for every request before the routes
app.use((req, res, next) => {
  console.log(req.method + " " + req.url);
  next();                                   // pass control to the next handler
});
app.use(express.json());                    // parse JSON bodies
app.use(express.urlencoded({ extended: true })); // parse form bodies

// Routes
app.get("/", (req, res) => {
  res.send("<h1>Express server</h1><p>Try /hello/Sakshi, /search?q=node or POST /add</p>");
});

// Route parameter: /hello/Sakshi
app.get("/hello/:name", (req, res) => {
  res.send("Hello, " + req.params.name + "!");
});

// Query string: /search?q=node
app.get("/search", (req, res) => {
  res.json({ searchedFor: req.query.q || null });
});

// JSON POST: send {"a": 4, "b": 6}
app.post("/add", (req, res) => {
  const { a, b } = req.body;
  if (typeof a !== "number" || typeof b !== "number") {
    return res.status(400).json({ error: "a and b must be numbers" });
  }
  res.json({ a, b, sum: a + b });
});

// 404 handler (must be last)
app.use((req, res) => {
  res.status(404).send("404 - Not Found");
});

app.listen(PORT, () => console.log("Express server at http://localhost:" + PORT));
