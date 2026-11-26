# Website with HTML, CSS and JavaScript (Ajax)

**Create a Website with HTML, CSS and JavaScript (Implement Ajax)**

*Lab Experiment 11 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

Ajax (Asynchronous JavaScript and XML) is a technique that lets a web page ask the server for data in the background and update only a part of the page, without reloading the whole page. This experiment builds a small responsive website named **CampusConnect** with HTML, CSS and JavaScript. Its data (students, posts, comments) is loaded with Ajax, and its contact form sends data to a server with a POST request. The data comes from JSONPlaceholder, a free test API.

Objectives:

- Build a complete, responsive website with HTML5, CSS3 and JavaScript.
- Send GET requests with `XMLHttpRequest` and with `fetch()`.
- Send a POST request with a JSON body.
- Update the page from the JSON response without reloading it.
- Show loading, success and error messages, and handle failures (network errors, server errors).
- Validate the form on the client side before sending, and keep the page safe from HTML injection.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Structure | HTML5 | Pages, sections, form, semantic elements |
| Styling | CSS3 | Responsive layout (Grid, Flexbox, media queries), loading spinner |
| Logic | JavaScript (ES6) | Ajax requests, `async/await`, DOM updates, validation |
| Ajax | `XMLHttpRequest` and `fetch()` | Talk to the server in the background |
| Data format | JSON | Format of the data sent and received |
| Data source | JSONPlaceholder (`https://jsonplaceholder.typicode.com`) | Free fake REST API for testing |
| Tools | VS Code, Chrome / Edge DevTools (Network tab) | Writing the code and watching the requests |

## 3. How to Run

1. Keep `index.html`, `style.css` and `script.js` in one folder named `exp11-ajax-website`.
2. Turn the **internet on**. The data is loaded from the JSONPlaceholder website.
3. Open `index.html` in Chrome or Edge (double-click it, or use the Live Server extension in VS Code).
4. The students and the first six posts load by themselves. No installation or local server is needed.
5. To watch the Ajax requests, press `F12`, open the **Network** tab, choose **Fetch/XHR**, and reload the page.

## 4. Project Structure

```
exp11-ajax-website/
├── index.html    # Page structure: header, home, students, posts, contact form, footer
├── style.css     # Responsive styling (mobile first)
├── script.js     # All the Ajax code
└── REPORT.md     # This report
```

## 5. How Ajax Works

```
Browser (JavaScript)                         Server (API)
     | -- 1. request (GET /users) ------------> |
     |        (page stays usable)               |
     | <-- 2. response (JSON data) ------------ |
     | 3. JavaScript updates part of the page   |
```

| Step | What happens |
|---|---|
| 1 | An event (page load, button click, form submit) makes JavaScript send a request |
| 2 | The request goes in the background, so the page does not freeze or reload |
| 3 | The server answers with data, usually JSON |
| 4 | JavaScript turns the JSON text into an object (`JSON.parse` or `response.json()`) |
| 5 | JavaScript changes only the needed part of the page through the DOM |

### XMLHttpRequest and fetch

| Point | `XMLHttpRequest` | `fetch()` |
|---|---|---|
| Style | Callbacks (`onload`, `onerror`) | Promises (`.then`) or `async/await` |
| Age | Old, supported everywhere | Modern, cleaner syntax |
| Code length | Longer | Shorter |
| HTTP errors (404, 500) | Check `xhr.status` | Does **not** fail by itself, so `response.ok` must be checked |
| Network failure | `onerror` event | The promise is rejected (use `try/catch`) |

### XMLHttpRequest `readyState` values

| Value | Meaning |
|---|---|
| 0 | Request not started |
| 1 | `open()` has been called |
| 2 | Request sent, headers received |
| 3 | Response is loading |
| 4 | Response is complete (the `onload` event runs now) |

### Common HTTP status codes

| Code | Meaning |
|---|---|
| 200 | OK |
| 201 | Created (a new item was made by POST) |
| 400 | Bad request |
| 404 | Not found |
| 500 | Server error |

## 6. Features of the Website

### 6.1 Students: GET with XMLHttpRequest

**Aim:** To load a list from the server with `XMLHttpRequest` and show it as cards.

