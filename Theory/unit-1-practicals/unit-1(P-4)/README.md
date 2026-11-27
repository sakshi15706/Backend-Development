# Unit 1 (P-4): Sessions, Cookies and Query Strings

## Aim
Demonstrate how state is kept across stateless HTTP requests using query strings, cookies and server-side sessions.

## Run
```bash
cd "unit-1(P-4)"
npm install
npm start
```
Open http://localhost:3000

## Routes
| Route | Shows |
|---|---|
| /search?q=express&page=2&sort=asc | reading `req.query` |
| /set-cookie?name=Aman, /get-cookie, /clear-cookie | setting, reading, deleting cookies |
| /login (password `1234`), /profile, /logout | session-based login |
| /visits | per-session visit counter |

## Notes
- Cookie data lives in the browser; session data lives on the server, and the browser only holds a session id cookie (`connect.sid`).
- Check cookies in DevTools: Application, Cookies.
- The default in-memory session store is for learning only, not production.
