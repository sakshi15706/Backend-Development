// P-5: localStorage, sessionStorage and JSON

const NOTES_KEY = "notes";
const VISITS_KEY = "sessionVisits";

// ---------- 1. localStorage notes (stored as a JSON string) ----------
const noteForm = document.getElementById("noteForm");
const noteInput = document.getElementById("noteInput");
const noteList = document.getElementById("noteList");

function loadNotes() {
  try {
    return JSON.parse(localStorage.getItem(NOTES_KEY)) || [];
  } catch {
    return [];
  }
}

function saveNotes(notes) {
  localStorage.setItem(NOTES_KEY, JSON.stringify(notes));
}

function renderNotes() {
  const notes = loadNotes();
  noteList.innerHTML = "";
  if (notes.length === 0) {
    noteList.innerHTML = "<li><em>No notes yet</em></li>";
    return;
  }
  notes.forEach((note) => {
    const li = document.createElement("li");
    const text = document.createElement("span");
    text.textContent = `${note.text} (${note.createdAt})`;
    const del = document.createElement("button");
    del.textContent = "Delete";
    del.className = "danger";
    del.addEventListener("click", () => {
      saveNotes(loadNotes().filter((n) => n.id !== note.id));
      renderNotes();
    });
    li.append(text, del);
    noteList.appendChild(li);
  });
}

noteForm.addEventListener("submit", (e) => {
  e.preventDefault();
  const notes = loadNotes();
  notes.push({
    id: Date.now(),
    text: noteInput.value.trim(),
    createdAt: new Date().toLocaleString(),
  });
  saveNotes(notes);
  noteInput.value = "";
  renderNotes();
});

document.getElementById("clearNotes").addEventListener("click", () => {
  localStorage.removeItem(NOTES_KEY);
  renderNotes();
});

// ---------- 2. sessionStorage visit counter ----------
const visitInfo = document.getElementById("visitInfo");

function updateVisits() {
  const count = Number(sessionStorage.getItem(VISITS_KEY) || 0) + 1;
  sessionStorage.setItem(VISITS_KEY, count);
  visitInfo.textContent = `You opened this page ${count} time(s) in this tab session.`;
}

document.getElementById("resetVisits").addEventListener("click", () => {
  sessionStorage.removeItem(VISITS_KEY);
  visitInfo.textContent = "Session counter reset. Reload the page to start again.";
});

// ---------- 3. JSON demo ----------
document.getElementById("jsonDemo").addEventListener("click", () => {
  const student = {
    name: "Aman",
    semester: 5,
    subjects: ["Backend Development", "DBMS"],
    address: { city: "Dehradun", state: "Uttarakhand" },
  };
  const jsonString = JSON.stringify(student, null, 2);
  const parsed = JSON.parse(jsonString);

  document.getElementById("jsonOutput").textContent =
    "Object -> JSON string:\n" + jsonString +
    "\n\nJSON string -> Object:\nname = " + parsed.name +
    "\nsubjects[0] = " + parsed.subjects[0] +
    "\ntypeof parsed = " + typeof parsed;
});

// ---------- 4. Storage inspector ----------
document.getElementById("inspect").addEventListener("click", () => {
  const dump = (store) =>
    Object.fromEntries(Object.keys(store).map((k) => [k, store.getItem(k)]));
  document.getElementById("storageOutput").textContent = JSON.stringify(
    { localStorage: dump(localStorage), sessionStorage: dump(sessionStorage) },
    null,
    2
  );
});

renderNotes();
updateVisits();
