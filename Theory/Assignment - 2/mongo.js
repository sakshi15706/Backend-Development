// run: mongosh < mongo.js   (or paste into mongosh)
use("assignment2");
db.products.drop();
db.products.insertMany([
  { name: "Clean Code", category: "book", price: 499.00, attributes: { author: "Robert C. Martin", pages: 464 } },
  { name: "The Pragmatic Programmer", category: "book", price: 650.00, attributes: { author: "Andrew Hunt", pages: 352 } },
  { name: "ThinkPad X1", category: "laptop", price: 125000.00, attributes: { ram_gb: 32, cpu: "Intel i7" } },
  { name: "MacBook Air", category: "laptop", price: 99000.00, attributes: { ram_gb: 8, cpu: "Apple M2" } },
  { name: "Wireless Mouse", category: "accessory", price: 1299.00, attributes: { color: "black", wireless: true } }
]);

printjson(db.products.find({ category: "book", "attributes.pages": { $gt: 400 } }, { name: 1, "attributes.author": 1 }).toArray());
printjson(db.products.find({ category: "laptop", "attributes.ram_gb": { $gte: 16 } }, { name: 1, "attributes.cpu": 1 }).toArray());
printjson(db.products.find({ category: "accessory", "attributes.color": "black", "attributes.wireless": true }).toArray());

db.products.createIndex({ "attributes.wireless": 1 });
printjson(db.products.find({ "attributes.wireless": true }).explain("executionStats").executionStats);
