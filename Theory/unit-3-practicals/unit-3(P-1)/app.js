// Student Management API skeleton (Lecture 25)

// Import the express module
const express = require('express');

// Initialize the express application
const app = express();
const PORT = process.env.PORT || 3000;

// Built-in middleware to parse incoming JSON payloads
app.use(express.json());

// Basic route: when a GET request is made to '/', this function executes
app.get('/', (req, res) => {
  // res.send sends a response back to the client
  res.send('API is running');
});

// Start the server only when this file is run directly (node app.js).
// When the tests require() this file, they get the app without a port being opened.
if (require.main === module) {
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

module.exports = app;
