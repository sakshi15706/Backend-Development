# jQuery

**Programs to Familiarize jQuery (2 Programs)**

*Lab Experiment 10 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

jQuery is a small, fast JavaScript library. It gives short methods for selecting elements, changing the page, handling events and making effects, so tasks that need many lines of plain JavaScript take one line. This experiment demonstrates jQuery with two programs: a set of basic demos, and a small Task Manager application that uses them together.

Objectives:

- Select elements with jQuery selectors and change their text, HTML, CSS, classes and attributes.
- Show effects and animations (hide, show, fade, slide, `animate()`).
- Add, remove and clone elements.
- Handle mouse, keyboard and form events, including event delegation.
- Move around the DOM tree (parent, children, siblings) and use method chaining.
- Build a working application with validation, filtering and searching using jQuery.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Structure | HTML5 | Elements that the scripts select and change |
| Styling | CSS3 | Layout, highlight classes, badges and progress bar |
| Library | jQuery 3.7.1 (CDN) | Selectors, effects, events and DOM methods |
| Logic | JavaScript (ES5/ES6) | Program logic and the task array |
| Tools | VS Code, Chrome / Edge DevTools | Writing and inspecting the pages |

## 3. How to Run

1. Keep all the files in a folder named `exp10-jquery`.
2. Open `program1.html` in Chrome or Edge (double-click it, or use the Live Server extension in VS Code). Use the links in the header to switch to `program2.html`.
3. The internet must be on, because jQuery is loaded from `https://code.jquery.com`.
4. Program 1 prints each result in a green box under its buttons. No installation or server is needed.

## 4. Project Structure

```
exp10-jquery/
├── program1.html   # Program 1 page (eight demos)
├── program1.js     # Program 1 jQuery code
├── program2.html   # Program 2 page (Task Manager)
├── program2.js     # Program 2 jQuery code
├── style.css       # Styling for both pages
└── REPORT.md       # This report
```

## 5. Programs

### 5.1 Program 1: jQuery basics

**Aim:** To demonstrate the main groups of jQuery methods on one page. The code is inside `$(document).ready(function () { ... });`, which runs after the page has loaded.

#### Part A: Selectors

| Selector | What it selects |
|---|---|
| `$("li.fruit")` | All `li` elements with the class `fruit` |
| `$(".special")` | The element with the class `special` |
| `$("#fruitList li:first")` | The first item |
| `$("#fruitList li:odd")` | Items at index 1, 3, 5... |
| `$("#fruitList li:last-child")` | The last item |

```js
$("#selClass").click(function () {
  $("#fruitList li").removeClass("picked");
  $(".special").addClass("picked");
});
```

**Expected result:** each button highlights the selected items in green and the log shows how many were selected, for example `1 element(s) selected: [Mango]`.

*Output:* *(screenshot)*

#### Part B: Effects and animation

| Method | What it does |
|---|---|
| `hide()` / `show()` / `toggle()` | Hide, show or switch the element |
| `fadeOut()` / `fadeIn()` / `fadeTo()` | Fade the element out, in or to a given opacity |
| `slideUp()` / `slideDown()` / `slideToggle()` | Slide the element up or down |
| `animate({ left: "250px" }, 1000)` | Gradually change numeric CSS properties |
| `stop()` | Stops the running animation |

```js
$("#ball")
  .animate({ left: "250px" }, 700)
  .animate({ top: "30px" }, 400)
  .animate({ left: "0px" }, 700)
  .animate({ top: "0px" }, 400);
```

**Expected result:** the box hides, fades and slides with each button. The red ball moves, grows, and the chain button makes it move right, down, left and up one step after another.

*Output:* *(screenshot)*

#### Part C: Content, CSS and attributes

| Method | What it does |
|---|---|
| `text()` | Gets or sets plain text |
| `html()` | Gets or sets HTML inside an element |
| `val()` | Gets or sets the value of a form field |
| `css({ color: "red" })` | Changes CSS |
| `addClass()` / `removeClass()` / `toggleClass()` | Changes classes |
| `attr("title", "...")` | Gets or sets an attribute |

**Expected result:** `text()` returns `This is some text inside a paragraph.`, `html()` returns the same text with `<b>some</b>`, and `val()` returns `Hello jQuery`. The Set buttons change the paragraph.

*Output:* *(screenshot)*

#### Part D: Adding and removing elements

