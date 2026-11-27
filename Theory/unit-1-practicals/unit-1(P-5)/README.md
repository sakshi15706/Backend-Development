# Unit 1 (P-5): LocalStorage, SessionStorage and JSON

## Aim
Use the browser Web Storage APIs to store data on the client, and use JSON to serialise objects.

## Run
No installation needed. Open `index.html` in a browser, or use the VS Code "Live Server" extension.

## What it shows
| Feature | Lifetime |
|---|---|
| `localStorage` | stays until deleted, survives closing the browser |
| `sessionStorage` | cleared when the tab is closed |
| `JSON.stringify` / `JSON.parse` | needed because storage only holds strings |

Open DevTools, then Application, then Local Storage / Session Storage to see the stored values.
