// P-1: Node.js and Express environment
const express = require("express");

const app = express();
const PORT = process.env.PORT || 3000;

// Built-in middleware: parse JSON bodies
app.use(express.json());

// Custom middleware: log every request
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()}  ${req.method}  ${req.url}`);
  next();
});

// Routes
app.get("/", (req, res) => {
  res.send("<h1>Hello from Node.js + Express</h1><p>Environment is working.</p>");
});

app.get("/about", (req, res) => {
  res.json({
    course: "Backend Development",
    practical: "P-1",
    node: process.version,
    platform: process.platform,
  });
});

app.get("/api/time", (req, res) => {
  res.json({ time: new Date().toISOString() });
});

app.post("/api/echo", (req, res) => {
  res.json({ youSent: req.body });
});

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

app.listen(PORT, () => {
  console.log(`Server running at http://localhost:${PORT}`);
});
