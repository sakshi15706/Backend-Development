# DOM and Event Handling

**Programs to Demonstrate the Document Object Model (DOM) and Event Handling in JavaScript**

*Lab Experiment 8 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

The Document Object Model (DOM) is the tree of objects that the browser builds from an HTML page. JavaScript can read and change this tree to update what the user sees. Events (clicks, key presses, form submissions and so on) are how the page responds to the user. This experiment demonstrates both with six small programs on one page.

Objectives:

- Select elements and change their text, HTML, style, classes and attributes.
- Create, insert and remove elements dynamically.
- Move around the DOM tree (parent, children, siblings).
- Handle mouse, keyboard and form events.
- Understand the event object, `preventDefault()`, bubbling, capturing, `stopPropagation()` and event delegation.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Structure | HTML5 | Elements that the scripts select and change |
| Styling | CSS3 | Layout, highlight classes, light and dark theme |
| Logic | JavaScript (ES6) | DOM manipulation and event listeners |
| Tools | VS Code, Chrome / Edge DevTools | Writing and inspecting the page |

## 3. How to Run

1. Keep `index.html` in a folder named `exp8-dom-events`.
2. Open it in Chrome or Edge (double-click it, or use the Live Server extension in VS Code).
3. Each program prints what it does in a green log box under it. No installation or server is needed.

## 4. Project Structure

```
exp8-dom-events/
├── index.html    # HTML, CSS and JavaScript in one file (six programs)
└── REPORT.md     # This report
```

## 5. Programs

### 5.1 Program 1: Selecting and changing elements

**Aim:** To select elements and change their content, style, classes and attributes.

| Method / property | What it does |
|---|---|
| `getElementById("id")` | Returns the one element with that id |
| `querySelector` / `querySelectorAll` | Select by CSS selector (first match / all matches) |
| `textContent` | Reads or sets plain text (safe for user input) |
| `innerHTML` | Reads or sets HTML inside an element (use only with trusted text) |
| `style.color = "..."` | Changes inline CSS |
| `classList.toggle("highlight")` | Adds or removes a class |
| `setAttribute` / `getAttribute` / `dataset` | Work with attributes and `data-*` values |

```js
document.getElementById("p1-text").addEventListener("click", () => {
    title.textContent = "Text changed with textContent";
});
```

**Expected result:** each button changes the heading or first paragraph, and the log shows the statement that ran. Reset restores the original state.

*Output:* *(screenshot)*

### 5.2 Program 2: Creating and removing elements

**Aim:** To build page content dynamically.

| Method | What it does |
|---|---|
| `document.createElement("li")` | Creates a new element in memory |
| `appendChild` / `append` | Adds it at the end of a parent |
| `insertBefore(new, reference)` | Adds it before another element (used for "Add to top") |
| `element.remove()` | Removes the element from the page |
| `replaceChildren()` | Removes all children at once |

```js
const li = document.createElement("li");
span.textContent = text;            // user text goes in through textContent
li.append(span, removeButton);
list.appendChild(li);
```

**Expected result:** typing a name and clicking Add to end / Add to top adds an item with its own Remove button. Clear all empties the list. An empty name is rejected with a message in the log.

*Output:* *(screenshot)*

### 5.3 Program 3: Traversing the DOM

**Aim:** To move from one element to related elements.

| Property | Returns |
|---|---|
| `parentElement` | The parent element |
| `children` | The child elements |
| `previousElementSibling` / `nextElementSibling` | The neighbouring elements |
| `firstElementChild` / `lastElementChild` | The first and last child |

**Expected result:** clicking an item (for example "Cherry") highlights it and logs its parent (`ul id='p3-list'`), previous (Banana), next (Mango) and its index (2 of 5). Clicking the first or last item shows `none` for the missing neighbour. The First child and Last child buttons do the same through code.

*Output:* *(screenshot)*

### 5.4 Program 4: Mouse and keyboard events

**Aim:** To react to mouse and keyboard activity using the event object.

| Event | Fires when |
|---|---|
| `mouseenter` / `mouseleave` | The pointer enters or leaves the box |
| `click` / `dblclick` | The box is clicked once or twice |
| `mousemove` | The pointer moves (the log is limited to one line every 0.4 seconds) |
| `keydown` / `keyup` | A key is pressed or released in the text field |

Useful event properties: `e.offsetX`, `e.offsetY` (position inside the box), `e.key` (the character), `e.code` (the physical key), `e.shiftKey`, `e.ctrlKey`.

**Expected result:** the box changes colour on hover and turns yellow briefly on double-click. Typing `A` with Shift logs `keydown key='A' code=KeyA +Shift`.

*Output:* *(screenshot)*

### 5.5 Program 5: Form events

**Aim:** To handle focus, typing, selection changes and form submission.

| Event | Fires when |
|---|---|
| `focus` / `blur` | A field gains or loses focus |
| `input` | The value changes on every keystroke (used for the 0 / 20 counter) |
| `change` | A select box or checkbox changes its value |
| `submit` | The form is submitted |
| `reset` | The form is reset |

