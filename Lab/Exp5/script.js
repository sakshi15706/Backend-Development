// =====================================================================
// Experiment 5: JavaScript Array, Object and Functions
// Each demo collects its output lines and prints them on the page
// (inside the <pre> with the given id) and in the browser console.
// =====================================================================

// Helper: show lines in a <pre> element and in the console
function show(id, lines) {
  var text = lines.join("\n");
  document.getElementById(id).textContent = text;
  console.log("--- " + id + " ---\n" + text);
}

// =====================================================================
// PART 1: ARRAYS
// =====================================================================

// 1.1 Creating and accessing arrays
(function () {
  var out = [];
  var fruits = ["Apple", "Banana", "Mango", "Orange"];
  var numbers = new Array(10, 20, 30);
  var mixed = [1, "Hello", true, null, { a: 1 }];

  out.push("fruits  = " + JSON.stringify(fruits));
  out.push("numbers = " + JSON.stringify(numbers));
  out.push("mixed   = " + JSON.stringify(mixed));
  out.push("First element  fruits[0] = " + fruits[0]);
  out.push("Last element   fruits[fruits.length - 1] = " + fruits[fruits.length - 1]);
  out.push("Length of fruits = " + fruits.length);
  out.push("Is fruits an array? " + Array.isArray(fruits));
  fruits[1] = "Grapes";                                   // change an element
  out.push("After fruits[1] = 'Grapes' -> " + JSON.stringify(fruits));
  show("arr1", out);
})();

// 1.2 Adding and removing elements
(function () {
  var out = [];
  var a = [10, 20, 30];
  out.push("Start            : " + JSON.stringify(a));
  a.push(40);
  out.push("push(40)         : " + JSON.stringify(a) + "   (adds at the end)");
  a.unshift(5);
  out.push("unshift(5)       : " + JSON.stringify(a) + "   (adds at the start)");
  var popped = a.pop();
  out.push("pop()            : " + JSON.stringify(a) + "   removed " + popped);
  var shifted = a.shift();
  out.push("shift()          : " + JSON.stringify(a) + "   removed " + shifted);
  a.splice(1, 0, 15, 17);
  out.push("splice(1,0,15,17): " + JSON.stringify(a) + "   (insert at index 1)");
  a.splice(2, 1);
  out.push("splice(2,1)      : " + JSON.stringify(a) + "   (remove 1 element at index 2)");
  var joined = a.concat([100, 200]);
  out.push("concat([100,200]): " + JSON.stringify(joined));
  show("arr2", out);
})();

// 1.3 Searching, slicing, sorting
(function () {
  var out = [];
  var a = [40, 10, 30, 20, 50, 30];
  out.push("Array a = " + JSON.stringify(a));
  out.push("indexOf(30)        = " + a.indexOf(30));
  out.push("lastIndexOf(30)    = " + a.lastIndexOf(30));
  out.push("includes(20)       = " + a.includes(20));
  out.push("includes(99)       = " + a.includes(99));
  out.push("slice(1, 4)        = " + JSON.stringify(a.slice(1, 4)) + "   (original is not changed)");
  out.push("join(' - ')        = " + a.join(" - "));
  var copy = a.slice();
  out.push("reverse()          = " + JSON.stringify(copy.reverse()));
  var copy2 = a.slice();
  out.push("sort() default     = " + JSON.stringify(copy2.sort()) + "   (sorts as text)");
  var copy3 = a.slice();
  out.push("sort((x,y)=>x-y)   = " + JSON.stringify(copy3.sort(function (x, y) { return x - y; })) + "   (numeric ascending)");
  var copy4 = a.slice();
  out.push("sort((x,y)=>y-x)   = " + JSON.stringify(copy4.sort(function (x, y) { return y - x; })) + "   (numeric descending)");
  out.push("Math.max / Math.min = " + Math.max.apply(null, a) + " / " + Math.min.apply(null, a));
  show("arr3", out);
})();

