/* =====================================================================
   CampusConnect: JavaScript with Ajax
   - Students  : XMLHttpRequest (GET)
   - Posts     : fetch + async/await (GET with page parameters), comments on click
   - Contact   : fetch (POST with a JSON body)
   The data comes from the free test API https://jsonplaceholder.typicode.com
   ===================================================================== */

const API = "https://jsonplaceholder.typicode.com";

// ---------- Small helpers ----------
let requestCount = 0;
function countRequest() {
  requestCount++;
  document.getElementById("reqCount").textContent = requestCount;
}

// Escape text before putting it into HTML (stops script injection)
function esc(text) {
  return String(text == null ? "" : text)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
}

// Show a message in a status box: type is "loading", "error" or "ok"
function setStatus(id, type, html) {
  const box = document.getElementById(id);
  box.className = "status " + (type || "");
  box.innerHTML = html || "";
}

// =====================================================================
// PART 1: STUDENTS using XMLHttpRequest
// =====================================================================
let allUsers = [];

function xhrGet(url, onSuccess, onFail) {
  const xhr = new XMLHttpRequest();          // 1. create the request object
  xhr.open("GET", url, true);                // 2. method, URL, asynchronous = true
  xhr.onload = function () {                 // 3. runs when the response has arrived (readyState 4)
    if (xhr.status >= 200 && xhr.status < 300) {
      try {
        onSuccess(JSON.parse(xhr.responseText));   // 4. text -> JavaScript object
      } catch (e) {
        onFail("The server sent data in a wrong format.");
      }
    } else {
      onFail("Server returned status " + xhr.status);
    }
  };
  xhr.onerror = function () { onFail("Network error. Check your internet connection."); };
  xhr.timeout = 10000;
  xhr.ontimeout = function () { onFail("The request took too long."); };
  xhr.send();                                // 5. send the request
  countRequest();
}

function loadUsers() {
  setStatus("userStatus", "loading", "Loading students...");
  document.getElementById("userGrid").innerHTML = "";
  xhrGet(
    API + "/users",
    function (users) {
      allUsers = users;
      setStatus("userStatus", "ok", users.length + " students loaded.");
      renderUsers();
    },
    function (message) {
      setStatus("userStatus", "error",
        "Could not load students: " + esc(message) + ' <button class="btn small" id="retryUsers">Retry</button>');
    }
  );
}

function renderUsers() {
  const q = document.getElementById("userSearch").value.toLowerCase().trim();
  const list = allUsers.filter(function (u) {
    return (u.name + " " + u.email + " " + u.address.city).toLowerCase().indexOf(q) !== -1;
  });

  const grid = document.getElementById("userGrid");
  if (list.length === 0) {
    grid.innerHTML = '<p class="status">No student matches your search.</p>';
    return;
  }
  grid.innerHTML = list.map(function (u) {
    return '<div class="card">' +
      '<div class="avatar">' + esc(u.name.charAt(0)) + "</div>" +
      "<h3>" + esc(u.name) + "</h3>" +
      "<p>@" + esc(u.username) + "</p>" +
      "<p>" + esc(u.email) + "</p>" +
      "<p>" + esc(u.address.city) + " | " + esc(u.company.name) + "</p>" +
      "</div>";
  }).join("");
}

// =====================================================================
// PART 2: POSTS using fetch and async/await
// =====================================================================
const POSTS_PER_PAGE = 6;
let page = 1;

// One reusable function for every GET request made with fetch
async function getJSON(url) {
  countRequest();
  const response = await fetch(url);
  if (!response.ok) {                         // fetch does not fail on 404 or 500, so we check
    throw new Error("Server returned status " + response.status);
  }
  return response.json();
}

async function loadPosts() {
  const list = document.getElementById("postList");
  setStatus("postStatus", "loading", "Loading posts...");
  document.getElementById("prevPage").disabled = true;
  document.getElementById("nextPage").disabled = true;

  try {
    const posts = await getJSON(API + "/posts?_page=" + page + "&_limit=" + POSTS_PER_PAGE);
    list.innerHTML = posts.map(function (p) {
      return '<article class="post" data-id="' + p.id + '">' +
        "<h3>" + esc(p.title) + "</h3>" +
        "<p>" + esc(p.body) + "</p>" +
        '<button class="btn small show-comments">Show comments</button>' +
        '<div class="comments" hidden></div>' +
        "</article>";
    }).join("");

    setStatus("postStatus", "", "");
    document.getElementById("pageNo").textContent = page;
    document.getElementById("prevPage").disabled = page === 1;
    document.getElementById("nextPage").disabled = posts.length < POSTS_PER_PAGE;   // last page
  } catch (err) {
    setStatus("postStatus", "error",
      "Could not load posts: " + esc(err.message) + ' <button class="btn small" id="retryPosts">Retry</button>');
    document.getElementById("prevPage").disabled = page === 1;
  }
}

