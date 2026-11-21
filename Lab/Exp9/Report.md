# AJAX with HTML, XML and JSON

**Programs using AJAX to load HTML, XML and JSON data without reloading the page**

*Lab Experiment 9 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

AJAX (Asynchronous JavaScript and XML) is a technique that lets a web page request data from a server in the background and update only part of the page, without a full reload. The data can be HTML, XML, JSON or plain text. This experiment builds five small programs that load HTML, XML and JSON data and also send JSON to a server.

Objectives:

- Understand how AJAX works and why it is asynchronous.
- Use `XMLHttpRequest` and the newer `fetch()` API.
- Load an HTML fragment and insert it into the page.
- Load and read an XML document using the XML DOM.
- Load JSON, convert it into JavaScript objects, and filter and sort it.
- Send JSON to a server with a POST request.
- Handle errors such as a missing file or a network failure.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Page | HTML5, CSS3 | Layout and styling |
| Client logic | JavaScript (ES6) | `XMLHttpRequest`, `fetch`, DOM updates |
| Data formats | HTML, XML, JSON | The three kinds of data loaded |
| Server | Node.js (`http` module, no packages) | Serves the files and answers the POST request |
| Tools | VS Code, Chrome / Edge DevTools (Network tab) | Writing code and watching requests |

## 3. How to Run

AJAX does not work when `index.html` is opened directly from the disk (`file://`), because browsers block those requests. The page must be served over `http://`.

**Option A: Node.js (recommended, needed for Program 4)**