```js
form.addEventListener("submit", (e) => {
    e.preventDefault();                  // stops the page from reloading
    const data = new FormData(form);
    console.log(data.get("name"));
});
```

**Expected result:** the log shows each focus, blur, input and change. Submit does not reload the page; instead it logs the entered name, email, city and newsletter choice.

*Output:* *(screenshot)*

### 5.6 Program 6: Bubbling, capturing and event delegation

**Aim:** To understand how an event travels through nested elements, and how to handle many elements with one listener.

| Concept | Meaning |
|---|---|
| Bubbling (default) | The event runs on the clicked element first, then on its parents, upwards |
| Capturing | The event runs on the outermost parent first and goes down to the target |
| `stopPropagation()` | Stops the event from reaching other elements |
| `preventDefault()` | Cancels the browser's default action (such as opening a link) |
| Event delegation | One listener on a parent handles clicks on all its children, even ones added later |

**Expected results:**

| Setting | Clicking the green box logs |
|---|---|
| Default (bubbling) | `inner` (target phase), then `middle`, then `outer` (bubble phase) |
| Use capture phase ticked | `outer` (capture phase), then `middle`, then `inner` |
| stopPropagation ticked | Only `inner`, then a line saying propagation stopped |

For delegation, clicking any list item marks it as done, and items added with Add item work immediately without adding a new listener. Clicking the link logs that its default action was prevented and the page does not open.

*Output:* *(screenshots for the three settings)*

## 6. Event Handling Summary

| Way to attach a handler | Example | Note |
|---|---|---|
| Inline attribute | `<button onclick="go()">` | Mixes HTML and JavaScript; avoid in larger pages |
| DOM property | `btn.onclick = go;` | Only one handler per event |
| `addEventListener` (used here) | `btn.addEventListener("click", go);` | Many handlers per event; supports capture and removal |

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Button did nothing | Script ran before the element existed, or the id was misspelled | Place the script at the end of `<body>` and check the id |
| `Cannot read properties of null` | `getElementById` returned `null` | Check the id in the HTML matches the id in the script |
| Form submit reloaded the page and the log vanished | Default form submission | Call `e.preventDefault()` in the `submit` handler |
| Clicking a new list item did nothing | A listener was added only to items that existed at load time | Use event delegation on the parent list |
| Clicking a button inside a list item also triggered the item's handler | Event bubbled up to the parent | Handle the event on the button, or call `stopPropagation()` |
| Capture checkbox did not change the order | The listener was added only once with the old setting | Remove and re-add the listeners when the checkbox changes |
| `mousemove` flooded the log | The event fires many times per second | Limit logging with a time check |

*(Keep only the problems you actually faced.)*

## 8. Testing

| Test | Expected Result |
|---|---|
| Program 1: click each button | Heading or paragraph changes, log shows the statement; Reset restores the original |
| Program 2: add three items, remove the middle one | List shows the two remaining items; the log shows the count |
| Program 2: click Add with an empty field | "Type an item name first" is logged; nothing is added |
| Program 3: click Banana | Previous: Apple, next: Cherry, index 1 of 5 |
| Program 3: click the last item | Next is `none` |
| Program 4: hover, click, double-click the box | Log shows `mouseenter`, `click` with x and y, `dblclick`; box colour changes |
| Program 4: type `a` in the field | `keydown` and `keyup` lines with `key='a'` |
| Program 5: type in Name | Counter updates (for example 5 / 20) and each `input` is logged |
| Program 5: fill the form and Submit | Page does not reload; values are logged |
| Program 6: click the green box (default) | Order: inner, middle, outer |
| Program 6: tick capture, click the green box | Order: outer, middle, inner |
| Program 6: tick stopPropagation, click the green box | Only inner runs |
| Program 6: Add item, then click the new item | New item toggles done without extra code |
| Program 6: click the link | Page does not open; log message appears |

*Output:* *(screenshots of the main tests)*

## 9. Limitations and Future Scope

Current limitations:

- The programs are demonstrations; the data is not saved and is lost on refresh.
- The `innerHTML` example uses a fixed string. Using `innerHTML` with user input would be unsafe.
- Only mouse and keyboard events are covered; touch, drag and drop, and scroll events are not.

Possible improvements:

- Save items with `localStorage` (see Assignment 01).
- Add drag and drop, touch events, and `IntersectionObserver` for scroll effects.
- Build a complete small application (such as a to-do list or quiz) using these ideas.
- Add keyboard support and ARIA attributes so every action works without a mouse.

## 10. Conclusion

This experiment showed how JavaScript uses the DOM to read and change a web page, and how events make the page interactive. Elements were selected, changed, created, removed and traversed; mouse, keyboard and form events were handled; and the event object, `preventDefault()`, bubbling, capturing, `stopPropagation()` and event delegation were demonstrated in a working page. These ideas are the foundation of every interactive website and of front-end libraries and frameworks.