// 1.4 Looping and higher-order methods
(function () {
  var out = [];
  var marks = [45, 82, 67, 90, 33, 74];
  out.push("marks = " + JSON.stringify(marks));

  out.push("\nfor loop:");
  var s1 = "";
  for (var i = 0; i < marks.length; i++) { s1 += marks[i] + " "; }
  out.push("  " + s1);

  out.push("for...of loop:");
  var s2 = "";
  for (var m of marks) { s2 += m + " "; }
  out.push("  " + s2);

  out.push("forEach:");
  marks.forEach(function (value, index) {
    out.push("  index " + index + " -> " + value);
  });

  var plus5 = marks.map(function (x) { return x + 5; });
  out.push("\nmap (add 5 grace marks)   : " + JSON.stringify(plus5));

  var passed = marks.filter(function (x) { return x >= 40; });
  out.push("filter (marks >= 40)      : " + JSON.stringify(passed));

  var total = marks.reduce(function (sum, x) { return sum + x; }, 0);
  out.push("reduce (total)            : " + total);
  out.push("Average                   : " + (total / marks.length).toFixed(2));

  var first = marks.find(function (x) { return x > 80; });
  out.push("find (first mark > 80)    : " + first);
  out.push("some (any mark < 35?)     : " + marks.some(function (x) { return x < 35; }));
  out.push("every (all marks >= 33?)  : " + marks.every(function (x) { return x >= 33; }));
  show("arr4", out);
})();

// 1.5 Two-dimensional array
(function () {
  var out = [];
  var matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
  ];
  out.push("Matrix:");
  for (var r = 0; r < matrix.length; r++) {
    out.push("  " + matrix[r].join("  "));
  }
  out.push("matrix[1][2] = " + matrix[1][2]);

  var diagonal = 0;
  for (var d = 0; d < matrix.length; d++) { diagonal += matrix[d][d]; }
  out.push("Sum of main diagonal = " + diagonal);

  out.push("Transpose:");
  for (var c = 0; c < 3; c++) {
    var row = [];
    for (var r2 = 0; r2 < 3; r2++) { row.push(matrix[r2][c]); }
    out.push("  " + row.join("  "));
  }
  show("arr5", out);
})();

// 1.6 Try it: interactive array
var userNumbers = [];

function addNumber() {
  var input = document.getElementById("numInput");
  if (input.value === "") { alert("Please enter a number"); return; }
  userNumbers.push(Number(input.value));
  input.value = "";
  var sum = userNumbers.reduce(function (s, x) { return s + x; }, 0);
  show("arrTry", [
    "Array   : " + JSON.stringify(userNumbers),
    "Count   : " + userNumbers.length,
    "Sum     : " + sum,
    "Average : " + (sum / userNumbers.length).toFixed(2),
    "Largest : " + Math.max.apply(null, userNumbers),
    "Smallest: " + Math.min.apply(null, userNumbers),
    "Sorted  : " + JSON.stringify(userNumbers.slice().sort(function (a, b) { return a - b; }))
  ]);
}

function clearNumbers() {
  userNumbers = [];
  show("arrTry", ["Array: []"]);
}

// =====================================================================
// PART 2: OBJECTS
// =====================================================================

// 2.1 Creating an object and accessing properties
(function () {
  var out = [];
  var student = {
    name: "Rahul",
    roll: 101,
    course: "CSE",
    marks: 85,
    passed: true
  };
  out.push("student = " + JSON.stringify(student));
  out.push("Dot notation      student.name       = " + student.name);
  out.push("Bracket notation  student['course']  = " + student["course"]);
  var key = "marks";
  out.push("Using a variable  student[key]       = " + student[key]);
  out.push("'roll' in student  = " + ("roll" in student));
  out.push("hasOwnProperty('age') = " + student.hasOwnProperty("age"));
  out.push("student.age (not present) = " + student.age);
  show("obj1", out);
})();

