// Program 4: Destructuring

// Array destructuring
const colors = ["red", "green", "blue", "yellow"];
const [first, second] = colors;
const [, , third] = colors;                           // skip items
const [head, ...tail] = colors;                       // rest
console.log(first, second, third);
console.log("head:", head, "| tail:", tail);

// Swapping variables
let a = 1, b = 2;
[a, b] = [b, a];
console.log("after swap: a =", a, ", b =", b);

// Default values
const [x = 10, y = 20] = [5];
console.log("x =", x, ", y =", y);

// Object destructuring
const student = { id: 7, name: "Riya", city: "Dehradun", marks: { maths: 90, science: 85 } };
const { name, city } = student;
console.log(name, "-", city);

// Rename and default
const { name: studentName, grade = "A" } = student;
console.log(studentName, "grade:", grade);

// Nested
const { marks: { maths, science } } = student;
console.log("maths:", maths, "science:", science);

// In function parameters
function describe({ name, city = "Unknown" }) {
    return `${name} lives in ${city}`;
}
console.log(describe(student));
console.log(describe({ name: "Karan" }));

// Returning multiple values
const minMax = (arr) => [Math.min(...arr), Math.max(...arr)];
const [min, max] = minMax([4, 9, 1, 7]);
console.log("min:", min, "max:", max);
