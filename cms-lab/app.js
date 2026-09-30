const express = require("express");
const { MongoClient, ObjectId } = require("mongodb");

const app = express();
const PORT = process.env.PORT || 3000;

// ---- MongoDB (single shared client, reused for every request) ----
const mongoURL = process.env.MONGO_URL || "mongodb://127.0.0.1:27017";
const client = new MongoClient(mongoURL);
let postsCollection;

async function connectDB() {
  await client.connect();
  const database = client.db("cms_lab");
  postsCollection = database.collection("posts");
  console.log("Connected to MongoDB");
}

// ---- Express + EJS configuration ----
app.set("view engine", "ejs");
app.use(express.urlencoded({ extended: true })); // parse HTML form data
app.use(express.static("public"));               // serve CSS

// Format a Date as "26 September 2026"
app.locals.formatDate = (d) =>
  new Date(d).toLocaleDateString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
  });
// Date and time, used on the single-post page
app.locals.formatDateTime = (d) =>
  new Date(d).toLocaleString("en-GB", {
    day: "numeric", month: "long", year: "numeric",
    hour: "2-digit", minute: "2-digit",
  });

// ---- Routes ----

// Display all posts (content is NOT loaded for the list page)
async function listPosts(req, res, next) {
  try {
    const posts = await postsCollection
      .find({}, { projection: { title: 1, author: 1, createdAt: 1 } })
      .sort({ createdAt: -1 })
      .toArray();
    res.render("posts", { posts });
  } catch (err) { next(err); }
}
app.get("/", listPosts);
app.get("/posts", listPosts);

// Display create-post form (must be declared before /posts/:id)
app.get("/posts/new", (req, res) => {
  res.render("new-post", { errors: [], values: {} });
});

// Create a new post
app.post("/posts", async (req, res, next) => {
  try {
    const title = (req.body.title || "").trim();
    const content = (req.body.content || "").trim();
    const author = (req.body.author || "").trim();

    // Validation
    const errors = [];
    if (!title) errors.push("Title must not be empty.");
    if (!content) errors.push("Content must not be empty.");
    if (!author) errors.push("Author must not be empty.");

    if (errors.length > 0) {
      return res.status(400).render("new-post", {
        errors,
        values: { title, content, author },
      });
    }

    await postsCollection.insertOne({
      title,
      content,
      author,
      createdAt: new Date(), // generated on the server, never from the form
    });

    res.redirect("/posts");
  } catch (err) { next(err); }
});

// Display a complete post
app.get("/posts/:id", async (req, res, next) => {
  try {
    if (!ObjectId.isValid(req.params.id)) {
      return res.status(404).send("Post not found");
    }
    const post = await postsCollection.findOne({
      _id: new ObjectId(req.params.id),
    });
    if (!post) return res.status(404).send("Post not found");
    res.render("post", { post });
  } catch (err) { next(err); }
});

// Generic error handler
app.use((err, req, res, next) => {
  console.error(err);
  res.status(500).send("Something went wrong on the server.");
});

connectDB()
  .then(() => app.listen(PORT, () =>
    console.log(`Simple CMS running at http://localhost:${PORT}`)))
  .catch((err) => {
    console.error("Could not connect to MongoDB:", err.message);
    process.exit(1);
  });
