// Program 5: Spread operator, rest parameters and default parameters

// Spread with arrays
const fruits = ["apple", "banana"];
const veggies = ["carrot", "peas"];
const basket = [...fruits, "mango", ...veggies];
console.log("basket:", basket);

const copy = [...fruits];                             // shallow copy
copy.push("grapes");
console.log("original:", fruits, "| copy:", copy);

// Spread with function calls
const numbers = [4, 9, 2, 7];
console.log("max:", Math.max(...numbers), "| min:", Math.min(...numbers));

// Spread with objects
const base = { name: "Aman", age: 20 };
const updated = { ...base, age: 21, city: "Delhi" };  // later keys override
console.log("updated:", updated);

// Rest parameters: collect extra arguments into an array
function sum(...nums) {
    return nums.reduce((total, n) => total + n, 0);
}
console.log("sum(1, 2, 3) =", sum(1, 2, 3));
console.log("sum(10, 20, 30, 40) =", sum(10, 20, 30, 40));

function introduce(first, second, ...others) {
    return `${first}, ${second} and ${others.length} more`;
}
console.log(introduce("A", "B", "C", "D", "E"));

// Default parameters
function greet(name = "Guest", greeting = "Hello") {
    return `${greeting}, ${name}!`;
}
console.log(greet());
console.log(greet("Sakshi"));
console.log(greet("Sakshi", "Welcome"));
console.log(greet(undefined, "Hi"));                  // undefined triggers the default

// Default can be an expression using earlier parameters
const area = (w, h = w) => w * h;
console.log("area(5) =", area(5), "| area(5, 2) =", area(5, 2));
