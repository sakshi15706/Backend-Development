// Program 1: Simplest Node.js web server (built-in http module)
// Run:  node 1_hello_server.js      Open: http://localhost:3000

const http = require("http");

const PORT = 3000;

// createServer() takes a function that runs for EVERY request.
// req = request from the browser, res = response we send back.
const server = http.createServer((req, res) => {
  console.log(req.method + " " + req.url);            // log each request in the terminal

  res.writeHead(200, { "Content-Type": "text/plain" }); // status code and header
  res.end("Hello from Node.js server!");                // send body and finish
});

// listen() starts the server on the given port
server.listen(PORT, () => {
  console.log("Server running at http://localhost:" + PORT);
});
