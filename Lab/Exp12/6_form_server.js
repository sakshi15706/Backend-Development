// Program 6: Handling GET query strings and POST form data, saving to a JSON file
// Run:  node 6_form_server.js      Open: http://localhost:3000

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = 3000;
const dataFile = path.join(__dirname, "submissions.json");

// ---------- helper functions ----------
function loadData() {
  if (!fs.existsSync(dataFile)) { return []; }
  return JSON.parse(fs.readFileSync(dataFile, "utf8"));
}
function saveData(list) {
  fs.writeFileSync(dataFile, JSON.stringify(list, null, 2));
}
// Escape HTML so users cannot inject scripts
function esc(text) {
  return String(text)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}
function page(title, body) {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>${title}</title>
<style>
  body{font-family:Arial;max-width:650px;margin:30px auto;padding:0 15px}
  input,textarea{width:100%;padding:8px;margin:4px 0 12px;box-sizing:border-box}
  button{padding:9px 20px;background:#2c7be5;color:#fff;border:0;border-radius:4px}
  .err{color:#b42318} .card{border:1px solid #bbb;padding:8px 14px;margin:8px 0;border-radius:6px}
</style></head><body>
<nav><a href="/">Form</a> | <a href="/submissions">All submissions</a> | <a href="/greet?name=Sakshi&city=Meerut">Query demo</a></nav>
<h1>${title}</h1>${body}</body></html>`;
}
function send(res, status, html) {
  res.writeHead(status, { "Content-Type": "text/html" });
  res.end(html);
}

// ---------- server ----------
const server = http.createServer((req, res) => {
  const url = new URL(req.url, "http://" + req.headers.host);
  console.log(req.method + " " + url.pathname);

  // 1. Show the form
  if (req.method === "GET" && url.pathname === "/") {
    send(res, 200, page("Feedback Form", `
      <form method="POST" action="/submit">
        <label>Name</label><input name="name">
        <label>Email</label><input name="email" type="email">
        <label>Message</label><textarea name="message" rows="4"></textarea>
        <button type="submit">Submit</button>
      </form>`));

  // 2. GET with a query string: /greet?name=Sakshi&city=Meerut
  } else if (req.method === "GET" && url.pathname === "/greet") {
    const name = url.searchParams.get("name") || "Guest";
    const city = url.searchParams.get("city") || "unknown city";
    send(res, 200, page("Query String Demo",
      `<p>Hello <b>${esc(name)}</b> from <b>${esc(city)}</b>!</p>
       <p>Try changing the values in the address bar.</p>`));

  // 3. POST: read the body in chunks, then parse it
  } else if (req.method === "POST" && url.pathname === "/submit") {
    let body = "";
    req.on("data", (chunk) => { body += chunk; });        // data arrives in pieces
    req.on("end", () => {                                  // all pieces received
      const form = new URLSearchParams(body);
      const name = (form.get("name") || "").trim();
      const email = (form.get("email") || "").trim();
      const message = (form.get("message") || "").trim();

      // Validation
      const errors = [];
      if (!name) errors.push("Name is required.");
      if (!email) errors.push("Email is required.");
      if (!message) errors.push("Message is required.");

      if (errors.length > 0) {
        const list = errors.map((e) => "<li class='err'>" + e + "</li>").join("");
        send(res, 400, page("Please fix these errors", "<ul>" + list + "</ul><a href='/'>Go back</a>"));
        return;
      }

      const all = loadData();
      all.push({ id: all.length + 1, name, email, message, time: new Date().toISOString() });
      saveData(all);

      // Redirect so a refresh does not submit the form again
      res.writeHead(303, { Location: "/submissions" });
      res.end();
    });

  // 4. Show saved data
  } else if (req.method === "GET" && url.pathname === "/submissions") {
    const all = loadData();
    const cards = all.map((s) =>
      `<div class="card"><b>#${s.id} ${esc(s.name)}</b> (${esc(s.email)})<br>
       ${esc(s.message)}<br><small>${esc(s.time)}</small></div>`).join("");
    send(res, 200, page("Submissions (" + all.length + ")", cards || "<p>No submissions yet.</p>"));

  } else {
    send(res, 404, page("404 Not Found", "<p>No such page.</p>"));
  }
});

server.listen(PORT, () => console.log("Server running at http://localhost:" + PORT));