| Method | What it does |
|---|---|
| `append()` / `prepend()` | Adds inside, at the end or the start |
| `after()` | Adds after the element |
| `remove()` | Removes the element |
| `empty()` | Removes all the children |
| `clone()` | Copies the element |

**Expected result:** starting with 2 items, the buttons change the list to 3, 4, 5, 4, 5 and finally 0 items. Clicking a list item toggles its green highlight, which works for items added later because the click is attached to the parent list with `on()`.

*Output:* *(screenshot)*

#### Part E: Events

| Event | Fires when |
|---|---|
| `click()` / `dblclick()` | The box is clicked once or twice |
| `mouseenter()` / `mouseleave()` | The pointer enters or leaves the box |
| `mousemove()` | The pointer moves (x and y are shown) |
| `keyup()` | A key is released in the text box |
| `change()` | The select box value changes (the page colour changes) |

**Expected result:** the log shows the last event. Typing `jquery` shows `6 characters`. Choosing a colour changes the page background.

*Output:* *(screenshot)*

#### Part F: Traversing and chaining

| Method | Returns |
|---|---|
| `parent()` | The parent element |
| `children()` | The child elements |
| `siblings()` | The other elements at the same level |
| `next()` / `prev()` / `nextAll()` | The following, previous and all following elements |
| `eq(0)` | The element at the given index |
| `each()` | Runs a function for every element |

```js
$("#chainBox").css("background", "#ffe08a").slideUp(500).slideDown(500).text("Chain finished!");
```

**Expected result:** for the middle item, `siblings()` selects 3 items, `next()` selects 1 and `nextAll()` selects 2. The chain button changes the colour, slides the box up and down, and then changes its text.

*Output:* *(screenshot)*

### 5.2 Program 2: Task Manager

**Aim:** To build a small application that uses jQuery for validation, events, filtering and effects. The tasks are kept in a JavaScript array, and a `render()` function draws the list.

| Feature | jQuery used |
|---|---|
| Add task with validation | `submit()`, `e.preventDefault()`, `$.trim()`, `val()`, `fadeIn()` |
| Complete a task | `change` event, `closest("li")`, `data("id")` |
| Delete a task | `slideUp()` with a callback, then the task is removed from the array |
| Filter (All / Pending / Completed) | `data("filter")`, `addClass()` |
| Search | `keyup` event with `val()` |
| Statistics and progress bar | `$.grep()`, `text()`, `animate()` |
| Clear completed | `$.grep()` |
| Accordion | `slideToggle()`, `next()`, `siblings()` |
| Tabs | `hide()`, `fadeIn()`, `data("tab")` |
| Character and word counter | `keyup` event, `$.trim()`, `split()` |

Validation rules for a new task:

| Rule | Message |
|---|---|
| Title has fewer than 3 characters | Title must have at least 3 characters. |
| No priority chosen | Please choose a priority. |
| Same title already exists (not case-sensitive) | This task already exists. |

```js
$("#taskForm").submit(function (e) {
  e.preventDefault();                                   // stops the page from reloading
  var title = $.trim($("#taskTitle").val());
  if (title.length < 3) {
    $("#formError").text("Title must have at least 3 characters.").hide().fadeIn(200);
    return;
  }
  tasks.push({ id: nextId++, title: title, priority: priority, done: false });
  render();
});
```

The task items are created later, so their events are attached to the parent list (event delegation):

```js
$("#taskList").on("click", ".del", function () { ... });
```

User text is put in the page with `.text()`, so a title such as `<b>x</b>` is shown as plain text and cannot inject HTML.

**Expected result:** the page starts with 3 tasks (1 completed, 2 pending). A valid task slides in and the totals update. Invalid input shows a red error and a red border. Ticking a task strikes it through and moves the progress bar. Filters, search, accordion, tabs and the counter work as described.

*Output:* *(screenshots of the list, an error message and a filter)*

## 6. jQuery and Plain JavaScript