// 2.2 Adding, updating and deleting properties
(function () {
  var out = [];
  var book = { title: "JavaScript Basics", price: 350 };
  out.push("Start   : " + JSON.stringify(book));
  book.author = "A. Kumar";
  out.push("Add     : " + JSON.stringify(book));
  book.price = 299;
  out.push("Update  : " + JSON.stringify(book));
  delete book.author;
  out.push("Delete  : " + JSON.stringify(book));

  var copy = Object.assign({}, book, { pages: 220 });
  out.push("Object.assign copy with pages: " + JSON.stringify(copy));
  var spread = { ...book, discount: 10 };
  out.push("Spread copy with discount     : " + JSON.stringify(spread));

  var frozen = Object.freeze({ x: 1 });
  frozen.x = 99;
  out.push("Frozen object after x = 99    : " + JSON.stringify(frozen) + "   (cannot change)");
  show("obj2", out);
})();

// 2.3 Methods and "this"
(function () {
  var out = [];
  var person = {
    firstName: "Priya",
    lastName: "Sharma",
    age: 21,
    fullName: function () {
      return this.firstName + " " + this.lastName;
    },
    birthdayWish: function () {
      this.age++;
      return "Happy Birthday " + this.firstName + "! You are now " + this.age + ".";
    }
  };
  out.push("person.fullName()     -> " + person.fullName());
  out.push("person.birthdayWish() -> " + person.birthdayWish());
  out.push("person.age            -> " + person.age);

  var rectangle = {
    length: 10,
    width: 5,
    area() { return this.length * this.width; },          // shorthand method
    perimeter() { return 2 * (this.length + this.width); }
  };
  out.push("rectangle.area()      -> " + rectangle.area());
  out.push("rectangle.perimeter() -> " + rectangle.perimeter());
  show("obj3", out);
})();

// 2.4 Looping through an object
(function () {
  var out = [];
  var car = { brand: "Toyota", model: "Innova", year: 2024, color: "White" };

  out.push("for...in:");
  for (var key in car) {
    out.push("  " + key + " : " + car[key]);
  }
  out.push("Object.keys(car)    = " + JSON.stringify(Object.keys(car)));
  out.push("Object.values(car)  = " + JSON.stringify(Object.values(car)));
  out.push("Object.entries(car) = " + JSON.stringify(Object.entries(car)));
  out.push("Number of properties = " + Object.keys(car).length);

  out.push("Destructuring: const { brand, year } = car");
  var { brand, year } = car;
  out.push("  brand = " + brand + ", year = " + year);
  show("obj4", out);
})();

// 2.5 Nested objects and array of objects
(function () {
  var out = [];
  var employee = {
    name: "Amit",
    address: { city: "Meerut", state: "Uttar Pradesh", pin: 250001 },
    skills: ["HTML", "CSS", "JavaScript"]
  };
  out.push("employee.address.city = " + employee.address.city);
  out.push("employee.skills[2]    = " + employee.skills[2]);
  out.push("JSON string:\n" + JSON.stringify(employee, null, 2));

  var products = [
    { id: 1, name: "Pen", price: 10 },
    { id: 2, name: "Notebook", price: 50 },
    { id: 3, name: "Bag", price: 700 }
  ];
  out.push("\nArray of objects:");
  products.forEach(function (p) {
    out.push("  " + p.id + ". " + p.name + " - Rs " + p.price);
  });
  var costly = products.filter(function (p) { return p.price > 40; });
  out.push("Price > 40 : " + costly.map(function (p) { return p.name; }).join(", "));
  var totalPrice = products.reduce(function (s, p) { return s + p.price; }, 0);
  out.push("Total price: Rs " + totalPrice);

  var parsed = JSON.parse('{"city":"Delhi","pop":32}');
  out.push("JSON.parse result: city = " + parsed.city + ", pop = " + parsed.pop);
  show("obj5", out);
})();

