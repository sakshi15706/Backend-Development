# Simple CMS

**A Blog Content Management System using Node.js, Express, EJS and MongoDB**

*Backend Development Lab Examination – Project Report*

Student: Sakshi | GitHub: https://github.com/sakshi15706/cms-app

## 1. Introduction and Objective

Simple CMS is a web application that lets users create blog posts, view a list of all posts and open any individual post by clicking its title. It is built with Node.js and Express.js on the server, EJS for server-side templates, and MongoDB for permanent storage.

Objectives:

- Build a working backend application with routing, form handling and database operations.
- Store posts permanently in MongoDB so data survives a browser refresh or a server restart.
- Render every page on the server using EJS templates.
- Generate the creation date and time automatically on the server, not from user input.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Runtime | Node.js | Runs JavaScript on the server |
| Web framework | Express.js | Routing, request handling, static files |
| Template engine | EJS | Server-side HTML rendering |
| Database | MongoDB | Permanent document storage |
| DB library | MongoDB Node.js Driver | Connects the app to MongoDB |
| Version control | Git and GitHub | Code hosting and submission |

## 3. Installation

### 3.1 Prerequisites

- Node.js installed (check with `node -v`).
- MongoDB server running at `mongodb://127.0.0.1:27017`.
- A code editor such as VS Code, and a web browser.

### 3.2 Steps

1. Open a terminal inside the project folder `cms-lab`.
2. Install the required packages:

```
   npm install
```

   (From scratch this is equivalent to `npm init -y` and `npm install express ejs mongodb`.)

3. Make sure the MongoDB service is running.
4. Start the application:

```
   node app.js
```

5. The terminal should print `Connected to MongoDB` and `Simple CMS running at http://localhost:3000`.
6. Open http://localhost:3000 in the browser.

### 3.3 Database Configuration

| Setting | Value |
|---|---|
| MongoDB URL | mongodb://127.0.0.1:27017 |
| Database | cms_lab |
| Collection | posts |

The database and collection are created automatically by MongoDB when the first post is inserted, so no manual setup is required.

## 4. Project Structure

```
cms-lab/
├── app.js            # Node.js entry point (server, routes, DB)
├── package.json      # Project details and dependencies
├── README.md         # Execution instructions
├── views/
│   ├── posts.ejs     # List of posts
│   ├── new-post.ejs  # Create-post form
│   └── post.ejs      # Individual post
└── public/
    └── style.css     # Styling
```

## 5. Working of the Application

### 5.1 Routes

| Method | Route | Purpose |
|---|---|---|
| GET | `/` or `/posts` | Fetches all posts (title, author, date only) and shows them as a list |
| GET | `/posts/new` | Displays the create-post form |
| POST | `/posts` | Validates form data, inserts the post, redirects to the list |
| GET | `/posts/:id` | Fetches one post by its ObjectId and displays the complete post |

### 5.2 Application Flow

```
Post List (/posts)
   |
   +----> Create Post (/posts/new) --submit--> saved --redirect--> Post List
   |
   +----> Click Post Title (/posts/:id)
               |
               +----> Complete Post
```

### 5.3 How each feature works

**Display all posts.** The server reads posts with `find()`, sorts them by `createdAt` in descending order so the newest post appears first, and passes them to `posts.ejs`. Only title, author and createdAt are requested from the database; the full content is not sent to the list page. Each title is a link to `/posts/<id>`.

**Create a post.** The form in `new-post.ejs` has three fields: Title, Content and Author. When submitted, the server trims the values and checks that none is empty. If a field is empty, the form is shown again with an error message and nothing is saved. Otherwise the post is inserted using `insertOne()` and the user is redirected to the post list.

```js
await postsCollection.insertOne({
  title, content, author,
  createdAt: new Date()   // generated on the server
});
```

**View an individual post.** The id from the URL is converted with `new ObjectId(req.params.id)` and used in `findOne()`. The complete post (title, author, date and content) is displayed by `post.ejs`. An invalid or unknown id shows "Post not found" with a 404 status instead of crashing.

**Server-side templates.** All pages are rendered with EJS. Values are printed with `<%= %>`, which also escapes HTML and protects against script injection, and loops such as `forEach` are used to list posts.

**Persistence.** Posts are stored in MongoDB and not in memory, so they remain available after a page refresh and after the Node.js server is restarted.

## 6. Database Design

Each post is stored as a document in the `posts` collection:

```json
{
  "_id": "ObjectId(...)",
  "title": "Introduction to MongoDB",
  "content": "MongoDB is a document-oriented database...",
  "author": "Priya",
  "createdAt": "ISODate(...)"
}
```

`_id` is generated by MongoDB and `createdAt` is generated by the server. A single `MongoClient` is created when the application starts and is reused for every request, instead of opening a new connection each time.

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| Browser shows "This site can't be reached" | Server was not running: MongoDB not connected, dependencies missing, or terminal in the wrong folder | Start MongoDB, run `npm install`, run `node app.js` inside `cms-lab`, and keep the terminal open |
| Page shows "No posts yet" | The posts collection was empty | Add posts using the Create Post form (or insert documents in mongosh) |
| `/posts/new` treated as a post id | Dynamic route `/posts/:id` matched "new" | Declare `/posts/new` before `/posts/:id` |
| Form values undefined in `req.body` | Form data was not being parsed | Add `express.urlencoded({ extended: true })` |
| Post not found for a valid id | Id from the URL is a string, but `_id` is an ObjectId | Convert with `new ObjectId(id)` |
| Duplicate posts on refresh after submit | Refreshing re-sent the POST request | Redirect to `/posts` after saving (Post/Redirect/Get) |
| Slow upload / push to GitHub | `node_modules` folder was included | Add `node_modules/` to `.gitignore` or skip it when uploading |

## 8. Testing

| Test | Expected Result |
|---|---|
| Open `/` with no posts | Message "No posts yet" is shown |
| Create a post with all three fields filled | Redirected to list; new post appears at the top |
| Submit the form with an empty field | Form shown again with an error; nothing saved |
| Click a post title | Complete post is displayed |
| Open `/posts/invalidid` | "Post not found" (404), no crash |
| Refresh page and restart server | All posts are still present |
| Check date on a new post | Date is generated by the server, not typed by the user |

## 9. Limitations and Future Scope

Current limitations:

- There is no user login, so anyone can create posts.
- Posts cannot be edited or deleted.
- The author name is typed manually and is not linked to an account.
- All posts are shown on one page without pagination.

Possible improvements:

- User registration and login with sessions.
- Edit and delete options for posts.
- Pagination, search, categories or tags.
- Comments, image uploads and a rich-text editor.
- Deployment on a cloud platform with MongoDB Atlas.

## 10. Conclusion

The Simple CMS project meets all compulsory requirements of the lab examination. It lists posts, creates posts with validation, shows each post by its unique id, renders pages with EJS on the server, generates the creation time on the backend and stores all data permanently in MongoDB. Working on it gave practical experience with Express routing, form handling, template engines, MongoDB operations, debugging and publishing a project on GitHub.