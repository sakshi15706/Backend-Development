// A tiny web server for Experiment 9 (no packages needed).
// Run with:  node server.js     then open http://localhost:3000
// Browsers block AJAX (fetch / XMLHttpRequest) for files opened directly from disk,
// so the pages must be served over http://.

const http = require("http");
const fs = require("fs");
const path = require("path");

const PORT = process.env.PORT || 3000;
const ROOT = __dirname;

const TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "text/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".xml": "application/xml; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".svg": "image/svg+xml",
    ".png": "image/png",
    ".ico": "image/x-icon"
};

function send(res, status, type, body) {
    res.writeHead(status, { "Content-Type": type, "Cache-Control": "no-store" });
    res.end(body);
}
function sendJSON(res, status, obj) {
    send(res, status, "application/json; charset=utf-8", JSON.stringify(obj));
}

const server = http.createServer((req, res) => {
    const url = new URL(req.url, "http://localhost");

    // ---- API: POST /api/echo  (receives JSON, answers with JSON) ----
    if (url.pathname === "/api/echo") {
        if (req.method !== "POST") return sendJSON(res, 405, { error: "Use POST for this address" });
        let body = "";
        req.on("data", (chunk) => {
            body += chunk;
            if (body.length > 10000) {
                sendJSON(res, 413, { error: "Request too large" });
                req.destroy();
            }
        });
        req.on("end", () => {
            let data;
            try { data = JSON.parse(body); }
            catch (e) { return sendJSON(res, 400, { error: "Invalid JSON" }); }
            const name = typeof data.name === "string" ? data.name.trim() : "";
            const message = typeof data.message === "string" ? data.message.trim() : "";
            if (!name || !message) return sendJSON(res, 400, { error: "Both name and message are required" });
            sendJSON(res, 200, {
                reply: "Hello " + name.slice(0, 40) + ", the server received your message.",
                received: { name: name.slice(0, 40), message: message.slice(0, 200) },
                characters: message.length,
                serverTime: new Date().toISOString()
            });
        });
        return;
    }

    // ---- Static files ----
    if (req.method !== "GET" && req.method !== "HEAD") return send(res, 405, "text/plain", "Method not allowed");

    let rel;
    try { rel = decodeURIComponent(url.pathname); }
    catch (e) { return send(res, 400, "text/plain", "Bad request"); }
    if (rel === "/") rel = "/index.html";

    const filePath = path.join(ROOT, rel);
    if (!filePath.startsWith(ROOT + path.sep)) return send(res, 403, "text/plain", "Forbidden");

    fs.readFile(filePath, (err, data) => {
        if (err) return send(res, 404, "text/plain; charset=utf-8", "404 Not Found");
        send(res, 200, TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream", data);
    });
});

server.listen(PORT, () => {
    console.log("Server running at http://localhost:" + PORT);
    console.log("Press Ctrl+C to stop.");
});