// 2.6 Constructor function and class
(function () {
  var out = [];

  // Constructor function
  function Student(name, roll) {
    this.name = name;
    this.roll = roll;
    this.show = function () { return this.roll + " - " + this.name; };
  }
  var s1 = new Student("Neha", 1);
  var s2 = new Student("Karan", 2);
  out.push("Constructor function: " + s1.show() + " | " + s2.show());

  // Prototype method (shared by all objects)
  Student.prototype.greet = function () { return "Hello, I am " + this.name; };
  out.push("Prototype method    : " + s1.greet());

  // ES6 class
  class Animal {
    constructor(name, sound) {
      this.name = name;
      this.sound = sound;
    }
    speak() { return this.name + " says " + this.sound; }
  }
  class Dog extends Animal {
    constructor(name) { super(name, "Woof"); }
    fetch() { return this.name + " fetches the ball"; }
  }
  var d = new Dog("Tommy");
  out.push("Class + inheritance : " + d.speak() + "; " + d.fetch());
  out.push("d instanceof Dog    : " + (d instanceof Dog));
  out.push("d instanceof Animal : " + (d instanceof Animal));
  show("obj6", out);
})();

// 2.7 Try it: students from a form
var students = [];

function addStudent() {
  var name = document.getElementById("sName").value.trim();
  var marks = document.getElementById("sMarks").value;
  if (name === "" || marks === "") { alert("Enter both name and marks"); return; }

  var student = { name: name, marks: Number(marks) };    // create an object
  students.push(student);                                // add it to the array
  document.getElementById("sName").value = "";
  document.getElementById("sMarks").value = "";

  var lines = ["Students (" + students.length + "):"];
  students.forEach(function (s, i) {
    lines.push("  " + (i + 1) + ". " + s.name + " - " + s.marks);
  });
  show("objTry", lines);
}

// =====================================================================
// PART 3: FUNCTIONS
// =====================================================================

// 3.1 Declaration, parameters, return
(function () {
  var out = [];

  function greet(name) {
    return "Hello, " + name + "!";
  }
  function add(a, b) {
    return a + b;
  }
  function isEven(n) {
    return n % 2 === 0;
  }
  function printLine() {                       // no parameter, no return value
    console.log("printLine() was called");
  }

  out.push("greet('Sakshi') -> " + greet("Sakshi"));
  out.push("add(5, 7)       -> " + add(5, 7));
  out.push("isEven(10)      -> " + isEven(10));
  out.push("isEven(7)       -> " + isEven(7));
  out.push("printLine()     -> " + printLine() + "   (returns undefined)");

  // Hoisting: a function declaration can be called before it is written
  out.push("Hoisting: square(6) -> " + square(6));
  function square(n) { return n * n; }

  // Function returning an object
  function makePoint(x, y) { return { x: x, y: y }; }
  out.push("makePoint(3, 4) -> " + JSON.stringify(makePoint(3, 4)));
  show("fn1", out);
})();

// 3.2 Function expression and arrow function
(function () {
  var out = [];

  var multiply = function (a, b) { return a * b; };    // function expression
  var divide = (a, b) => a / b;                         // arrow function
  var double = n => n * 2;                              // one parameter
  var hello = () => "Hello from arrow";                 // no parameter
  var describe = (name, age) => {                       // block body
    var group = age >= 18 ? "adult" : "minor";
    return name + " is an " + group;
  };

  out.push("Function expression multiply(4, 5) -> " + multiply(4, 5));
  out.push("Arrow divide(20, 4)                 -> " + divide(20, 4));
  out.push("Arrow double(8)                     -> " + double(8));
  out.push("Arrow hello()                       -> " + hello());
  out.push("Arrow describe('Rahul', 19)         -> " + describe("Rahul", 19));
  out.push("Arrow with map: [1,2,3].map(n => n*n) -> " + JSON.stringify([1, 2, 3].map(n => n * n)));
  show("fn2", out);
})();