// Comments are loaded only when the button is clicked (on demand)
async function toggleComments(button) {
  const post = button.closest(".post");
  const box = post.querySelector(".comments");

  if (!box.hidden) {                          // already open: close it
    box.hidden = true;
    button.textContent = "Show comments";
    return;
  }
  if (box.dataset.loaded === "yes") {         // already loaded once: just show it
    box.hidden = false;
    button.textContent = "Hide comments";
    return;
  }

  button.disabled = true;
  button.textContent = "Loading...";
  try {
    const comments = await getJSON(API + "/posts/" + post.dataset.id + "/comments");
    box.innerHTML = comments.map(function (c) {
      return "<div><b>" + esc(c.email) + "</b><br>" + esc(c.body) + "</div>";
    }).join("");
    box.dataset.loaded = "yes";
    box.hidden = false;
    button.textContent = "Hide comments";
  } catch (err) {
    box.innerHTML = '<div class="status error">Could not load comments: ' + esc(err.message) + "</div>";
    box.hidden = false;
    button.textContent = "Show comments";
  } finally {
    button.disabled = false;
  }
}

// =====================================================================
// PART 3: CONTACT FORM sent with a POST request
// =====================================================================
function validateContact(data) {
  const errors = {};
  if (data.name.length < 3) { errors.cName = "Name must have at least 3 characters."; }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) { errors.cEmail = "Enter a valid email address."; }
  if (data.message.length < 10) { errors.cMsg = "Message must have at least 10 characters."; }
  return errors;
}

async function sendContact(event) {
  event.preventDefault();                     // stop the normal form submit (page reload)

  const data = {
    name: document.getElementById("cName").value.trim(),
    email: document.getElementById("cEmail").value.trim(),
    message: document.getElementById("cMsg").value.trim()
  };

  // Clear old errors, then validate
  ["cName", "cEmail", "cMsg"].forEach(function (id) {
    document.getElementById(id).classList.remove("invalid");
  });
  document.getElementById("formResponse").hidden = true;
  const errors = validateContact(data);
  const ids = Object.keys(errors);
  if (ids.length > 0) {
    ids.forEach(function (id) { document.getElementById(id).classList.add("invalid"); });
    setStatus("formStatus", "error", ids.map(function (id) { return esc(errors[id]); }).join("<br>"));
    return;
  }

  const button = document.getElementById("sendBtn");
  button.disabled = true;
  setStatus("formStatus", "loading", "Sending your message...");

  try {
    countRequest();
    const response = await fetch(API + "/posts", {
      method: "POST",
      headers: { "Content-Type": "application/json; charset=UTF-8" },
      body: JSON.stringify({ title: data.name + " <" + data.email + ">", body: data.message, userId: 1 })
    });
    if (!response.ok) { throw new Error("Server returned status " + response.status); }

    const result = await response.json();
    setStatus("formStatus", "ok", "Message sent. Reference number: " + esc(result.id));
    const box = document.getElementById("formResponse");
    box.textContent = "Status: " + response.status + "\nResponse from server:\n" + JSON.stringify(result, null, 2);
    box.hidden = false;
    document.getElementById("contactForm").reset();
  } catch (err) {
    setStatus("formStatus", "error", "Could not send the message: " + esc(err.message));
  } finally {
    button.disabled = false;
  }
}

// =====================================================================
// START: attach events (event delegation for buttons created later)
// =====================================================================
document.addEventListener("DOMContentLoaded", function () {
  // Students
  document.getElementById("userSearch").addEventListener("input", renderUsers);
  document.getElementById("reloadUsers").addEventListener("click", loadUsers);

  // Posts
  document.getElementById("prevPage").addEventListener("click", function () { page--; loadPosts(); });
  document.getElementById("nextPage").addEventListener("click", function () { page++; loadPosts(); });
  document.getElementById("postList").addEventListener("click", function (e) {
    const btn = e.target.closest(".show-comments");
    if (btn) { toggleComments(btn); }
  });

  // Retry buttons are created later inside the status boxes
  document.getElementById("userStatus").addEventListener("click", function (e) {
    if (e.target.id === "retryUsers") { loadUsers(); }
  });
  document.getElementById("postStatus").addEventListener("click", function (e) {
    if (e.target.id === "retryPosts") { loadPosts(); }
  });

  // Form
  document.getElementById("contactForm").addEventListener("submit", sendContact);

  // Close the mobile menu after a link is clicked
  document.querySelectorAll(".nav a").forEach(function (a) {
    a.addEventListener("click", function () { document.getElementById("menu-toggle").checked = false; });
  });

  // Load the data when the page opens
  loadUsers();
  loadPosts();
});
