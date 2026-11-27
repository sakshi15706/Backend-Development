// P-2 Part 4 and 5: Mongoose schemas for a Blog application with validation rules
const mongoose = require("mongoose");

const postSchema = new mongoose.Schema(
  {
    title: {
      type: String,
      required: [true, "Title is required"],
      trim: true,
      minlength: [3, "Title must be at least 3 characters"],
      maxlength: [150, "Title cannot exceed 150 characters"],
    },
    slug: {
      type: String,
      required: [true, "Slug is required"],
      unique: true, // unique index
      lowercase: true,
      match: [/^[a-z0-9]+(?:-[a-z0-9]+)*$/, "Slug may only contain letters, numbers and hyphens"],
    },
    content: { type: String, required: [true, "Content is required"] },
    author: {
      type: String,
      required: [true, "Author is required"],
      trim: true,
    },
    status: {
      type: String,
      enum: {
        values: ["draft", "published", "archived"],
        message: "Status must be draft, published or archived",
      },
      default: "draft",
    },
    tags: { type: [String], default: [] },
  },
  { timestamps: true } // createdAt and updatedAt
);

const commentSchema = new mongoose.Schema(
  {
    post: {
      type: mongoose.Schema.Types.ObjectId, // reference to Post (1 Post : M Comments)
      ref: "Post",
      required: [true, "A comment must belong to a post"],
    },
    author: { type: String, required: [true, "Author is required"], trim: true },
    email: {
      type: String,
      required: [true, "Email is required"],
      lowercase: true,
      match: [/^\S+@\S+\.\S+$/, "Invalid email format"],
    },
    text: {
      type: String,
      required: [true, "Comment text is required"],
      minlength: [1, "Comment cannot be empty"],
      maxlength: [500, "Comment cannot exceed 500 characters"],
    },
  },
  { timestamps: true }
);

// virtual: all comments of a post (populate with .populate('comments'))
postSchema.virtual("comments", { ref: "Comment", localField: "_id", foreignField: "post" });

const Post = mongoose.model("Post", postSchema);
const Comment = mongoose.model("Comment", commentSchema);

module.exports = { Post, Comment };