1. Open the `exp9-ajax` folder in VS Code and open the terminal (Ctrl + `).
2. Run:
   ```
   node server.js
   ```
3. Open http://localhost:3000 in Chrome or Edge. Press Ctrl + C in the terminal to stop the server.

**Option B: VS Code Live Server** (Programs 1, 2, 3 and 5 work; Program 4 needs Option A): right-click `index.html` and choose "Open with Live Server".

**Option C: Python** (same limits as B): run `python -m http.server 3000` in the folder and open http://localhost:3000.

## 4. Project Structure

```
exp9-ajax/
├── index.html              # the page with five programs (HTML, CSS and JavaScript)
├── server.js               # small Node.js web server
├── partials/
│   └── about.html          # HTML fragment loaded by Program 1
├── data/
│   ├── students.xml        # XML data loaded by Program 2
│   └── products.json       # JSON data loaded by Program 3
└── REPORT.md               # This report
```

## 5. Theory

### 5.1 How AJAX Works

```
Browser (page stays open)                    Server
   |  1. JavaScript creates a request           |
   |------------------------------------------->|
   |  2. The user can keep using the page       |
   |                                            |  3. Server finds / builds the data
   |<-------------------------------------------|
   |  4. JavaScript receives the response       |
   |  5. JavaScript updates part of the page    |
```

"Asynchronous" means the browser does not freeze while it waits; a function runs when the response arrives.

### 5.2 `XMLHttpRequest` readyState and common status codes

| readyState | Name | Meaning |
|---|---|---|
| 0 | UNSENT | Request object created |
| 1 | OPENED | `open()` has been called |
| 2 | HEADERS_RECEIVED | Response headers have arrived |
| 3 | LOADING | Body is being downloaded |
| 4 | DONE | Request finished; check `status` |

| Status | Meaning |
|---|---|
| 200 | OK: the request succeeded |
| 400 | Bad Request: the server could not understand the data sent |
| 403 | Forbidden |
| 404 | Not Found: the file does not exist |
| 405 | Method Not Allowed |

### 5.3 HTML vs XML vs JSON

| Aspect | HTML | XML | JSON |
|---|---|---|---|
| Purpose | Ready-made page content | General structured data | Structured data for programs |
| Read in JavaScript | `innerHTML` | `responseXML` and DOM methods (`getElementsByTagName`) | `JSON.parse()` or `response.json()` |
| Size | Larger (contains markup and styling hooks) | Larger (opening and closing tags) | Smaller and lighter |
| Readable by humans | Yes | Yes | Yes |
| Typical use today | Loading page fragments | Older web services, feeds | Most modern APIs |

### 5.4 `XMLHttpRequest` vs `fetch()`

| Aspect | `XMLHttpRequest` | `fetch()` |
|---|---|---|
| Style | Events and callbacks (`onload`, `onreadystatechange`) | Promises, works with `async` / `await` |
| Code length | Longer | Shorter and cleaner |
| JSON | Manual `JSON.parse(xhr.responseText)` | `await res.json()` |
| HTTP errors (404, 500) | Check `xhr.status` | Check `res.ok` (a 404 does not throw an error) |
| Progress events, request abort | Built in | Needs extra code (`AbortController`) |

## 6. Programs

### 6.1 Program 1: AJAX with HTML (`XMLHttpRequest`)

**Aim:** To load an HTML fragment from the server and insert it into the page.

```js
const xhr = new XMLHttpRequest();
xhr.open("GET", "partials/about.html", true);     // true = asynchronous
xhr.onload = function () {
    if (xhr.status === 200) out.innerHTML = xhr.responseText;
    else showError("Could not load the page (HTTP " + xhr.status + ").");
};
xhr.onerror = function () { showError("Network error."); };
xhr.send();
```

**Expected result:** Load HTML shows the content of `about.html` inside the page, without a reload, and the log shows status 200. Load a missing file shows an error message and status 404.

**Note:** `innerHTML` is used because the file belongs to the same site and is trusted. HTML from an unknown source should never be inserted this way.

*Output:* *(screenshots of the 200 and 404 cases)*

### 6.2 Program 2: AJAX with XML (`XMLHttpRequest`)

**Aim:** To load an XML file, read its elements and attributes, and show them in a table.

```js
let xml = xhr.responseXML;                         // already parsed XML
if (!xml) xml = new DOMParser().parseFromString(xhr.responseText, "application/xml");
const students = xml.getElementsByTagName("student");
Array.from(students).forEach((s) => {
    const id = s.getAttribute("id");
    const name = s.getElementsByTagName("name")[0].textContent;
});
```

**Expected result:** A table of the five students (ID, name, course, year, marks) appears, with "Average marks: 80.4". The log shows "5 `<student>` elements found". If the XML is not well formed, an error message is shown instead.

*Output:* *(screenshot of the table)*

### 6.3 Program 3: AJAX with JSON (`fetch` and `XMLHttpRequest`)

**Aim:** To load JSON, convert it into JavaScript objects, and filter and sort it in the browser.

```js
const res = await fetch("data/products.json");
if (!res.ok) throw new Error("HTTP " + res.status);
const products = await res.json();                 // JSON text to JavaScript array
```

The second button does the same with `XMLHttpRequest` and `JSON.parse(xhr.responseText)`, so both methods can be compared.

**Expected result:** Eight product cards appear. The category and sort menus become active: choosing "book" shows three books; "Price: low to high" puts Clean Code (Rs. 499) first.

*Output:* *(screenshots: all products, filtered by category, sorted by price)*

### 6.4 Program 4: Sending JSON to the server (POST)

**Aim:** To send data to the server as JSON and show the JSON reply.

```js
const res = await fetch("/api/echo", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, message })
});
const data = await res.json();
```

`server.js` reads the body, checks that `name` and `message` are present, and answers with JSON containing a reply, the received values, the character count and the server time.

**Expected result:**

| Input | Result |
|---|---|
| Name and message filled | Status 200; formatted JSON reply is shown |
| A field left empty | Message shown in the page; no request is sent |
| Server not running or Live Server used | "Request failed" message |

*Output:* *(screenshot of the JSON reply)*

### 6.5 Program 5: Watching an `XMLHttpRequest` step by step

**Aim:** To see the `readyState` values change during a request.

**Expected log for a successful request:**

```
created: readyState = 0 (UNSENT)
readyState = 1 (OPENED)
readyState = 2 (HEADERS_RECEIVED)
readyState = 3 (LOADING)
readyState = 4 (DONE) | status = 200 | bytes = ...
```

For `data/nothing.json` the last line shows `status = 404`, which shows that a finished request (readyState 4) is not always a successful one. For very small files, readyState 3 may be skipped.

*Output:* *(screenshots of a 200 and a 404 request)*

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Nothing loaded; Console shows a CORS / "blocked" error | The page was opened as `file://` | Serve the page over `http://` with `node server.js` or Live Server |
| `Cannot GET` or 404 for a data file | Wrong path, or the server was started in another folder | Run the server inside `exp9-ajax` and check the file path |
| `xhr.responseXML` was `null` | Server sent the XML with the wrong content type | Send `application/xml`, or parse `responseText` with `DOMParser` |
| `fetch` did not throw an error on a missing file | `fetch` only fails on network errors | Check `res.ok` and throw an error for 404 and 500 |
| `Unexpected token` when reading JSON | The file was not valid JSON (for example a trailing comma) | Check the JSON with `JSON.parse` in a `try` / `catch` and fix the file |
| Old data kept showing after editing a file | The browser cached the response | Hard refresh with Ctrl + F5; the server sends `Cache-Control: no-store` |
| POST gave 405 or "Request failed" | Page served by Live Server, which has no `/api/echo` | Use `node server.js` for Program 4 |
| Page could break with special characters in data | Data inserted with `innerHTML` | Insert server data with `textContent` (used for XML, JSON and POST output) |

