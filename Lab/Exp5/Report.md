# Experiment 5: Programs to Demonstrate JavaScript Array, Object and Functions

**Session:** 5  
**Course Outcome:** CO2  
**Student:** Sakshi  
**Date:** 22 September 2026  
**Files:** `index.html`, `style.css`, `script.js`

---

## 1. Aim

To write JavaScript programs that demonstrate arrays, objects and functions.

## 2. Software Requirements

| Item | Details |
|---|---|
| Editor | Visual Studio Code |
| Browser | Google Chrome / Microsoft Edge (Console through `F12`) |
| Languages | HTML5, CSS3, JavaScript (ES6) |
| Extension (optional) | Live Server |

## 3. Theory

### 3.1 Array

An **array** stores many values in one variable, in order. Each value has an index starting from 0.

```js
var fruits = ["Apple", "Banana", "Mango"];
console.log(fruits[0]);        // Apple
```

| Method | Purpose |
|---|---|
| `push()` / `pop()` | Add / remove at the end |
| `unshift()` / `shift()` | Add / remove at the start |
| `splice(i, n, ...items)` | Insert or remove at any position |
| `slice(start, end)` | Copy a part of the array |
| `concat()` | Join arrays |
| `indexOf()` / `includes()` | Search for a value |
| `sort()` / `reverse()` | Sort or reverse |
| `join()` | Convert to a string |
| `forEach()` | Run a function for each element |
| `map()` | Make a new array by changing each element |
| `filter()` | Make a new array with elements that pass a test |
| `reduce()` | Combine all elements into one value |
| `find()`, `some()`, `every()` | Search and test elements |

### 3.2 Object

An **object** stores data as **key : value** pairs (properties) and can also hold functions (methods).

```js
var student = { name: "Rahul", roll: 101, show: function () { return this.name; } };
console.log(student.name);       // dot notation
console.log(student["roll"]);    // bracket notation
```

| Concept | Purpose |
|---|---|
| Dot / bracket notation | Access properties |
| `delete obj.key` | Remove a property |
| `this` | Refers to the current object inside a method |
| `for...in`, `Object.keys()`, `Object.values()`, `Object.entries()` | Loop through an object |
| Nested objects, array of objects | Store complex data |
| Constructor function / `class` | Create many similar objects |
| `JSON.stringify()` / `JSON.parse()` | Convert between object and JSON text |

### 3.3 Function

A **function** is a block of code that runs when it is called. It makes code reusable.

```js
function add(a, b) { return a + b; }       // declaration
var sub = function (a, b) { return a - b; };   // expression
var mul = (a, b) => a * b;                  // arrow function
```

| Concept | Purpose |
|---|---|
| Parameters and `return` | Send values in and get a value out |
| Default parameters | `function f(a = 10)` |
| Rest parameter | `function f(...nums)` takes any number of arguments |
| Callback | A function passed as an argument to another function |
| Recursion | A function that calls itself, with a base case |
| Closure | An inner function that remembers the variables of its outer function |
| IIFE | A function that runs as soon as it is defined |
| Hoisting | Function declarations can be called before they are written |

## 4. Programs in the Experiment

### Part 1: Arrays

| No. | Program | Concepts |
|---|---|---|
| 1.1 | Creating and accessing | Literal and `new Array`, index, `length`, `Array.isArray` |
| 1.2 | Add and remove | `push`, `pop`, `shift`, `unshift`, `splice`, `concat` |
| 1.3 | Search, slice, sort | `indexOf`, `includes`, `slice`, `join`, `reverse`, `sort` (text and numeric) |
| 1.4 | Looping and higher-order | `for`, `for...of`, `forEach`, `map`, `filter`, `reduce`, `find`, `some`, `every` |
| 1.5 | Two-dimensional array | Matrix, diagonal sum, transpose |
| 1.6 | Interactive | Add numbers from an input box, show sum, average, largest, smallest and sorted array |

### Part 2: Objects

| No. | Program | Concepts |
|---|---|---|
| 2.1 | Create and access | Dot and bracket notation, `in`, `hasOwnProperty` |
| 2.2 | Add, update, delete | `delete`, `Object.assign`, spread, `Object.freeze` |
| 2.3 | Methods and `this` | `person.fullName()`, rectangle area and perimeter |
| 2.4 | Looping | `for...in`, `Object.keys/values/entries`, destructuring |
| 2.5 | Nested and array of objects | `JSON.stringify`, `JSON.parse`, filter and reduce on objects |
| 2.6 | Constructor and class | Constructor function, prototype, `class`, `extends`, `super`, `instanceof` |
| 2.7 | Interactive | Create student objects from a form and store them in an array |

### Part 3: Functions

