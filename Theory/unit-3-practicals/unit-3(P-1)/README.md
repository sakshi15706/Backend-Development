# Unit 3 (P-1): Introduction to Express.js (Lecture 25)

**PBL:** set up the Student Management API skeleton with Express. Create the project, install dependencies and write `app.js` so that `/` answers **"API is running"**.

**Assessment evidence:** `package.json` + `app.js` showing a running Express server.

## Steps (this is how this folder was created)
```bash
mkdir express-api && cd express-api
npm init -y
npm install express
# then write app.js
```
In this folder those are already done; you only need:

```bash
cd "unit-3(P-1)"
npm install
npm start            # Server running on http://localhost:3000
```
Open http://localhost:3000 or run `curl http://localhost:3000/` and you should see `API is running`.

## Test
```bash
npm test
```
3 tests: `/` returns 200 and the text, an unknown route returns 404, and malformed JSON is rejected (proves `express.json()` is in the pipeline).

## Understand it (viva points)
- Express is a minimal framework over Node's built-in `http` module.
- **Middleware pipeline:** every request passes through functions registered with `app.use()` before reaching a route handler. `express.json()` parses JSON bodies into `req.body`.
- `app.get('/', handler)` registers a route for `GET /`.
- `app.listen(PORT)` starts the server. `require.main === module` is true only when you run `node app.js`, so tests can import the app without opening a port.

## Mapping to the evaluation table
| Criterion | Evidence |
|---|---|
| Environment setup | `package.json` with the `express` dependency |
| Server functionality | `app.js` listens and responds to `/` |
