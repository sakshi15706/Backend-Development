# Backend Development Lab Report – Unit 3
## Frameworks and Performance Optimization

## 1. Introduction

Unit 3 focuses on backend development using Express.js and Django, middleware implementation, URL routing, third-party API integration, application testing, authentication, authorization, database optimisation, caching, forms, and file uploads.

The practicals helped in understanding how backend frameworks handle requests, process data, communicate with external services, secure applications, and improve performance.

A total of eight practicals were completed using Node.js, Express.js, Python, Django, Django REST Framework, SQLite, and other supporting libraries.

## 2. Practical Work and Concepts Covered

### Practical 1: Express.js Setup and Basic Server

**Objective:** To set up an Express.js application and create a basic backend server.

**Work Performed:**
- Initialised a Node.js project using npm.
- Installed the Express.js framework.
- Created a basic server using `app.js`.
- Configured JSON middleware using `express.json()`.
- Implemented a root route that returns an API running message.
- Tested the root route, unknown routes, and invalid JSON requests.
- Used Node.js built-in testing functionality to verify the application.

**Concepts Included:**
- Node.js.
- Express.js.
- npm package management.
- Backend server creation.
- Routing.
- JSON middleware.
- HTTP status codes.
- Automated testing using `node:test`.

### Practical 2: Django Middleware and URL Routing

**Objective:** To understand Django middleware and URL routing for handling incoming HTTP requests.

**Work Performed:**
- Created a Django project named `student_system`.
- Created a Django application named `students`.
- Implemented a health-check route.
- Developed custom logging middleware.
- Recorded incoming requests and response status codes.
- Measured request processing time.
- Configured application-level and project-level URL routing.
- Implemented fixed and dynamic URL patterns.
- Tested routing errors and debugging scenarios.

**Concepts Included:**
- Django framework.
- Django project and application structure.
- Middleware.
- Request-response processing.
- URL routing.
- Dynamic URL parameters.
- Logging.
- Debugging HTTP 404 and 500 errors.

### Practical 3: Integration of Third-Party APIs

**Objective:** To integrate external APIs into a Django application and handle different API failures.

**Work Performed:**
- Created a service utility to communicate with an external API.
- Used the Python Requests library to send HTTP requests.
- Configured a 2-second request timeout.
- Handled timeout errors, HTTP errors, network failures, and invalid JSON responses.
- Returned appropriate error responses using HTTP 503.
- Used mock requests to test external API responses without depending on an actual internet connection.

**Concepts Included:**
- Third-party API integration.
- External API communication.
- Python Requests library.
- Request timeouts.
- Exception handling.
- HTTP 503 status code.
- Mocking external