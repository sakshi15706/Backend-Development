# Experiment 12: Programs to Familiarize Server-Side Scripting using Node JS

**Session:** 12  
**Course Outcome:** CO3  
**Name:** Sakshi Jaiswal  
**SAP ID:** 590015706  
**Date:** 3 October 2026  
**Folder:** `Lab/Exp12`

---

## 1. Aim

To write Node.js programs that introduce server-side scripting: creating web servers, routing, handling forms and JSON, using the file system, modules and events.

## 2. Software Requirements

| Item | Details |
|---|---|
| Runtime | Node.js (v18 or later) with npm |
| Editor | Visual Studio Code |
| Browser | Chrome / Edge |
| Test tool (optional) | `curl` or Postman, for POST, PUT and DELETE requests |
| Package | `express` (only for Program 9) |

Check the installation with `node -v` and `npm -v`.

## 3. Theory

### 3.1 Server-side scripting

Server-side scripting means the code runs on the **server**, not in the browser. The server receives a request, runs code (reads files, talks to a database, applies logic) and sends a response (HTML or JSON) to the browser.

```
Browser  --- request --->  Node.js server  (runs code, uses files / database)
Browser  <-- response ---  Node.js server
```

### 3.2 Node.js

Node.js is a JavaScript runtime built on Chrome's V8 engine, which lets JavaScript run outside the browser. Its main features:

| Feature | Meaning |
|---|---|
| **Non-blocking, asynchronous I/O** | The server does not wait for a slow task (file, database) and can handle other requests meanwhile. |
| **Event-driven** | Code responds to events, such as "a request arrived" or "data received". |
| **Single-threaded event loop** | One thread handles many connections efficiently. |
| **Modules and npm** | Code is split into modules, and npm gives access to thousands of packages. |

### 3.3 Important built-in modules

| Module | Use |
|---|---|
| `http` | Create web servers and handle requests and responses |
| `fs` | Read, write, copy, rename and delete files |
| `path` | Build and read file paths safely on any OS |
| `os` | Information about the computer (platform, memory, CPU) |
| `url` | Parse URLs and query strings |
| `events` | `EventEmitter` for event-driven code |
| `querystring`, `util` | Parse query strings, helper functions |

### 3.4 Request and response

| Part | What it has |
|---|---|
| **Request (`req`)** | `req.method` (GET, POST...), `req.url`, `req.headers`, and the body (arrives in chunks) |
| **Response (`res`)** | `res.writeHead(status, headers)`, `res.end(body)` |

Common status codes: **200** OK, **201** Created, **303** Redirect, **400** Bad Request, **404** Not Found, **405** Method Not Allowed, **500** Server Error.

### 3.5 Modules

Each file is a module. A file exposes things with `module.exports`, and another file loads them with `require()`.

```js
// mathModule.js
module.exports = { add, subtract };
// app.js
const math = require("./mathModule");     // our own file: starts with ./
const fs = require("fs");                 // built-in module: no ./
```

## 4. Programs

All programs are in the folder `Lab/Exp12`.

| No. | File | What it demonstrates |
|---|---|---|
| 1 | `1_hello_server.js` | The simplest web server with `http.createServer` and `listen` |
| 2 | `2_routing_server.js` | Routing by path and method, HTML pages, a JSON route, 404 page |
| 3 | `3_file_system.js` | `fs`: create folder, write, append, read, stat, copy, rename, async read, errors, delete |
| 4 | `4_mathModule.js`, `4_modules.js` | Creating a custom module (`module.exports`) and using it with `require`, `try...catch` |
| 5 | `5_events.js` | `EventEmitter`: `on`, `once`, `emit`, arguments, a class extending `EventEmitter`, `removeListener`, async order |
| 6 | `6_form_server.js` | HTML form, GET query string, POST body, validation, saving to a JSON file, HTML escaping, redirect |
| 7 | `7_json_api.js` | REST API with GET, POST, PUT and DELETE, JSON responses, status codes |
| 8 | `8_core_modules.js` | `path`, `os`, `URL`, `querystring`, `util`, `process` |
| 9 | `9_express_server.js` | The same ideas with Express: middleware, route parameters, query, JSON body |

## 5. Procedure

1. Create the folder `Exp12` and open it in VS Code.
2. Create the program files listed above.
3. Open the terminal in the folder (`Ctrl + ~`).
4. Run a program with `node <filename>`. For example: `node 3_file_system.js`.
5. For a **server** program (1, 2, 6, 7, 9), open the URL in the browser. The terminal must stay open. Stop the server with `Ctrl + C`.
6. For Program 9, run `npm install` first to install Express.
7. Use `curl` (or Postman) to test POST, PUT and DELETE requests of Program 7 and the form of Program 6.
8. Take screenshots of the terminal output and the browser pages.

