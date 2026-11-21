// Program 3: Template literals

const name = "Sakshi";
const marks = 86;

// Old style vs template literal
console.log("Old: " + name + " scored " + marks + " marks.");
console.log(`New: ${name} scored ${marks} marks.`);

// Expressions inside ${ }
const price = 499;
const qty = 3;
console.log(`Total = Rs. ${price * qty}`);
console.log(`Result: ${marks >= 40 ? "Pass" : "Fail"}`);
console.log(`Uppercase name: ${name.toUpperCase()}`);

// Multi-line strings
const card = `Student Card
Name  : ${name}
Marks : ${marks}`;
console.log(card);

// Tagged template: a function that processes the template
function highlight(strings, ...values) {
    return strings.reduce(
        (out, str, i) => out + str + (i < values.length ? `[${values[i]}]` : ""),
        ""
    );
}
console.log(highlight`Hello ${name}, you scored ${marks}!`);

// String.raw keeps backslashes as typed
console.log(String.raw`C:\new\table`);
