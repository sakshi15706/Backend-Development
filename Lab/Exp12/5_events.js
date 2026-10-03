// Program 5: Events and EventEmitter (the base of Node.js asynchronous programming)
// Run:  node 5_events.js

const EventEmitter = require("events");

// 1. Basic emitter
const emitter = new EventEmitter();

// on() registers a listener; emit() fires the event
emitter.on("greet", (name) => {
  console.log("Hello, " + name + "!");
});
emitter.on("greet", (name) => {
  console.log("(second listener) Welcome to Node.js, " + name);
});
emitter.once("firstVisit", () => {
  console.log("once(): this runs only the first time");
});

console.log("--- Basic events ---");
emitter.emit("greet", "Sakshi");
emitter.emit("firstVisit");
emitter.emit("firstVisit");                       // nothing happens the second time
console.log("Listeners for 'greet':", emitter.listenerCount("greet"));

// 2. Event with several arguments
emitter.on("order", (item, qty, price) => {
  console.log("Order received: " + qty + " x " + item + " = Rs " + qty * price);
});
console.log("\n--- Event with arguments ---");
emitter.emit("order", "Notebook", 3, 50);

// 3. A class that extends EventEmitter (a realistic example)
class Shop extends EventEmitter {
  constructor() {
    super();
    this.stock = 5;
  }
  buy(qty) {
    if (qty > this.stock) {
      this.emit("error", new Error("Only " + this.stock + " items in stock"));
      return;
    }
    this.stock -= qty;
    this.emit("sold", qty);
    if (this.stock === 0) {
      this.emit("outOfStock");
    }
  }
}

const shop = new Shop();
shop.on("sold", (qty) => console.log("Sold " + qty + " item(s). Stock left: " + shop.stock));
shop.on("outOfStock", () => console.log("Alert: shop is out of stock!"));
shop.on("error", (err) => console.log("Error event: " + err.message));

console.log("\n--- Shop example ---");
shop.buy(2);
shop.buy(10);
shop.buy(3);

// 4. Removing a listener
function once1() { console.log("This listener will be removed"); }
emitter.on("test", once1);
emitter.emit("test");
emitter.removeListener("test", once1);
emitter.emit("test");                              // no output now
console.log("\nAfter removeListener, 'test' listeners:", emitter.listenerCount("test"));

// 5. Asynchronous order: setTimeout vs synchronous code
console.log("\n--- Async order ---");
console.log("1. Start");
setTimeout(() => console.log("3. Inside setTimeout (runs later)"), 0);
process.nextTick(() => console.log("2b. nextTick (runs before timers)"));
console.log("2. End of the script");
