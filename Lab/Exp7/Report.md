# ES6 Concepts

**Programs to Familiarise ES6 (ECMAScript 2015) Features**

*Lab Experiment 7 Report*

Student: Sakshi Jaiswal | Sap Id: 590015706

## 1. Introduction and Objective

ES6 (ECMAScript 2015) is a major update of JavaScript that added modern syntax such as `let` and `const`, arrow functions, classes, template literals, destructuring, promises and modules. This experiment demonstrates each concept with a small, runnable program.

Objectives:

- Understand block scoping with `let` and `const`.
- Write functions with arrow syntax and understand `this` in arrow functions.
- Use template literals, destructuring, the spread and rest operators, and default parameters.
- Create classes with inheritance, getters, setters, static members and private fields.
- Handle asynchronous code with promises and `async` / `await`.
- Use `Set`, `Map`, iterators and generators.
- Split code into modules with `import` and `export`.

## 2. Technology Stack

| Component | Technology | Purpose |
|---|---|---|
| Language | JavaScript (ES6 and later) | All programs |
| Runtime | Node.js | Runs the programs from the terminal |
| Editor | VS Code | Writing code |

## 3. How to Run

Install Node.js (check with `node -v`). Open the `exp7-es6` folder in VS Code, open the terminal (Ctrl + `) and run any program:

```
node 01_let_const_var.js
node 09_modules_main.mjs
```

To run all programs one after another:

```
node run_all.js
```

The programs can also be pasted into the browser console (F12, Console), except Program 9, which needs modules.

## 4. Project Structure

```
exp7-es6/
├── 01_let_const_var.js
├── 02_arrow_functions.js
├── 03_template_literals.js
├── 04_destructuring.js
├── 05_spread_rest_default.js
├── 06_classes.js
├── 07_promises_async.js
├── 08_map_set_generators.js
├── 09_math_module.mjs        # module that exports
├── 09_modules_main.mjs       # module that imports
├── run_all.js                # runs every program
└── REPORT.md
```

## 5. Programs and Output

### 5.1 Program 1: `var`, `let` and `const`

**File:** `01_let_const_var.js`

**Aim:** To understand scope, hoisting and the temporal dead zone, and why `let` and `const` replaced `var`.

| Concept | What it does |
|---|---|
| `var` | Function scoped; hoisted and initialised as `undefined`; ignores block boundaries |
| `let` | Block scoped; cannot be used before its declaration (temporal dead zone) |
| `const` | Block scoped; cannot be reassigned, but the contents of an object can change |

**Output:**

```
--- var: function scoped and hoisted ---
before declaration: undefined
var leaks out of the block
--- let: block scoped, temporal dead zone ---
Error: ReferenceError - Cannot access 'tdz' before initialization
visible only inside this block
typeof blockOnly outside the block: undefined
--- const: cannot be reassigned ---
Error: TypeError - Assignment to constant variable.
const object after change: { name: 'Riya' }
--- classic loop closure problem ---
var: [ 3, 3, 3 ]
let: [ 0, 1, 2 ]
```

**Explanation:** Using `var` in a loop makes every callback share one variable, so all print `3`. `let` creates a fresh variable for each pass, so the output is `0, 1, 2`.

*Output:* *(screenshot of the terminal)*

### 5.2 Program 2: Arrow functions

**File:** `02_arrow_functions.js`

**Aim:** To write short functions with `=>` and understand how `this` behaves differently from a regular function.

| Concept | What it does |
|---|---|
| Implicit return | `(a, b) => a + b` returns the value without `return` |
| Returning an object | Wrap the object in parentheses: `() => ({ name, age })` |
| `this` | An arrow function does not have its own `this`; it uses the surrounding one |

**Output:**

```
addOld(2, 3) = 5
add(2, 3) = 5
square(5) = 25
Hello, ES6!
makeUser: { name: 'Aman', age: 21 }
passed (>= 40): [ 45, 78, 92, 67 ]
with grace +5: [ 50, 83, 97, 38, 72 ]
total: 315
regular: Aman
arrow: undefined
arrow inside method: [ 'Aman1', 'Aman2' ]
```

**Explanation:** In Node.js the top-level `this` is an empty object, so `arrowFn` prints `undefined`. (In a browser console it would be `window`.) An arrow function inside a method keeps the method's `this`, which is why `delayedList` works.

*Output:* *(screenshot of the terminal)*

### 5.3 Program 3: Template literals

**File:** `03_template_literals.js`

**Aim:** To build strings with backticks, `${ }` expressions, multi-line text and tagged templates.

| Concept | What it does |
|---|---|
| `${ }` | Inserts any JavaScript expression into a string |
| Multi-line | Line breaks inside backticks are kept |
| Tagged template | A function placed before the backticks receives the text parts and the values |
| `String.raw` | Keeps backslashes exactly as typed |

**Output:**

```
Old: Sakshi scored 86 marks.
New: Sakshi scored 86 marks.
Total = Rs. 1497
Result: Pass
Uppercase name: SAKSHI
Student Card
Name  : Sakshi
Marks : 86
Hello [Sakshi], you scored [86]!
C:\new\table
```

**Explanation:** A tagged template calls `highlight(strings, ...values)`; here it wraps every inserted value in square brackets.

*Output:* *(screenshot of the terminal)*

### 5.4 Program 4: Destructuring

**File:** `04_destructuring.js`

**Aim:** To unpack values from arrays and objects into variables in one statement.

| Concept | What it does |
|---|---|
| Array destructuring | By position: `const [first, second] = colors` |
| Object destructuring | By name: `const { name, city } = student` |
| Rename and default | `{ name: studentName, grade = "A" }` |
| In parameters | `function describe({ name, city = "Unknown" })` |

**Output:**

```
red green blue
head: red | tail: [ 'green', 'blue', 'yellow' ]
after swap: a = 2 , b = 1
x = 5 , y = 20
Riya - Dehradun
Riya grade: A
maths: 90 science: 85
Riya lives in Dehradun
Karan lives in Unknown
min: 1 max: 9
```

**Explanation:** Swapping two variables needs no temporary variable: `[a, b] = [b, a]`. A function can return an array and the caller unpacks it directly.

*Output:* *(screenshot of the terminal)*

### 5.5 Program 5: Spread, rest and default parameters

**File:** `05_spread_rest_default.js`

**Aim:** To expand arrays and objects with `...`, collect extra arguments, and give parameters default values.

| Concept | What it does |
|---|---|
| Spread `...` | Expands an array or object in place (copy, merge, pass as arguments) |
| Rest `...` | In a parameter list, collects the remaining arguments into an array |
| Default parameters | Used only when the argument is `undefined` |

**Output:**

```
basket: [ 'apple', 'banana', 'mango', 'carrot', 'peas' ]
original: [ 'apple', 'banana' ] | copy: [ 'apple', 'banana', 'grapes' ]
max: 9 | min: 2
updated: { name: 'Aman', age: 21, city: 'Delhi' }
sum(1, 2, 3) = 6
sum(10, 20, 30, 40) = 100
A, B and 3 more
Hello, Guest!
Hello, Sakshi!
Welcome, Sakshi!
Hi, Guest!
area(5) = 25 | area(5, 2) = 10
```

**Explanation:** Spreading an array makes a shallow copy, so changing the copy does not change the original. In `{ ...base, age: 21 }` the later key overrides the earlier one.

*Output:* *(screenshot of the terminal)*

### 5.6 Program 6: Classes and inheritance

**File:** `06_classes.js`

**Aim:** To create classes with constructors, getters and setters, static members, private fields and inheritance.

| Concept | What it does |
|---|---|
| `constructor` | Runs when `new` creates an object |
| `get` / `set` | Properties that run code when read or written (the setter validates the age) |
| `static` | Belongs to the class, not to objects (`Person.count`) |
| `#id` | Private field, accessible only inside the class |
| `extends` / `super` | Inheritance and calling the parent's constructor or method |

**Output:**

```
Hi, I am Aman, 25 years old.
Hi, I am Riya, 17 years old. I study Computer Science.
p.id: 1 | s.id: 2
p.isAdult: true | s.isAdult: false
Total people created: 2
s instanceof Student: true | s instanceof Person: true
typeof Person: function
Error: Age cannot be negative
```

**Explanation:** `typeof Person` is `function`: classes are syntax built on top of functions. `s instanceof Person` is `true` because `Student` extends `Person`.

*Output:* *(screenshot of the terminal)*

### 5.7 Program 7: Promises and async / await

**File:** `07_promises_async.js`

**Aim:** To handle asynchronous work with promise chains, `async` / `await`, `Promise.all` and `Promise.race`.

| Concept | What it does |
|---|---|
| `then` / `catch` | Chain steps and handle a rejected promise |
| `async` / `await` | Write asynchronous code that reads like normal code; errors use `try` / `catch` |
| `Promise.all` | Runs promises in parallel and waits for all (three 300 ms delays finish in about 300 ms, not 900 ms) |
| `Promise.race` | Returns the result of whichever promise finishes first |

**Output:**

```
1. Promise chain
   got { id: 1, name: 'User1' }
   next step with id 1
2. async / await
   got { id: 2, name: 'User2' }
   caught: Invalid user id: -1
3. Promise.all (parallel)
   results: [ 'A', 'B', 'C' ] | finished in about 300 ms: true
4. Promise.race
   winner: fast
Done
```

**Explanation:** `fetchUser(-1)` rejects, and the rejection is caught by `try` / `catch` just like a normal error.

*Output:* *(screenshot of the terminal)*

### 5.8 Program 8: Set, Map, iterators, generators and newer operators

**File:** `08_map_set_generators.js`

**Aim:** To use the new collection types, iterate with `for...of`, create lazy sequences with generators, and use `?.` and `??`.

| Concept | What it does |
|---|---|
| `Set` | Stores unique values; `[...new Set(array)]` removes duplicates |
| `Map` | Key-value pairs where the key can be any type |
| `for...of` | Loops over arrays, strings, Sets, Maps and any iterable |
| Generator `function*` | Produces values one at a time with `yield` |
| `?.` and `??` | Safe property access, and a default only for `null` / `undefined` |

**Output:**

```
Set: Set(4) { 1, 2, 3, 4 } | size: 4 | has 3: true
unique array: [ 'a', 'b', 'c' ]
Map size: 3 | get 42: answer
  entry: name => Aman
  entry: 42 => answer
  entry: true => yes
  char: E
  char: S
  char: 6
  maths: 90
  science: 85
generator: [ 1, 2, 3, 4, 5 ]
ids: 1 2 3
range: [ 1, 2, 3, 4 ]
city: Dehradun
phone: undefined
visits with ||: 10
visits with ??: 0
```

**Explanation:** `user.visits || 10` gives `10` because `0` is falsy, but `user.visits ?? 10` correctly keeps `0`. (`?.` and `??` are ES2020, a later addition to the ES6 family of features.)

*Output:* *(screenshot of the terminal)*

### 5.9 Program 9: Modules (`import` and `export`)

**Files:** `09_math_module.mjs`, `09_modules_main.mjs`

**Aim:** To split code into files and share values between them.

| Concept | What it does |
|---|---|
| `export` | Makes a value, function or class available to other files |
| `export default` | The single main export of a module |
| `import { a, b }` | Imports named exports (`multiply as times` renames one) |
| `import * as Lib` | Imports everything as one object |

**Output:**

```
PI = 3.14159
add(2, 3) = 5
times(4, 5) = 20
circleArea(2) = 12.57
history: [ '10 add 5 = 15', '3 multiply 7 = 21' ]
names exported by the module: [ 'PI', 'add', 'circleArea', 'default', 'multiply' ]
```

**Explanation:** Files with the `.mjs` extension are treated as ES modules by Node.js. The names listed in the last line include `default`, which is the exported `Calculator` class.

*Output:* *(screenshot of the terminal)*

## 6. Comparison: Old JavaScript vs ES6

| Task | Before ES6 | With ES6 |
|---|---|---|
| Variables | `var` (function scope) | `let` / `const` (block scope) |
| Functions | `function (a, b) { return a + b; }` | `(a, b) => a + b` |
| Strings | `"Hi " + name + "!"` | `` `Hi ${name}!` `` |
| Read object values | `var n = obj.name; var c = obj.city;` | `const { name, city } = obj;` |
| Copy / merge | `Object.assign({}, a, b)` | `{ ...a, ...b }` |
| Objects with behaviour | Constructor functions and prototypes | `class` with `extends` |
| Asynchronous code | Nested callbacks | Promises and `async` / `await` |
| Sharing code | Global variables or script tags | `import` / `export` |

## 7. Problems Faced and Solutions

| Problem | Cause | Solution |
|---|---|---|
| `Cannot use import statement outside a module` | Older Node.js versions treat `.js` files as CommonJS | Use the `.mjs` extension (or add `"type": "module"` to `package.json`) |
| `Assignment to constant variable` | A `const` was reassigned | Use `let` if the value must change |
| `Cannot access 'x' before initialization` | `let` / `const` used before its declaration | Declare the variable before using it |
| Arrow function printed `undefined` for `this.name` | Arrow functions do not have their own `this` | Use a regular method when the function needs the object's `this` |
| Returning an object from an arrow function gave `undefined` | `{ }` was read as a function body | Wrap the object in parentheses: `() => ({ ... })` |
| `node` is not recognized | Node.js not installed or not in PATH | Install Node.js and restart VS Code |

*(Keep only the problems you actually faced.)*

## 8. Testing

| Test | Expected Result |
|---|---|
| Run each program with `node <file>` | Runs without errors and prints the output shown above |
| Run `node run_all.js` | All nine programs run one after another |
| Try `PI = 3` on a `const` | `TypeError: Assignment to constant variable.` |
| Use a `let` variable before its declaration | `ReferenceError` (temporal dead zone) |
| Set a negative age in Program 6 | `Error: Age cannot be negative` |

## 9. Limitations and Future Scope

Current limitations:

- The programs are small demonstrations and run only in the terminal (Program 9 does not run in the browser console).
- Older browsers do not support all ES6 features without a tool such as Babel.
- Promise timings use fixed delays instead of real network requests.

Possible improvements:

- Use real asynchronous work, such as `fetch()` calls to an API, in the promises program.
- Add a browser page that loads the modules with `<script type="module">`.
- Cover further features: `Symbol`, `WeakMap`, proxies, and array methods such as `flat` and `find`.
- Bundle and transpile the code with Babel and a bundler.

## 10. Conclusion

This experiment demonstrated the main ES6 features through nine runnable programs. `let` and `const` fixed the scope problems of `var`; arrow functions, template literals, destructuring, spread, rest and default parameters made code shorter and clearer; classes gave a clean syntax for inheritance; promises and `async` / `await` made asynchronous code easier to read; and modules allowed code to be split across files. Together these features make modern JavaScript easier to write, read and maintain.

