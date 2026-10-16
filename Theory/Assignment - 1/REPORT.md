# Notes App

**A Notes / Todo Application using HTML, CSS, JavaScript and localStorage**

*Backend Development: Assignment 01 Report (Unit 1, L07: localStorage, sessionStorage and JSON)*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

Notes App is a frontend-only web application that lets a user add, view, edit and delete notes. It is built with HTML, CSS and JavaScript, and all notes are stored in the browser's `localStorage`, so they remain after a page refresh. The assignment is to follow the Web Storage API tutorial and complete **Task 12: Build a Notes App**.

Objectives:

- Understand the Web Storage API: `localStorage`, `sessionStorage` and how they differ.
- Understand why objects must be converted with `JSON.stringify()` before saving and with `JSON.parse()` after reading.
- Build a working app with full CRUD (Create, Read, Update, Delete) using only frontend code.
- Persist data in `localStorage` so it survives a refresh.
- Store `id`, `text`, `createdAt` and `updatedAt` for every note.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Structure | HTML5 | Page layout, input box and buttons |
| Styling | CSS3 (CSS variables) | Card layout, light and dark theme |
| Logic | JavaScript (ES6) | CRUD functions, rendering, events |
| Storage | Web Storage API (`localStorage`) | Permanent storage in the browser |
| Data format | JSON | Converts note objects to strings and back |
| Tools | VS Code, Chrome / Edge DevTools | Writing code, inspecting storage |

## 3. How to Run

1. Keep `index.html` in a folder named `notes-app`.
2. Open the file in Chrome or Edge (double-click it, or right-click in VS Code and choose "Open with Live Server").
3. No installation, server or database is needed.

## 4. Project Structure

```
notes-app/
├── index.html    # HTML, CSS and JavaScript in one file
└── REPORT.md     # This report
```

## 5. Working of the Application

### 5.1 Data Structure (Step 1)

Each note is a JavaScript object. All notes are kept in one array and saved under the `localStorage` key `"notes"`.

```js
const note = {
    id: Date.now(),                       // unique ID
    text: "My first note",
    completed: false,
    createdAt: new Date().toISOString(),
    updatedAt: null                       // set when the note is edited
};
```

### 5.2 Functions

| Function | Purpose |
|---|---|
| `getNotes()` | Reads `"notes"` from localStorage, parses the JSON and returns an array (empty array if nothing is stored or parsing fails) |
| `saveNotes(notes)` | Converts the array to JSON and saves it under `"notes"` |
| `addNote(text)` | CREATE: validates, adds a new note, saves and re-renders |
| `updateNote(id, newText)` | UPDATE: changes the text, sets `updatedAt`, saves and re-renders |
| `deleteNote(id)` | DELETE: removes the note with that id, saves and re-renders |
| `toggleDone(id)` | Marks a note as done or not done |
| `editNote(id)`, `saveEdit(id)`, `cancelEdit()` | Switch a card into edit mode, save the edit, or cancel it |
| `renderNotes()` | Reads all notes and draws them on the page |
| `escapeHTML(str)` | Makes user text safe to place inside `innerHTML` |
| `toggleTheme()`, `loadTheme()` | Switch and restore light / dark mode |

### 5.3 Application Flow

```
Page opens --> window.onload --> renderNotes() --> reads "notes" from localStorage
                                                       |
   +---------------------+---------------------+-------+---------------+
   |                     |                     |                       |
Add Note             Edit / Save             Delete                  Done / Undo
addNote()            updateNote()            deleteNote()            toggleDone()
   |                     |                     |                       |
   +----------> saveNotes() --> localStorage --> renderNotes() <-------+
```

### 5.4 How each feature works

**Add a note.** The user types text and clicks Add Note (or presses Enter). The text is trimmed. If it is empty, an error message is shown and nothing is saved. Otherwise the note is pushed to the array, saved, and the input box is cleared.

```js
function addNote(text) {
    text = text.trim();
    if (text === "") { /* show error */ return; }
    const notes = getNotes();
    notes.push({ id: Date.now(), text: text, completed: false,
                 createdAt: new Date().toISOString(), updatedAt: null });
    saveNotes(notes);
    renderNotes();
}
```

**Display notes on page load.** `window.onload` calls `renderNotes()`, which reads the saved array and builds a card for each note using `map()` and `join("")`. If there are no notes, the message "No notes yet" is shown.

**Edit a note.** Clicking Edit turns the card into a text box with Save and Cancel buttons. Saving calls `updateNote()`, which finds the note with `find()`, changes its text and sets `updatedAt` to the current time. The card then shows both the created and updated times.

**Delete a note.** `deleteNote(id)` keeps every note except the one with that id, using `filter()`, then saves and re-renders.

**Persistence.** `localStorage` stores strings only, so the array is converted with `JSON.stringify()` when saving and with `JSON.parse()` when reading. Because the data lives in the browser, it remains after a refresh and after closing and reopening the tab.

