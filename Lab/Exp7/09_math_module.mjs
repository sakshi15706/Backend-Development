// Program 9 (part 1): a module that exports values and functions

export const PI = 3.14159;

export function add(a, b) {
    return a + b;
}

export const multiply = (a, b) => a * b;

export function circleArea(radius) {
    return PI * radius * radius;
}

// One default export per module
export default class Calculator {
    constructor() {
        this.history = [];
    }
    run(op, a, b) {
        const result = op === "add" ? add(a, b) : multiply(a, b);
        this.history.push(`${a} ${op} ${b} = ${result}`);
        return result;
    }
}
