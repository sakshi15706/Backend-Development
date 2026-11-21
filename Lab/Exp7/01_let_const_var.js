// Program 1: var vs let vs const (scope, hoisting, temporal dead zone)

console.log("--- var: function scoped and hoisted ---");
function varDemo() {
    console.log("before declaration:", hoisted);      // undefined (hoisted, not yet assigned)
    var hoisted = "I am var";
    if (true) {
        var inside = "var leaks out of the block";
    }
    console.log(inside);                              // still accessible
}
varDemo();

console.log("--- let: block scoped, temporal dead zone ---");
function letDemo() {
    try {
        console.log(tdz);                             // cannot be used before its declaration
    } catch (e) {
        console.log("Error:", e.name + " - " + e.message);
    }
    let tdz = "I am let";
    if (true) {
        let blockOnly = "visible only inside this block";
        console.log(blockOnly);
    }
    console.log("typeof blockOnly outside the block:", typeof blockOnly);
}
letDemo();

console.log("--- const: cannot be reassigned ---");
const PI = 3.14159;
try {
    PI = 3;
} catch (e) {
    console.log("Error:", e.name + " - " + e.message);
}
const student = { name: "Sakshi" };
student.name = "Riya";                                // allowed: the object itself can change
console.log("const object after change:", student);

console.log("--- classic loop closure problem ---");
const withVar = [];
for (var i = 0; i < 3; i++) withVar.push(() => i);
console.log("var:", withVar.map((f) => f()));         // [3, 3, 3]
const withLet = [];
for (let j = 0; j < 3; j++) withLet.push(() => j);
console.log("let:", withLet.map((f) => f()));         // [0, 1, 2]
