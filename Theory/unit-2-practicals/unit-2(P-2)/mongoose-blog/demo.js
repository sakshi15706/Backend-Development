// Needs a running MongoDB:  mongodb://127.0.0.1:27017  (local install, Docker, or a free Atlas URI)
//   MONGO_URI="mongodb://127.0.0.1:27017/blog_app" npm start
const mongoose = require("mongoose");
const { Post, Comment } = require("./models");

const MONGO_URI = process.env.MONGO_URI || "mongodb://127.0.0.1:27017/blog_app";

async function main() {
  await mongoose.connect(MONGO_URI);
  await Post.deleteMany({});
  await Comment.deleteMany({});
  await Post.init(); // make sure the unique index exists

  const post = await Post.create({
    title: "My first post",
    slug: "my-first-post",
    content: "Hello from Mongoose",
    author: "Aarav",
    status: "published",
    tags: ["intro", "mongo"],
  });
  await Comment.create({ post: post._id, author: "Diya", email: "Diya@UPES.ac.in", text: "Great post!" });
  await Comment.create({ post: post._id, author: "Rohan", email: "rohan@upes.ac.in", text: "Thanks for sharing" });

  const withComments = await Post.findById(post._id).populate("comments");
  console.log(`"${withComments.title}" has ${withComments.comments.length} comments`);

  console.log("\n-- validation errors --");
  try {
    await Post.create({ title: "x", slug: "Bad Slug", content: "c", author: "a", status: "deleted" });
  } catch (e) {
    Object.values(e.errors).forEach((err) => console.log(" -", err.message));
  }

  console.log("\n-- unique constraint --");
  try {
    await Post.create({ title: "Duplicate", slug: "my-first-post", content: "c", author: "a" });
  } catch (e) {
    console.log(" - duplicate key error code:", e.code); // 11000
  }

  await mongoose.disconnect();
}

main().catch((e) => { console.error(e); process.exit(1); });
