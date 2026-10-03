// Program 2: Routing with the http module (different URLs, HTML pages, 404)
// Run:  node 2_routing_server.js      Open: http://localhost:3000

const http = require("http");

const PORT = 3000;

// A small helper to wrap content in an HTML page
function page(title, body) {
  return `<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>${title}</title></head>
<body style="font-family:Arial;margin:30px">
  <nav><a href="/">Home</a> | <a href="/about">About</a> | <a href="/contact">Contact</a> | <a href="/api/time">Time (JSON)</a></nav>
  <hr>
  <h1>${title}</h1>
  ${body}
</body></html>`;
}

const server = http.createServer((req, res) => {
  // Parse the URL so we can separate the path from the query string
  const url = new URL(req.url, "http://" + req.headers.host);
  const path = url.pathname;

  console.log(req.method + " " + req.url);

  if (req.method === "GET" && path === "/") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(page("Home", "<p>Welcome to the Node.js routing demo.</p>"));

  } else if (req.method === "GET" && path === "/about") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(page("About", "<p>This server uses only Node's built-in <code>http</code> module.</p>"));

  } else if (req.method === "GET" && path === "/contact") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(page("Contact", "<p>Email: sakshi@example.com</p>"));

  } else if (req.method === "GET" && path === "/api/time") {
    // Send JSON instead of HTML
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ time: new Date().toISOString() }));

  } else {
    // Anything else: 404 Not Found
    res.writeHead(404, { "Content-Type": "text/html" });
    res.end(page("404 - Page Not Found", "<p>The page <b>" + path + "</b> does not exist.</p>"));
  }
});

server.listen(PORT, () => console.log("Server running at http://localhost:" + PORT));
