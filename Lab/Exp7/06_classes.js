// Program 6: Classes, inheritance, getters/setters, static and private fields

class Person {
    #id;                                              // private field
    static count = 0;                                 // static property

    constructor(name, age) {
        this.name = name;
        this.age = age;
        this.#id = ++Person.count;
    }

    get id() { return this.#id; }                     // getter
    get isAdult() { return this.age >= 18; }

    set age(value) {                                  // setter with validation
        if (value < 0) throw new Error("Age cannot be negative");
        this._age = value;
    }
    get age() { return this._age; }

    introduce() {
        return `Hi, I am ${this.name}, ${this.age} years old.`;
    }

    static total() { return `Total people created: ${Person.count}`; }
}

class Student extends Person {
    constructor(name, age, course) {
        super(name, age);                             // call the parent constructor
        this.course = course;
    }
    introduce() {                                     // method overriding
        return `${super.introduce()} I study ${this.course}.`;
    }
}

const p = new Person("Aman", 25);
const s = new Student("Riya", 17, "Computer Science");

console.log(p.introduce());
console.log(s.introduce());
console.log("p.id:", p.id, "| s.id:", s.id);
console.log("p.isAdult:", p.isAdult, "| s.isAdult:", s.isAdult);
console.log(Person.total());
console.log("s instanceof Student:", s instanceof Student, "| s instanceof Person:", s instanceof Person);
console.log("typeof Person:", typeof Person);          // classes are special functions

try {
    p.age = -5;
} catch (e) {
    console.log("Error:", e.message);
}