| No. | Program | Concepts |
|---|---|---|
| 3.1 | Declaration | Parameters, return, hoisting, function returning an object |
| 3.2 | Expression and arrow | Different arrow function forms |
| 3.3 | Default and rest | Default values, `...rest`, `arguments`, spread |
| 3.4 | Callback | Passing functions, `setTimeout` (asynchronous) |
| 3.5 | Recursion | Factorial, Fibonacci, sum of n numbers |
| 3.6 | Closure | Counter, multiplier, bank account with a private balance |
| 3.7 | IIFE | Normal and arrow IIFE |
| 3.8 | Interactive | Calculator using an object of functions |

### Part 4: Combined program

**Student Result:** an **array of objects** (5 students with 3 subject marks) and **functions** (`total`, `percentage`, `grade`, `status`). It calculates total, percentage, grade and pass/fail, finds the topper with `reduce`, counts the passed students with `filter`, sorts students by total, and shows the result in an HTML table.

## 5. Procedure

1. Create a folder `experiment5` in VS Code.
2. Create `index.html`, `style.css` and `script.js` in it.
3. In `index.html`, make sections for arrays, objects and functions. Add a `<pre id="...">` output box for each program.
4. Link `style.css` in `<head>` and `script.js` before `</body>`.
5. In `script.js`, write a helper function `show(id, lines)` that prints the output in the page and in the console.
6. Write the array programs, then the object programs, then the function programs, then the combined program.
7. Add input boxes and buttons for the interactive programs (`onclick="addNumber()"` and so on).
8. Save the files and open `index.html` with Live Server.
9. Check the output boxes on the page, test every button, and press `F12` to see the same output in the **Console** tab.
10. Take screenshots.

## 6. Structure of the Code

```
experiment5/
├── index.html    # sections, output boxes, input boxes and buttons
├── style.css     # page and console-style output boxes
└── script.js     # all the JavaScript programs
```

### Key code snippets

**Array methods**

```js
var marks = [45, 82, 67, 90, 33, 74];
var passed = marks.filter(function (x) { return x >= 40; });
var total  = marks.reduce(function (sum, x) { return sum + x; }, 0);
```

**Object with a method**

```js
var person = {
  firstName: "Priya",
  lastName: "Sharma",
  fullName: function () { return this.firstName + " " + this.lastName; }
};
```

**Closure**

```js
function makeCounter() {
  var count = 0;
  return function () { count++; return count; };
}
var c1 = makeCounter();
c1();   // 1
c1();   // 2
```

**Recursion**

```js
function factorial(n) {
  if (n <= 1) { return 1; }
  return n * factorial(n - 1);
}
```

**Array of objects with functions**

```js
var final = results.map(function (s) {
  var p = percentage(s);
  return { name: s.name, total: total(s), grade: grade(p), status: status(s) };
});
```

## 7. Output

Take screenshots of the page and the browser console and paste them here:

```
![Arrays output](arrays.png)
![Objects output](objects.png)
![Functions output](functions.png)
![Console output](console.png)
```

### Sample output

| Program | Output |
|---|---|
| `fruits[0]` | `Apple` |
| `a.push(40)` on `[10,20,30]` | `[10,20,30,40]` |
| `marks.filter(x => x >= 40)` | `[45,82,67,90,74]` |
| `marks.reduce(...)` (total) | `391` |
| `person.fullName()` | `Priya Sharma` |
| `Object.keys(car)` | `["brand","model","year","color"]` |
| `factorial(5)` | `120` |
| Fibonacci (first 10) | `0, 1, 1, 2, 3, 5, 8, 13, 21, 34` |
| `triple(7)` (closure) | `21` |
| Combined program | Topper: Priya (275/300), 4 students passed, 1 failed |

## 8. Observations

- Arrays keep ordered data, and methods like `map`, `filter` and `reduce` process whole arrays in one line, without writing loops.
- `sort()` without a function sorts numbers as text (`[10, 100, 20]`), so a compare function `(a, b) => a - b` is needed for numbers.
- `slice()` does not change the original array, but `splice()`, `push()`, `pop()` and `sort()` do.
- Objects keep related data and behaviour together, and `this` refers to the object that calls the method.
- An arrow function does not have its own `this`, so it is not suitable as an object method.
- A closure keeps the variable alive after the outer function ends, which gives private data (the bank balance cannot be changed directly).
- Recursion needs a base case, otherwise the function calls itself forever.
- `setTimeout` runs its callback later, so the page does not wait and the callback output appears after 2 seconds.

## 9. Result

JavaScript programs demonstrating arrays, objects and functions were written and executed successfully, and the output was displayed correctly on the web page and in the browser console.

## 10. Conclusion

Arrays store lists of values, objects store related data as properties and methods, and functions make code reusable. Together, an array of objects processed by functions (as in the Student Result program) is the base of most real JavaScript applications.
