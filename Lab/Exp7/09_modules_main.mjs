// Program 9 (part 2): importing from a module
// Run with:  node 09_modules_main.mjs

import Calculator, { PI, add, multiply as times, circleArea } from "./09_math_module.mjs";
import * as MathLib from "./09_math_module.mjs";

console.log("PI =", PI);
console.log("add(2, 3) =", add(2, 3));
console.log("times(4, 5) =", times(4, 5));             // imported under the name "times"
console.log("circleArea(2) =", circleArea(2).toFixed(2));

const calc = new Calculator();
calc.run("add", 10, 5);
calc.run("multiply", 3, 7);
console.log("history:", calc.history);

console.log("names exported by the module:", Object.keys(MathLib));
