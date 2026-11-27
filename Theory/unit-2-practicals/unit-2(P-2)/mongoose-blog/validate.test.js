// Checks the validation rules WITHOUT needing a running MongoDB.
//   npm test
const assert = require("assert");
const { Post, Comment } = require("./models");

function errorsOf(doc) {
  const err = doc.validateSync();
  return err ? Object.keys(err.errors) : [];
}

// valid post and comment
assert.deepStrictEqual(
  errorsOf(new Post({ title: "Hello World", slug: "hello-world", content: "text", author: "Aarav" })),
  []
);
console.log("ok  valid post passes");

// required fields
assert.deepStrictEqual(errorsOf(new Post({})).sort(), ["author", "content", "slug", "title"]);
console.log("ok  required fields enforced");

// enum
assert.ok(errorsOf(new Post({ title: "Hello", slug: "a", content: "x", author: "y", status: "deleted" })).includes("status"));
console.log("ok  enum rejects invalid status");

// slug pattern + title length
const bad = errorsOf(new Post({ title: "Hi", slug: "Not A Slug!", content: "x", author: "y" }));
assert.ok(bad.includes("title") && bad.includes("slug"));
console.log("ok  minlength and match rules enforced");

// default status
assert.strictEqual(new Post({}).status, "draft");
console.log("ok  default status is draft");

// comment rules
const post = new Post({});
assert.deepStrictEqual(errorsOf(new Comment({ post: post._id, author: "A", email: "a@b.co", text: "Nice" })), []);
assert.ok(errorsOf(new Comment({ post: post._id, author: "A", email: "nope", text: "Nice" })).includes("email"));
assert.ok(errorsOf(new Comment({ post: post._id, author: "A", email: "a@b.co", text: "x".repeat(501) })).includes("text"));
assert.ok(errorsOf(new Comment({ author: "A", email: "a@b.co", text: "Hi" })).includes("post"));
console.log("ok  comment validation (email format, max length, required post)");

// unique constraint is a DB index (checked when connected)
assert.strictEqual(Post.schema.path("slug").options.unique, true);
console.log("ok  slug declared unique");

console.log("\nAll validation checks passed.");