```js
const xhr = new XMLHttpRequest();          // 1. create the request object
xhr.open("GET", url, true);                // 2. method, URL, asynchronous
xhr.onload = function () {                 // 3. runs when the response has arrived
  if (xhr.status >= 200 && xhr.status < 300) {
    onSuccess(JSON.parse(xhr.responseText));   // 4. text -> object
  } else {
    onFail("Server returned status " + xhr.status);
  }
};
xhr.onerror = function () { onFail("Network error."); };
xhr.send();                                // 5. send
```

| Part | What it does |
|---|---|
| Loading | "Loading students..." with a spinner, until the data arrives |
| Cards | 10 students shown as cards (name, username, email, city, company) in 1, 2 or 3 columns |
| Search | Filters the already loaded students while typing (no new request is needed) |
| Reload button | Sends the request again |
| Error | A message with a **Retry** button if the network fails or the server answers with an error |

**Expected result:** ten student cards appear a moment after the page opens. Typing `meerut` or a name filters the cards instantly.

*Output:* *(screenshot)*

### 6.2 Posts: GET with fetch, async/await and pagination

**Aim:** To load data with `fetch()` and `async/await`, and to load it page by page.

```js
async function getJSON(url) {
  const response = await fetch(url);
  if (!response.ok) {                         // fetch does not fail on 404 or 500
    throw new Error("Server returned status " + response.status);
  }
  return response.json();
}

const posts = await getJSON(API + "/posts?_page=" + page + "&_limit=6");
```

| Part | What it does |
|---|---|
| Pagination | `?_page=2&_limit=6` asks the server for only 6 posts of page 2. **Previous** and **Next** change the page, and Next is disabled when fewer than 6 posts arrive (the last page). |
| Comments on demand | Each post has a **Show comments** button. The comments are requested (`/posts/1/comments`) only when the button is clicked, and are not requested again when the box is closed and reopened. |
| Event delegation | One click listener on the post list handles the buttons of all posts, including posts created later. |
| Error handling | `try / catch / finally` shows an error message with a Retry button, and always enables the button again. |

**Expected result:** six posts are shown. Next shows the next six. Clicking **Show comments** adds the post's comments below it, and the button changes to **Hide comments**.

*Output:* *(screenshots of two pages and an opened comment box)*

### 6.3 Contact form: POST with fetch

**Aim:** To send data to the server with a POST request.

```js
const response = await fetch(API + "/posts", {
  method: "POST",
  headers: { "Content-Type": "application/json; charset=UTF-8" },
  body: JSON.stringify({ title: data.name, body: data.message, userId: 1 })
});
const result = await response.json();      // { id: 101, ... }
```

| Check before sending | Message |
|---|---|
| Name shorter than 3 characters | Name must have at least 3 characters. |
| Email not in the form `a@b.c` | Enter a valid email address. |
| Message shorter than 10 characters | Message must have at least 10 characters. |

| Part | What it does |
|---|---|
| `event.preventDefault()` | Stops the normal form submit, so the page does not reload |
| Validation | Wrong fields get a red border and a message, and **no request is sent** |
| While sending | The button is disabled and "Sending your message..." is shown, which prevents double submission |
| Success | Shows the reference number and the server's reply in a green console-style box |
| Failure | Shows the error and enables the button again |

JSONPlaceholder answers a POST with status **201** and the new item with an `id` (101), but it does not really store it.

**Expected result:** after a valid form, the page shows `Message sent. Reference number: 101` and `Status: 201` with the JSON that the server returned. The form is cleared.

*Output:* *(screenshots of the validation error and the success message)*

### 6.4 Safety, responsive layout and other details