### 5.5 Requirements Checklist

| Requirement | Status | Implemented by |
|---|---|---|
| Add a new note with text | Done | `addNote()` |
| Display all saved notes on page load | Done | `window.onload = renderNotes` |
| Delete individual notes | Done | `deleteNote()` |
| Edit existing notes | Done | `editNote()`, `updateNote()` |
| Data persists after refresh | Done | `localStorage` with JSON |
| Each note has id, text, createdAt, updatedAt | Done | Note object in `addNote()` |
| Mark notes complete / incomplete (stretch) | Done | `toggleDone()` |
| Search / filter notes (stretch) | Done | Search box in `renderNotes()` |
| Dark / light mode saved (stretch) | Done | `toggleTheme()`, key `"theme"` |
| Categories or tags, import / export, drag reorder (stretch) | Not done | Listed under Future Scope |

## 6. Storage Design

Two keys are used in `localStorage`:

| Key | Value |
|---|---|
| `notes` | JSON string of the array of notes |
| `theme` | `"dark"` or `"light"` |

Example of the stored `notes` value:

```json
[
  {
    "id": 1760600000000,
    "text": "Finish assignment",
    "completed": false,
    "createdAt": "2026-10-16T08:30:00.000Z",
    "updatedAt": null
  }
]
```

*Output:* *(screenshot of DevTools: Application, Local Storage, key `notes`)*

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Delete button did nothing | The `confirm()` pop-up was blocked in the editor's preview, so it returned false and cancelled the delete | Removed the pop-up and deleted directly in `deleteNote()` |
| Notes showed `[object Object]` or could not be used after reading | `localStorage` stores strings only | Used `JSON.stringify()` to save and `JSON.parse()` to read |
| App could crash on bad stored data | `JSON.parse()` throws an error if the string is not valid JSON | Wrapped it in `try...catch` inside `getNotes()` and returned an empty array |
| First visit failed with `null` | `getItem("notes")` returns `null` when nothing is saved | Checked `raw ? JSON.parse(raw) : []` |
| Typing HTML such as `<b>` in a note broke the layout | Text was inserted into `innerHTML` unescaped | Added `escapeHTML()` before inserting text |
| Empty notes were being saved | No validation | Trimmed the text and rejected empty input |
| Edit or delete targeted the wrong note | Notes were identified by position | Identified each note by its unique `id` |

## 8. Testing

| Test | Expected Result |
|---|---|
| Open the page with no saved notes | "No notes yet" message is shown |
| Add a note, then refresh | Note is still there |
| Delete a note, then refresh | Note is gone |
| Edit a note, then refresh | Updated text is kept and the Updated time is shown |
| Open the page in a new tab | Same notes appear (localStorage is shared) |
| DevTools, Application, Local Storage | Key `notes` is present with the JSON array |
| Try adding empty text | Not allowed; error message shown |
| Add a note containing `<b>test</b>` | Shown as plain text, not as bold |
| Click Done, then refresh | Note stays marked as done |
| Type in the search box | Only matching notes are shown |
| Switch to dark mode, then refresh | Dark mode is remembered |
| Console: `console.table(JSON.parse(localStorage.getItem("notes")))` | Table of all notes is printed |

*Output:* *(screenshots of the main tests)*

## 9. Limitations and Future Scope

Current limitations:

- Data is stored only in one browser on one device. Clearing browser data deletes all notes.
- There is no login, so anyone using the browser can see and change the notes.
- `localStorage` has a size limit of about 5-10 MB and can be edited by the user in DevTools.
- There is no server-side validation.

Possible improvements (from Section 13 of the tutorial, Expanding to a Backend):

- Add a Node.js and Express backend with a database such as MongoDB, and replace `getNotes()` and `saveNotes()` with `fetch("/api/notes")` calls.
- Add user login with tokens so each user sees only their own notes.
- Keep `localStorage` as a cache for fast loading and offline use, with the backend as the source of truth.
- Add categories or tags, import and export as a JSON file, and drag-to-reorder.

## 10. Conclusion

The Notes App meets all the compulsory requirements of Assignment 01. It adds, displays, edits and deletes notes, stores each note with `id`, `text`, `createdAt` and `updatedAt`, and keeps data permanently in `localStorage` through `JSON.stringify()` and `JSON.parse()`. Building it gave practical experience with the Web Storage API, JSON conversion, DOM rendering, input validation, safe handling of user text and testing with browser DevTools. It also showed why `localStorage` works well for small, per-browser data but should be paired with a backend and database for real applications.

## References

1. Tutorial: Web Storage API Tutorial, https://upessocs.github.io/Lectures/Backend%20Development/Theory/Unit%201/L07%20LocalStorage%20SessionStorage%20and%20JSON/
2. MDN Web Docs: Web Storage API, https://developer.mozilla.org/en-US/docs/Web/API/Web_Storage_API
3. MDN Web Docs: JSON.stringify() and JSON.parse(), https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/JSON