| Task | Plain JavaScript | jQuery (used here) |
|---|---|---|
| Select by id | `document.getElementById("a")` | `$("#a")` |
| Select by class | `document.querySelectorAll(".x")` | `$(".x")` |
| Change text | `el.textContent = "Hi"` | `$("#a").text("Hi")` |
| Hide | `el.style.display = "none"` | `$("#a").hide()` |
| Add a class | `el.classList.add("on")` | `$("#a").addClass("on")` |
| Click event | `el.addEventListener("click", f)` | `$("#a").click(f)` |
| Loop | `for (...)` | `$("li").each(f)` |

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| `$ is not defined` in the Console | The jQuery script did not load (no internet) or was placed after our own script | Check the internet connection, and put the jQuery `<script>` before our script |
| `$("#id")` found nothing | The code ran before the element existed | Put the code inside `$(document).ready(function () { ... });` |
| Clicking a newly added item did nothing | The handler was attached only to items that existed at load time | Use event delegation: `$("#list").on("click", ".item", fn)` |
| Form submit reloaded the page and the error message disappeared | Default form submission | Call `e.preventDefault()` in the `submit` handler |
| A deleted item came back after the next redraw | The item was removed from the page but not from the `tasks` array | Remove it from the array and then call `render()` |
| Animations ran one after another instead of together | Chained animations are queued | Use one `animate()` with several properties for a simultaneous effect |
| HTML tags typed by the user appeared as formatting | `html()` was used with user input | Use `text()` for user input |

*(Keep only the problems you actually faced.)*

## 8. Testing

Both pages were tested by a script that clicks each control and checks the result. All 38 checks passed.

| Test | Expected Result | Result |
|---|---|---|
| Program 1: `$(".special")`, `$("li")`, `:odd` | Selects 1, 5 and 2 elements | Passed |
| Program 1: `text()`, `html()`, `val()` | `This is some text inside a paragraph.`, text with `<b>some</b>`, `Hello jQuery` | Passed |
| Program 1: set html, toggle class, `attr()` | Bold text appears, class is added, title is `Set by jQuery` | Passed |
| Program 1: append, prepend, after, remove, clone, empty | List has 3, 4, 5, 4, 5 and 0 items | Passed |
| Program 1: click and double-click the event box | Log shows `click`, and `dblclick` toggles the colour | Passed |
| Program 1: type `jquery` in the key box | Log shows 6 characters | Passed |
| Program 1: choose a colour | `change` event is logged | Passed |
| Program 1: `next()`, `siblings()`, `nextAll()`, `each()` | 1, 3 and 2 elements; each item listed with its index | Passed |
| Program 2: open the page | 3 tasks: 1 completed, 2 pending | Passed |
| Program 2: add a 2-character title | Rejected: at least 3 characters | Passed |
| Program 2: add a task with no priority | Rejected: choose a priority | Passed |
| Program 2: add `push code to github` (exists in other case) | Rejected: already exists | Passed |
| Program 2: add `Write report`, priority High | Task added, total is 4 | Passed |
| Program 2: complete the new task | 2 completed, 2 pending | Passed |
| Program 2: filter Completed and Pending | 2 tasks in each | Passed |
| Program 2: search `report`, then `zzz` | 1 task, then the "No tasks to show" message | Passed |
| Program 2: Clear completed | 2 tasks left, 0 completed | Passed |
| Program 2: add a task titled `<b>x</b> bold` | Shown as text, tags are escaped | Passed |
| Program 2: click a tab, open an accordion item | Tab becomes active, accordion opens | Passed |
| Program 2: type `one two three` in the note box | 13 characters, 3 words | Passed |

*Output:* *(screenshots of the main tests)*

## 9. Limitations and Future Scope

Current limitations:

- The tasks are kept in a JavaScript array, so they are lost when the page is refreshed.
- jQuery is loaded from a CDN, so the pages do not work without the internet.
- Most of these jQuery features can now also be written in plain JavaScript, so jQuery is mainly useful for older projects.

Possible improvements:

- Save tasks with `localStorage` so they stay after a refresh.
- Add edit, due dates and drag-and-drop ordering (for example with jQuery UI).
- Load tasks from a server with `$.ajax()` (see Experiment 9).
- Add keyboard support and ARIA attributes so every action works without a mouse.

## 10. Conclusion

This experiment showed how jQuery makes client-side scripting shorter. Elements were selected and changed, effects and animations were shown, elements were added and removed, and events, traversing and method chaining were demonstrated in Program 1. Program 2 combined these ideas into a working Task Manager with validation, event delegation, filtering, searching, an accordion and tabs. Understanding selectors, events and the DOM through jQuery also makes it easier to understand the same ideas in plain JavaScript and in modern front-end frameworks.