| Detail | Explanation |
|---|---|
| HTML escaping | Every piece of data from the server or the user passes through the `esc()` function before it is put into HTML, so tags like `<img onerror=...>` are shown as plain text and cannot run (protection against XSS). |
| Request counter | The Home section shows how many Ajax requests the page has made, which helps to see that comments are loaded only once. |
| Responsive design | A mobile-first layout: hamburger menu on small screens, 1 / 2 / 3 columns of cards by screen width (media queries at 601px and 901px). |
| Loading spinner | A CSS animation, shown while a request is waiting. |
| Smooth scrolling and sticky menu | `scroll-behavior: smooth` and `position: sticky` on the header. |

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Nothing loaded and the Console shows `net::ERR_INTERNET_DISCONNECTED` or a network error | The internet was off, so the API could not be reached | Turn the internet on and press **Retry** |
| `fetch` did not throw an error for a 404 or 500 response | `fetch()` fails only on network errors, not on HTTP error codes | Check `response.ok` and throw an error by hand |
| `Unexpected token < in JSON` | The server sent an HTML page (such as an error page) and not JSON | Check the URL and the status code before calling `response.json()` |
| CORS error in the Console | The server does not allow requests from another website | Use an API that allows CORS (JSONPlaceholder does) |
| Ajax did not work when the HTML file was opened from a local file | Browsers block requests to local files with `file://` | Call an online API, or run the page through Live Server |
| The page reloaded after clicking Send | The default form submit was not stopped | Call `event.preventDefault()` in the `submit` handler |
| The page showed the old data after Previous / Next | The old list was not replaced | Replace the list with `innerHTML = ...` after each response |
| Comments buttons of the posts did not work after the next page loaded | Listeners were attached only to the old buttons | Use event delegation on the parent list |
| The Send button could be clicked twice | The button stayed enabled during the request | Disable the button until the request ends (`finally` block) |
| Text with tags like `<b>` changed the look of the page | User and server text was put into `innerHTML` directly | Escape the text with `esc()` before it is added |

*(Keep only the problems you actually faced.)*

## 8. Testing

The website was tested with a script that loads the page, simulates the API (including failures) and clicks every control. All 27 checks passed. The tests used simulated responses, because the real API must be reached through the internet when the page is opened in a browser.

| Test | Expected Result | Result |
|---|---|---|
| Open the page | 10 student cards and 6 posts are loaded, and the counter shows 2 requests | Passed |
| Request type of students and posts | `XHR GET /users` and `fetch GET /posts?_page=1&_limit=6` | Passed |
| Student name containing `<img onerror=...>` | Shown as plain text, not as an image | Passed |
| Search `meerut` | 5 students are shown | Passed |
| Search `zzz` | "No student matches your search." | Passed |
| Click Next twice | Page 2 shows 6 posts, page 3 shows 2 posts and Next is disabled | Passed |
| Click Previous | Goes back to page 2 | Passed |
| Click Show comments | 2 comments are shown and the button reads Hide comments | Passed |
| Comment text containing `<b>post</b>` | Shown as plain text | Passed |
| Hide, then show the comments again | The box closes and reopens, and no second request is sent | Passed |
| Submit the form with wrong values | 3 fields marked invalid, error shown, no request sent | Passed |
| Submit a valid form | `Reference number: 101` and `Status: 201` are shown | Passed |
| After a successful send | The form is cleared and the button is enabled again | Passed |
| Server answers the POST with status 500 | Error message is shown and the button is enabled again | Passed |
| Network error while loading the students | Error message with a Retry button | Passed |
| Click Retry (students) | The 10 students load again | Passed |
| Server answers the posts request with status 500 | Error message with a Retry button | Passed |
| Click Retry (posts) | Posts load and the message is cleared | Passed |

*Output:* *(screenshots of the page, the Network tab showing the Fetch/XHR requests, and the main tests)*

## 9. Limitations and Future Scope

Current limitations:

- The website needs the internet, because the data comes from JSONPlaceholder.
- JSONPlaceholder is a fake API: a POST returns a reply but nothing is saved, so the sent message does not appear in the posts afterwards.
- The data is read only. Posts cannot be edited or deleted (PUT and DELETE requests are not used).
- The posts and students are not cached, so they are requested again each time they are loaded.

Possible improvements:

- Use PUT and DELETE requests to edit and delete posts.
- Connect the form to the Node.js and MongoDB backend of Experiments 12 and 13, so the data is stored permanently.
- Add caching with `localStorage` and a debounce on the search box.
- Add `AbortController` to cancel old requests, and a "Load more" button or infinite scroll.
- Use `Promise.all()` to load several requests together.

## 10. Conclusion

This experiment built a complete, responsive website with HTML, CSS and JavaScript, and added Ajax to it. Students were loaded with `XMLHttpRequest`, posts and comments were loaded with `fetch()` and `async/await`, and the contact form was sent with a POST request carrying JSON. The page was updated without reloading, loading and error states were handled, the form was validated before it was sent, and all text was escaped to keep the page safe. Ajax is the base of modern web applications, and in the next experiments the same requests will be sent to a backend written with Node.js.