*(Keep only the problems you actually faced.)*

## 8. Testing

| Test | Expected Result |
|---|---|
| Open http://localhost:3000 | Page loads with five programs, no warning banner |
| Open `index.html` directly from disk | Banner says to start the server |
| Program 1: Load HTML | About text appears; status 200 in the log |
| Program 1: Load a missing file | Error message; status 404 |
| Program 2: Load XML | Table with 5 students; average marks 80.4 |
| Program 3: Load with `fetch()` | 8 product cards; log shows content type `application/json` |
| Program 3: Load with `XMLHttpRequest` | Same 8 cards |
| Program 3: choose category "book" | 3 books shown |
| Program 3: sort by price, low to high | Clean Code first, ThinkPad X1 last |
| Program 4: send name and message | Status 200 and a JSON reply |
| Program 4: leave a field empty | Validation message; no request sent |
| Program 5: request `data/nothing.json` | readyState goes up to 4 with status 404 |
| DevTools, Network tab, any program | The request appears without the page reloading |
| Stop the server and click a Load button | "Network error" message |

Automated server check (run in Node.js against `server.js`): the page, HTML fragment, XML and JSON files were all served with status 200 and the correct content types; the JSON file parsed as 8 products and the XML file contained 5 students; a missing file returned 404; a path-traversal attempt returned 403; and `/api/echo` returned 200 for valid JSON, 400 for a missing field or invalid JSON, and 405 for a GET request.

*Output:* *(screenshots of the main tests and the Network tab)*

## 9. Limitations and Future Scope

Current limitations:

- The data files are static; nothing is stored on the server.
- The Node.js server is a minimal teaching server, not meant for production.
- There is no loading indicator on most requests, and no retry on failure.
- Insecure cross-site requests (CORS) and authentication are not covered.

Possible improvements:

- Load data from a real public API with `fetch()` and handle CORS.
- Store submitted data in a database such as MongoDB (see Experiment 13).
- Add loading spinners, timeouts and request cancelling with `AbortController`.
- Use JSON instead of XML for new services, and add pagination and search on the server.

## 10. Conclusion

This experiment showed how AJAX updates part of a page without reloading it. HTML, XML and JSON data were loaded with `XMLHttpRequest` and `fetch()`, XML was read through the XML DOM, JSON was parsed into JavaScript objects and then filtered and sorted, and a JSON object was sent to a Node.js server with a POST request. Handling status codes, network errors and invalid data was part of every program. JSON with `fetch()` and `async` / `await` is the most common choice today, while `XMLHttpRequest` remains useful to understand how requests work underneath.
