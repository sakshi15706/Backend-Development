// Program 8: Set, Map, for...of, generators, optional chaining and nullish coalescing

// Set: unique values only
const set = new Set([1, 2, 2, 3, 3, 3]);
set.add(4);
console.log("Set:", set, "| size:", set.size, "| has 3:", set.has(3));
const unique = [...new Set(["a", "b", "a", "c", "b"])];
console.log("unique array:", unique);

// Map: key-value pairs where keys can be any type
const map = new Map();
map.set("name", "Aman");
map.set(42, "answer");
map.set(true, "yes");
console.log("Map size:", map.size, "| get 42:", map.get(42));
for (const [key, value] of map) {
    console.log("  entry:", key, "=>", value);
}

// for...of works on arrays, strings, Sets and Maps
for (const ch of "ES6") console.log("  char:", ch);

// Object.entries with destructuring
const scores = { maths: 90, science: 85 };
for (const [subject, mark] of Object.entries(scores)) {
    console.log(`  ${subject}: ${mark}`);
}

// Generator function: produces values one at a time
function* counter(limit) {
    for (let i = 1; i <= limit; i++) yield i;
}
console.log("generator:", [...counter(5)]);

function* idMaker() {
    let id = 1;
    while (true) yield id++;                          // infinite, but lazy
}
const ids = idMaker();
console.log("ids:", ids.next().value, ids.next().value, ids.next().value);

// Custom iterable using Symbol.iterator
const range = {
    from: 1,
    to: 4,
    [Symbol.iterator]() {
        let current = this.from;
        const last = this.to;
        return { next: () => (current <= last ? { value: current++, done: false } : { value: undefined, done: true }) };
    }
};
console.log("range:", [...range]);

// Optional chaining (?.) and nullish coalescing (??)
const user = { profile: { city: "Dehradun" }, visits: 0 };
console.log("city:", user.profile?.city);
console.log("phone:", user.contact?.phone);           // undefined, no error
console.log("visits with ||:", user.visits || 10);    // 10 (0 is falsy)
console.log("visits with ??:", user.visits ?? 10);    // 0  (only null / undefined use the default)
