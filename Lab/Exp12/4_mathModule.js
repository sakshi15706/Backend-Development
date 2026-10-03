// Program 4a: A custom module.
// Anything put in module.exports can be imported in another file with require().

function add(a, b) { return a + b; }
function subtract(a, b) { return a - b; }
function multiply(a, b) { return a * b; }
function divide(a, b) {
  if (b === 0) { throw new Error("Cannot divide by zero"); }
  return a / b;
}
function isPrime(n) {
  if (n < 2) { return false; }
  for (let i = 2; i * i <= n; i++) {
    if (n % i === 0) { return false; }
  }
  return true;
}
function factorial(n) {
  return n <= 1 ? 1 : n * factorial(n - 1);
}

const PI = 3.14159;

// Export what other files may use
module.exports = { add, subtract, multiply, divide, isPrime, factorial, PI };
