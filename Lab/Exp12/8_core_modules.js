// Program 8: Useful built-in modules - path, os, url, querystring, util, process
// Run:  node 8_core_modules.js

const path = require("path");
const os = require("os");
const util = require("util");
const querystring = require("querystring");

console.log("=== path module ===");
const p = "/home/sakshi/projects/app/index.html";
console.log("basename  :", path.basename(p));
console.log("dirname   :", path.dirname(p));
console.log("extname   :", path.extname(p));
console.log("join      :", path.join("folder", "sub", "file.txt"));
console.log("parse     :", path.parse(p));
console.log("is absolute?", path.isAbsolute(p));

console.log("\n=== os module ===");
console.log("Platform      :", os.platform());
console.log("CPU cores     :", os.cpus().length);
console.log("Total memory  :", (os.totalmem() / 1024 / 1024 / 1024).toFixed(2), "GB");
console.log("Free memory   :", (os.freemem() / 1024 / 1024 / 1024).toFixed(2), "GB");
console.log("Home directory:", os.homedir());

console.log("\n=== URL (WHATWG) ===");
const u = new URL("https://example.com:8080/products/list?category=books&page=2#top");
console.log("protocol :", u.protocol);
console.log("hostname :", u.hostname);
console.log("port     :", u.port);
console.log("pathname :", u.pathname);
console.log("search   :", u.search);
console.log("hash     :", u.hash);
console.log("category :", u.searchParams.get("category"));
console.log("page     :", u.searchParams.get("page"));
u.searchParams.append("sort", "price");
console.log("after append:", u.href);

console.log("\n=== querystring module ===");
console.log("parse    :", querystring.parse("name=Sakshi&city=Meerut&age=20"));
console.log("stringify:", querystring.stringify({ course: "CSE", year: 2 }));

console.log("\n=== util module ===");
console.log("format :", util.format("%s is %d years old", "Rahul", 20));
console.log("inspect:", util.inspect({ a: 1, b: { c: [1, 2, 3] } }, { depth: null }));

// util.promisify turns a callback function into a Promise-based one
const wait = util.promisify((ms, cb) => setTimeout(() => cb(null, "waited " + ms + " ms"), ms));
wait(300).then((msg) => console.log("promisify:", msg));

console.log("\n=== process object ===");
console.log("Node version :", process.version);
console.log("Current folder:", process.cwd());
console.log("Arguments    :", process.argv.slice(2));
console.log("Environment variable PORT:", process.env.PORT || "(not set)");
process.on("exit", (code) => console.log("\nProgram finished with code", code));