Only one server can use port 3000 at a time. Stop the first server before starting the next one.

## 6. Code Explanation and Output

### Program 1: Hello server

```js
const http = require("http");
const server = http.createServer((req, res) => {
  res.writeHead(200, { "Content-Type": "text/plain" });
  res.end("Hello from Node.js server!");
});
server.listen(3000, () => console.log("Server running at http://localhost:3000"));
```

- `createServer` takes a function that runs for **every request**.
- `writeHead` sets the status code and the content type, and `end` sends the body.
- `listen(3000)` starts waiting for requests on port 3000.

**Output**

```
Terminal : Server running at http://localhost:3000
           GET /
Browser  : Hello from Node.js server!
```

### Program 2: Routing

The URL is parsed with `new URL(req.url, ...)`, and `if / else if` decides what to send, based on `req.method` and `url.pathname`.

| Request | Response |
|---|---|
| `GET /` | 200, Home page (HTML) |
| `GET /about` | 200, About page |
| `GET /contact` | 200, Contact page |
| `GET /api/time` | 200, `{"time":"2026-10-03T10:13:41.293Z"}` (JSON) |
| `GET /nothing` | 404, "Page Not Found" page |

### Program 3: File system

Steps done by the program: create a folder, `writeFileSync`, `appendFileSync` twice, `readFileSync`, count lines and words, `statSync`, `copyFileSync`, `renameSync`, `readdirSync`, async `readFile` with a callback, reading a missing file (error handling) and deleting everything.

**Output**

```
=== 4. Read the file (readFileSync) ===
Line 1: Hello Node.js
Line 2: File System module
Line 3: Server-side scripting

=== 5. Count lines and words ===
Lines: 3 | Words: 13 | Characters: 79

=== 6. File information (statSync) ===
Size in bytes : 79
Is a file     : true
Is a folder   : false

=== 7. Copy and rename ===
Files in folder: [ 'notes.txt', 'notes_renamed.txt' ]

=== 8. Asynchronous read (readFile with a callback) ===
(This line prints BEFORE the async result, because readFile does not block.)
Async read finished. First line: Line 1: Hello Node.js

=== 9. Reading a file that does not exist (error handling) ===
Error caught: ENOENT

=== 10. Delete files and folder ===
Deleted. Folder still exists? false
```

Note that the "(This line prints BEFORE...)" message appears before the async result: `readFile` does not block the program.

### Program 4: Modules

`4_mathModule.js` exports the functions `add`, `subtract`, `multiply`, `divide`, `isPrime`, `factorial` and the value `PI`. `4_modules.js` loads it with `require("./4_mathModule")`.

**Output**

```
add(10, 5)       = 15
subtract(10, 5)  = 5
multiply(10, 5)  = 50
divide(10, 5)    = 2
factorial(6)     = 720
PI               = 3.14159

Prime numbers up to 30:
2, 3, 5, 7, 11, 13, 17, 19, 23, 29

Error caught: Cannot divide by zero

Destructured: add(2, 3) = 5 | multiply(2, 3) = 6
Same module object both times? true
```

### Program 5: Events

```js
const EventEmitter = require("events");
const emitter = new EventEmitter();
emitter.on("greet", (name) => console.log("Hello, " + name + "!"));   // listen
emitter.emit("greet", "Sakshi");                                      // fire
```

- `on` runs every time, `once` runs only the first time, `removeListener` stops a listener.
- A `Shop` class that **extends** `EventEmitter` emits `sold`, `outOfStock` and `error` events.

**Output**

```
--- Basic events ---
Hello, Sakshi!
(second listener) Welcome to Node.js, Sakshi
once(): this runs only the first time
Listeners for 'greet': 2

--- Shop example ---
Sold 2 item(s). Stock left: 3
Error event: Only 3 items in stock
Sold 3 item(s). Stock left: 0
Alert: shop is out of stock!

--- Async order ---
1. Start
2. End of the script
2b. nextTick (runs before timers)
3. Inside setTimeout (runs later)
```

### Program 6: Form handling server

| Route | Work done |
|---|---|
| `GET /` | Shows an HTML form (name, email, message) |
| `GET /greet?name=Sakshi&city=Meerut` | Reads the query string with `url.searchParams` |
| `POST /submit` | Collects the body with `req.on("data")` and `req.on("end")`, parses it with `URLSearchParams`, validates, saves to `submissions.json`, then redirects (303) |
| `GET /submissions` | Reads the JSON file and shows all saved entries |

User text is passed through an `esc()` function, so `<b>Hi</b>` is shown as plain text and cannot run as HTML or script.

**Test results**

```
GET /greet?name=Sakshi&city=Meerut -> Hello Sakshi from Meerut!
POST with empty fields             -> 400 (errors shown)
POST with valid data               -> 303 redirect to /submissions
Saved in submissions.json          -> { "id": 1, "name": "Sakshi", "email": "s@x.com",
                                        "message": "<b>Hi</b>", "time": "..." }
```

