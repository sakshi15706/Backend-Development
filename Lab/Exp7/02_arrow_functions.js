// Program 2: Arrow functions

// Regular function vs arrow function
function addOld(a, b) { return a + b; }
const add = (a, b) => a + b;                          // implicit return
const square = (n) => n * n;                          // one parameter
const greet = () => "Hello, ES6!";                    // no parameters
const makeUser = (name, age) => ({ name, age });      // returning an object needs ( )

console.log("addOld(2, 3) =", addOld(2, 3));
console.log("add(2, 3) =", add(2, 3));
console.log("square(5) =", square(5));
console.log(greet());
console.log("makeUser:", makeUser("Aman", 21));

// Arrow functions with array methods
const marks = [45, 78, 92, 33, 67];
console.log("passed (>= 40):", marks.filter((m) => m >= 40));
console.log("with grace +5:", marks.map((m) => m + 5));
console.log("total:", marks.reduce((sum, m) => sum + m, 0));

// "this": regular methods get their own this, arrows use the surrounding this
const person = {
    name: "Aman",
    regularFn: function () { return "regular: " + this.name; },
    arrowFn: () => "arrow: " + this.name,             // this is NOT the person object here
    delayedList() {
        // arrow inside a method keeps the method's this
        return [1, 2].map((n) => this.name + n);
    }
};
console.log(person.regularFn());
console.log(person.arrowFn());
console.log("arrow inside method:", person.delayedList());
