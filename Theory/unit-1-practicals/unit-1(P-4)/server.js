// P-4: Sessions, cookies and query strings
const express = require("express");
const cookieParser = require("cookie-parser");
const session = require("express-session");

const app = express();
const PORT = process.env.PORT || 3000;

app.use(express.urlencoded({ extended: true }));
app.use(cookieParser());
app.use(
  session({
    secret: "change-this-secret-in-real-apps",
    resave: false,
    saveUninitialized: false,
    cookie: { maxAge: 1000 * 60 * 30, httpOnly: true }, // 30 minutes
  })
);

app.get("/", (req, res) => {
  res.send(`
    <h1>Sessions, Cookies &amp; Query Strings</h1>
    <ul>
      <li><a href="/search?q=express&page=2&sort=asc">Query string demo</a></li>
      <li><a href="/set-cookie?name=Aman">Set cookie</a></li>
      <li><a href="/get-cookie">Read cookie</a></li>
      <li><a href="/clear-cookie">Clear cookie</a></li>
      <li><a href="/login">Session login</a></li>
      <li><a href="/profile">Profile (needs login)</a></li>
      <li><a href="/visits">Visit counter (session)</a></li>
    </ul>`);
});

// ---------- Query strings ----------
app.get("/search", (req, res) => {
  const { q = "", page = 1, sort = "asc" } = req.query;
  res.json({ query: q, page: Number(page), sort, allParams: req.query });
});

// ---------- Cookies ----------
app.get("/set-cookie", (req, res) => {
  const name = req.query.name || "Guest";
  res.cookie("username", name, { maxAge: 60 * 1000, httpOnly: true });
  res.send(`Cookie 'username=${name}' set for 60 seconds. <a href="/get-cookie">Read it</a>`);
});

app.get("/get-cookie", (req, res) => {
  res.json({ cookies: req.cookies });
});

app.get("/clear-cookie", (req, res) => {
  res.clearCookie("username");
  res.send("Cookie cleared. <a href='/get-cookie'>Check</a>");
});

// ---------- Sessions ----------
app.get("/login", (req, res) => {
  res.send(`
    <h2>Login</h2>
    <form method="POST" action="/login">
      <input name="username" placeholder="username" required />
      <input name="password" type="password" placeholder="password (use 1234)" required />
      <button>Login</button>
    </form>`);
});

app.post("/login", (req, res) => {
  const { username, password } = req.body;
  if (password === "1234") {
    req.session.user = username;
    return res.redirect("/profile");
  }
  res.status(401).send("Invalid credentials. <a href='/login'>Try again</a>");
});

app.get("/profile", (req, res) => {
  if (!req.session.user) return res.redirect("/login");
  res.send(`Welcome, ${req.session.user}! <a href="/logout">Logout</a>`);
});

app.get("/visits", (req, res) => {
  req.session.visits = (req.session.visits || 0) + 1;
  res.send(`You have visited this page ${req.session.visits} time(s) in this session.`);
});

app.get("/logout", (req, res) => {
  req.session.destroy(() => {
    res.clearCookie("connect.sid");
    res.redirect("/login");
  });
});

app.listen(PORT, () => console.log(`Server running at http://localhost:${PORT}`));
