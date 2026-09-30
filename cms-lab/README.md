# Simple CMS – Backend Development Lab Examination
Stack: **Option A** – Node.js + Express.js, EJS, MongoDB Node.js Driver

## Prerequisites
- Node.js installed
- MongoDB server already running at `mongodb://127.0.0.1:27017`
  - Database: `cms_lab`
  - Collection: `posts`

## Execution instructions
1. Open a terminal inside the `cms-lab` folder.
2. Install packages:
   ```
   npm install
   ```
   (Starting from scratch this is `npm init -y` then `npm install express ejs mongodb`.)
3. Start the application:
   ```
   node app.js
   ```
   The terminal should print `Connected to MongoDB` and `Simple CMS running at http://localhost:3000`.
4. Open http://localhost:3000 in the browser.

## How to use
- `/` or `/posts` – list of all posts (title, author, date). Click a title to read the post.
- `/posts/new` – create-post form (title, content, author).
- Submitting the form validates the three fields, inserts the post into MongoDB, generates `createdAt` on the server and redirects to the post list.
- `/posts/:id` – complete post, fetched from MongoDB by its `ObjectId`.

## Routes
| Method | Route           | Purpose               |
|--------|-----------------|-----------------------|
| GET    | `/` or `/posts` | Display all posts     |
| GET    | `/posts/new`    | Display create form   |
| POST   | `/posts`        | Create a new post     |
| GET    | `/posts/:id`    | Display complete post |

## Document format
```json
{ "title": "...", "content": "...", "author": "...", "createdAt": "Date (server generated)" }
```
`_id` is generated automatically by MongoDB.

## Project structure
```
cms-lab/
├── app.js            # Node.js entry point
├── package.json
├── views/
│   ├── posts.ejs     # List of posts
│   ├── new-post.ejs  # Create-post form
│   └── post.ejs      # Individual post
└── public/
    └── style.css
```
