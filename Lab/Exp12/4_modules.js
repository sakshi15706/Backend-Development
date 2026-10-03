// Program 4b: Using a custom module and built-in modules with require()
// Run:  node 4_modules.js        (needs 4_mathModule.js in the same folder)

const math = require("./4_mathModule");     // "./" means a file of our own
const os = require("os");                   // built-in module (no "./")

console.log("add(10, 5)       =", math.add(10, 5));
console.log("subtract(10, 5)  =", math.subtract(10, 5));
console.log("multiply(10, 5)  =", math.multiply(10, 5));
console.log("divide(10, 5)    =", math.divide(10, 5));
console.log("factorial(6)     =", math.factorial(6));
console.log("PI               =", math.PI);

console.log("\nPrime numbers up to 30:");
const primes = [];
for (let i = 1; i <= 30; i++) {
  if (math.isPrime(i)) { primes.push(i); }
}
console.log(primes.join(", "));

// Error handling with try...catch
try {
  console.log("\ndivide(5, 0) =", math.divide(5, 0));
} catch (err) {
  console.log("\nError caught:", err.message);
}

// Destructuring only what we need
const { add, multiply } = require("./4_mathModule");
console.log("\nDestructured: add(2, 3) =", add(2, 3), "| multiply(2, 3) =", multiply(2, 3));

// A module is loaded once and cached
console.log("Same module object both times?", require("./4_mathModule") === math);
console.log("Platform:", os.platform());
