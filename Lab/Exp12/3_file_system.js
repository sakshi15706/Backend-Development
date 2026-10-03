// Program 3: File System (fs) module - create, write, read, append, rename, list, delete
// Run:  node 3_file_system.js

const fs = require("fs");
const path = require("path");

// __dirname = folder of this file; path.join builds a correct path on any OS
const folder = path.join(__dirname, "demo_files");
const file = path.join(folder, "notes.txt");

console.log("=== 1. Create a folder ===");
if (!fs.existsSync(folder)) {
  fs.mkdirSync(folder);
}
console.log("Folder ready:", folder);

console.log("\n=== 2. Write a file (writeFileSync) ===");
fs.writeFileSync(file, "Line 1: Hello Node.js\n");
console.log("File written");

console.log("\n=== 3. Append to the file (appendFileSync) ===");
fs.appendFileSync(file, "Line 2: File System module\n");
fs.appendFileSync(file, "Line 3: Server-side scripting\n");
console.log("Text appended");

console.log("\n=== 4. Read the file (readFileSync) ===");
const content = fs.readFileSync(file, "utf8");
console.log(content);

console.log("=== 5. Count lines and words ===");
const lines = content.trim().split("\n");
const words = content.trim().split(/\s+/);
console.log("Lines:", lines.length, "| Words:", words.length, "| Characters:", content.length);

console.log("\n=== 6. File information (statSync) ===");
const info = fs.statSync(file);
console.log("Size in bytes :", info.size);
console.log("Is a file     :", info.isFile());
console.log("Is a folder   :", info.isDirectory());

console.log("\n=== 7. Copy and rename ===");
const copy = path.join(folder, "notes_copy.txt");
fs.copyFileSync(file, copy);
const renamed = path.join(folder, "notes_renamed.txt");
fs.renameSync(copy, renamed);
console.log("Files in folder:", fs.readdirSync(folder));

console.log("\n=== 8. Asynchronous read (readFile with a callback) ===");
fs.readFile(file, "utf8", (err, data) => {
  if (err) {
    console.log("Error:", err.message);
    return;
  }
  console.log("Async read finished. First line:", data.split("\n")[0]);

  console.log("\n=== 9. Reading a file that does not exist (error handling) ===");
  fs.readFile(path.join(folder, "missing.txt"), "utf8", (err2) => {
    console.log("Error caught:", err2.code);

    console.log("\n=== 10. Delete files and folder ===");
    fs.unlinkSync(file);
    fs.unlinkSync(renamed);
    fs.rmdirSync(folder);
    console.log("Deleted. Folder still exists?", fs.existsSync(folder));
  });
});

console.log("(This line prints BEFORE the async result, because readFile does not block.)");
