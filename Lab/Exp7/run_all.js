// Runs every program in this folder one after another:  node run_all.js
const { execFileSync } = require("child_process");
const fs = require("fs");

const files = fs.readdirSync(__dirname)
    .filter((f) => /^\d\d_.*\.(js|mjs)$/.test(f) && !f.includes("_math_module"))
    .sort();

for (const file of files) {
    console.log("\n==================== " + file + " ====================");
    console.log(execFileSync(process.execPath, [file], { cwd: __dirname }).toString());
}