### Program 7: JSON REST API

| Method | URL | Action | Result |
|---|---|---|---|
| GET | `/students` | List all (optional `?minMarks=80`) | 200 and JSON array |
| GET | `/students/1` | One student | 200, or 404 if missing |
| POST | `/students` | Add a student | 201 and the new student, or 400 for bad data |
| PUT | `/students/1` | Update a student | 200 and the updated student |
| DELETE | `/students/2` | Delete a student | 200 with a message |

Test commands and results:

```
curl localhost:3000/students
  -> [{"id":1,"name":"Rahul","marks":85},{"id":2,"name":"Priya","marks":92},{"id":3,"name":"Amit","marks":74}]

curl "localhost:3000/students?minMarks=80"
  -> [{"id":1,"name":"Rahul","marks":85},{"id":2,"name":"Priya","marks":92}]

curl -X POST -d '{"name":"Ravi","marks":80}' localhost:3000/students
  -> {"id":4,"name":"Ravi","marks":80}

curl -X POST -d '{"name":"Bad"}' localhost:3000/students
  -> {"error":"name and numeric marks are required"}   (status 400)

curl -X PUT -d '{"marks":95}' localhost:3000/students/1
  -> {"id":1,"name":"Rahul","marks":95}

curl -X DELETE localhost:3000/students/2
  -> {"message":"Deleted student 2"}

curl localhost:3000/students/99
  -> {"error":"Student not found"}                      (status 404)
```

The data is stored in memory, so it resets when the server restarts. A database is used in Experiment 13.

### Program 8: Core modules

**Output (selected lines)**

```
basename  : index.html
dirname   : /home/sakshi/projects/app
extname   : .html
join      : folder/sub/file.txt

protocol : https:
hostname : example.com
port     : 8080
pathname : /products/list
search   : ?category=books&page=2
category : books
after append: https://example.com:8080/products/list?category=books&page=2&sort=price#top

parse    : { name: 'Sakshi', city: 'Meerut', age: '20' }
stringify: course=CSE&year=2
format : Rahul is 20 years old
Node version : v22.22.0
Arguments    : [ 'hello', '123' ]
promisify: waited 300 ms
Program finished with code 0
```

(The `os` values, such as CPU cores and memory, depend on your computer.)

### Program 9: Express server

Run `npm install` and then `node 9_express_server.js`.

| Request | Response |
|---|---|
| `GET /hello/Sakshi` | `Hello, Sakshi!` (route parameter) |
| `GET /search?q=node` | `{"searchedFor":"node"}` (query string) |
| `POST /add` with `{"a":4,"b":6}` | `{"a":4,"b":6,"sum":10}` (JSON body) |
| `GET /zzz` | 404 - Not Found |

**Comparison with the plain `http` module**

| Task | `http` module | Express |
|---|---|---|
| Route | `if (url.pathname === "/about")` | `app.get("/about", ...)` |
| Route parameter | Split the path manually | `req.params.name` |
| Query string | `new URL(...).searchParams` | `req.query.q` |
| JSON body | Collect chunks and `JSON.parse` | `app.use(express.json())` |
| Send JSON | `JSON.stringify` and set the header | `res.json(data)` |

## 7. Output Screenshots

Take screenshots of the terminal and the browser and paste them here:

```
![Program 1 output](screenshots/p1.png)
![Program 2 routing](screenshots/p2.png)
![Program 3 file system](screenshots/p3.png)
![Program 6 form](screenshots/p6.png)
![Program 7 API](screenshots/p7.png)
```

## 8. Observations

- A Node.js server is only a program that keeps running. When the terminal closes or `Ctrl + C` is pressed, the server stops.
- The code inside `createServer` runs once for every request, including the browser's automatic `GET /favicon.ico` request.
- Asynchronous functions (`readFile`, `setTimeout`) do not block the program, so their results appear after the following lines.
- A POST body arrives in **chunks**, so it must be collected with the `data` and `end` events before it can be parsed.
- User input must always be escaped before it is put into HTML, otherwise a script can be injected.
- A redirect after a POST (status 303) stops the form from being submitted again when the page is refreshed.
- Express needs much less code than the `http` module for routing, parameters and JSON.

## 9. Result

Node.js programs for web servers, routing, file handling, modules, events, form handling, a JSON API and Express were written and executed successfully, and the outputs matched the expected results.

## 10. Conclusion

Node.js allows JavaScript to be used for server-side scripting. Its built-in modules (`http`, `fs`, `events`, `path`) are enough to build servers and handle files and forms, and its asynchronous, event-driven design keeps the server responsive. Express reduces the code needed for routing and JSON, and Experiment 13 adds a MongoDB database to store the data permanently.