// 3.3 Default and rest parameters
(function () {
  var out = [];

  function welcome(name = "Guest", city = "Meerut") {
    return "Welcome " + name + " from " + city;
  }
  out.push("welcome()                 -> " + welcome());
  out.push("welcome('Priya')          -> " + welcome("Priya"));
  out.push("welcome('Amit', 'Delhi')  -> " + welcome("Amit", "Delhi"));

  function sumAll(...nums) {                           // rest parameter
    return nums.reduce(function (s, n) { return s + n; }, 0);
  }
  out.push("sumAll(1, 2, 3)           -> " + sumAll(1, 2, 3));
  out.push("sumAll(10, 20, 30, 40, 50)-> " + sumAll(10, 20, 30, 40, 50));

  function showArgs() {                                // arguments object
    return "arguments.length = " + arguments.length;
  }
  out.push("showArgs('a','b','c')     -> " + showArgs("a", "b", "c"));

  var values = [5, 9, 2];
  out.push("Spread: Math.max(...[5,9,2]) -> " + Math.max(...values));
  show("fn3", out);
})();

// 3.4 Callback function
(function () {
  var out = [];

  function calculate(a, b, callback) {
    return callback(a, b);
  }
  function add(x, y) { return x + y; }
  function subtract(x, y) { return x - y; }

  out.push("calculate(10, 5, add)       -> " + calculate(10, 5, add));
  out.push("calculate(10, 5, subtract)  -> " + calculate(10, 5, subtract));
  out.push("calculate(10, 5, (x,y)=>x*y) -> " + calculate(10, 5, (x, y) => x * y));

  function processArray(arr, fn) {
    var result = [];
    for (var i = 0; i < arr.length; i++) { result.push(fn(arr[i])); }
    return result;
  }
  out.push("processArray([1,2,3], n=>n*10) -> " + JSON.stringify(processArray([1, 2, 3], n => n * 10)));

  out.push("setTimeout callback: a message will appear after 2 seconds below...");
  show("fn4", out);
  setTimeout(function () {
    out.push("   -> Callback executed after 2 seconds (asynchronous)");
    show("fn4", out);
  }, 2000);
})();

// 3.5 Recursion
(function () {
  var out = [];

  function factorial(n) {
    if (n <= 1) { return 1; }              // base case
    return n * factorial(n - 1);           // recursive call
  }
  function fibonacci(n) {
    if (n <= 1) { return n; }
    return fibonacci(n - 1) + fibonacci(n - 2);
  }
  function sumTo(n) {
    return n === 0 ? 0 : n + sumTo(n - 1);
  }

  out.push("factorial(5)  = " + factorial(5));
  out.push("factorial(7)  = " + factorial(7));
  var fib = [];
  for (var i = 0; i < 10; i++) { fib.push(fibonacci(i)); }
  out.push("Fibonacci series (first 10) = " + fib.join(", "));
  out.push("sumTo(10)     = " + sumTo(10));
  out.push("Recursion = a function that calls itself, with a base case to stop.");
  show("fn5", out);
})();

// 3.6 Closure
(function () {
  var out = [];

  function makeCounter() {
    var count = 0;                         // private variable
    return function () {
      count++;
      return count;
    };
  }
  var c1 = makeCounter();
  var c2 = makeCounter();
  out.push("c1() -> " + c1());
  out.push("c1() -> " + c1());
  out.push("c1() -> " + c1());
  out.push("c2() -> " + c2() + "   (c2 has its own separate count)");

  function multiplier(factor) {
    return function (n) { return n * factor; };
  }
  var triple = multiplier(3);
  out.push("multiplier(3) -> triple(7) = " + triple(7));

  function bankAccount(initial) {
    var balance = initial;
    return {
      deposit: function (amt) { balance += amt; return balance; },
      withdraw: function (amt) {
        if (amt > balance) { return "Insufficient balance"; }
        balance -= amt; return balance;
      },
      getBalance: function () { return balance; }
    };
  }
  var acc = bankAccount(1000);
  out.push("Bank account: deposit(500)   -> " + acc.deposit(500));
  out.push("Bank account: withdraw(300)  -> " + acc.withdraw(300));
  out.push("Bank account: withdraw(5000) -> " + acc.withdraw(5000));
  out.push("balance variable is private, only reachable through the functions.");
  show("fn6", out);
})();

