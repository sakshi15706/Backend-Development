# Unit 1 (P-1): Node.js and Express Environment

## Aim
Set up Node.js, npm and Express, and build a small server with routes and middleware.

## Run
```bash
cd "unit-1(P-1)"
npm install
npm start        # or: npm run dev  (auto-restart with nodemon)
```

## Test
- http://localhost:3000/
- http://localhost:3000/about
- http://localhost:3000/api/time
- `curl -X POST http://localhost:3000/api/echo -H "Content-Type: application/json" -d '{"name":"test"}'`

## Concepts covered
Node.js runtime, npm, `package.json`, Express routing, middleware, JSON responses, 404 handling.