// 3.7 IIFE
(function () {
  var out = [];
  var result = (function (a, b) {
    return "IIFE ran immediately, a + b = " + (a + b);
  })(10, 20);
  out.push(result);

  var arrowIife = (() => "Arrow IIFE ran immediately")();
  out.push(arrowIife);
  out.push("An IIFE runs as soon as it is defined and keeps its variables private.");
  show("fn7", out);
})();

// 3.8 Try it: calculator
function add(a, b) { return a + b; }
function sub(a, b) { return a - b; }
function mul(a, b) { return a * b; }
function div(a, b) { return b === 0 ? "Cannot divide by zero" : a / b; }

function calculate() {
  var a = document.getElementById("n1").value;
  var b = document.getElementById("n2").value;
  var op = document.getElementById("op").value;
  if (a === "" || b === "") { alert("Enter both numbers"); return; }
  a = Number(a); b = Number(b);

  var operations = { add: add, sub: sub, mul: mul, div: div };   // object of functions
  var symbols = { add: "+", sub: "-", mul: "x", div: "/" };
  var result = operations[op](a, b);
  show("fnTry", [a + " " + symbols[op] + " " + b + " = " + result]);
}

// =====================================================================
// PART 4: COMBINED PROGRAM - Student result (array of objects + functions)
// =====================================================================
(function () {
  var out = [];

  var results = [
    { name: "Rahul", maths: 78, physics: 65, chemistry: 82 },
    { name: "Priya", maths: 92, physics: 88, chemistry: 95 },
    { name: "Amit",  maths: 45, physics: 52, chemistry: 38 },
    { name: "Neha",  maths: 60, physics: 71, chemistry: 66 },
    { name: "Karan", maths: 30, physics: 41, chemistry: 35 }
  ];

  function total(s) { return s.maths + s.physics + s.chemistry; }
  function percentage(s) { return total(s) / 3; }
  function grade(p) {
    if (p >= 90) return "A+";
    if (p >= 75) return "A";
    if (p >= 60) return "B";
    if (p >= 40) return "C";
    return "F";
  }
  function status(s) {
    return (s.maths >= 33 && s.physics >= 33 && s.chemistry >= 33) ? "Pass" : "Fail";
  }

  // Build the final list with calculated fields
  var final = results.map(function (s) {
    var p = percentage(s);
    return {
      name: s.name,
      total: total(s),
      percentage: p.toFixed(2),
      grade: grade(p),
      status: status(s)
    };
  });

  var topper = final.reduce(function (best, s) {
    return s.total > best.total ? s : best;
  });
  var passCount = final.filter(function (s) { return s.status === "Pass"; }).length;
  var classAverage = final.reduce(function (sum, s) { return sum + s.total; }, 0) / final.length;

  out.push("Students           : " + final.length);
  out.push("Passed             : " + passCount);
  out.push("Failed             : " + (final.length - passCount));
  out.push("Topper             : " + topper.name + " (" + topper.total + "/300)");
  out.push("Class average total: " + classAverage.toFixed(2));
  out.push("Sorted by total (highest first): " +
    final.slice().sort(function (a, b) { return b.total - a.total; })
         .map(function (s) { return s.name; }).join(" > "));
  show("comb", out);

  // Build an HTML table
  var html = "<table><tr><th>Name</th><th>Total /300</th><th>Percentage</th><th>Grade</th><th>Status</th></tr>";
  final.forEach(function (s) {
    var cls = s.name === topper.name ? " class='topper'" : "";
    html += "<tr" + cls + "><td>" + s.name + "</td><td>" + s.total + "</td><td>" +
            s.percentage + "%</td><td>" + s.grade + "</td><td>" + s.status + "</td></tr>";
  });
  html += "</table>";
  document.getElementById("resultTable").innerHTML = html;
})();
