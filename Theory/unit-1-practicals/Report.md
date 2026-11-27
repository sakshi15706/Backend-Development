# Backend Development Lab Report – Unit 1
## Web Fundamentals and Frameworks

## 1. Introduction

Unit 1 focuses on the fundamentals of backend development, web technologies, HTTP communication, APIs, client-side storage, session management, and server-side rendering.

The practicals helped in understanding how frontend and backend applications communicate, how servers handle client requests, how data is stored, and how dynamic web pages are generated using different backend frameworks.

A total of six practicals were completed using Node.js, Express.js, Flask, FastAPI, Python, HTML, CSS, JavaScript, EJS, and Jinja2.

## 2. Practical Work and Concepts Covered

### Practical 1: Node.js and Express Environment

**Objective:** To set up a backend development environment using Node.js and Express.js and create a basic web server.

**Work Performed:**
- Installed and configured Node.js and npm.
- Created an Express.js application.
- Implemented different routes such as `/`, `/about`, and `/api/time`.
- Created a POST API endpoint `/api/echo`.
- Used middleware to process incoming requests.
- Tested the server using a web browser and API requests.

**Concepts Included:**
- Introduction to Node.js.
- Express.js framework.
- Server creation and configuration.
- Routing and middleware.
- GET and POST requests.
- JSON responses.

### Practical 2: HTTP Requests and Methods

**Objective:** To understand HTTP communication between clients and servers using Flask and Python Requests.

**Work Performed:**
- Created a Flask application to handle HTTP requests.
- Implemented GET, POST, PUT, and DELETE methods.
- Used query strings to pass information through URLs.
- Implemented HTTP status codes and custom response headers.
- Created a Python client using the Requests library.
- Tested communication between the client and server.

**Concepts Included:**
- HTTP request-response cycle.
- HTTP methods.
- Status codes.
- Request and response headers.
- Query parameters.
- Flask framework.
- Python Requests library.

### Practical 3: RESTful API Using FastAPI

**Objective:** To develop a RESTful API using FastAPI with data validation and automatic API documentation.

**Work Performed:**
- Created a FastAPI application for managing book records.
- Implemented endpoints to perform CRUD operations.
- Used Pydantic models for data validation.
- Implemented query parameters.
- Tested API endpoints using Swagger UI.
- Accessed automatic API documentation through `/docs`.

**Concepts Included:**
- REST architecture.
- FastAPI framework.
- CRUD operations.
- Pydantic data validation.
- Query parameters.
- HTTP methods.
- Automatic API documentation.
- Swagger UI.

### Practical 4: Sessions, Cookies and Query Strings

**Objective:** To understand how web applications maintain user information using cookies and server-side sessions.

**Work Performed:**
- Created an Express.js application.
- Implemented query strings to transfer information through URLs.
- Used cookies to store information in the browser.
- Implemented server-side sessions using `express-session`.
- Explored how session IDs connect browsers with server-side session data.

**Concepts Included:**
- Stateless nature of HTTP.
- Query strings.
- Cookies.
- Session management.
- Express-session middleware.
- Client-side and server-side state management.

### Practical 5: LocalStorage, SessionStorage and JSON

**Objective:** To understand browser-based storage mechanisms and JSON data handling using HTML, CSS, and JavaScript.

**Work Performed:**
- Created a browser-based web page.
- Implemented LocalStorage to store data persistently.
- Used SessionStorage to store temporary session data.
- Implemented JSON.stringify() to convert JavaScript objects into JSON strings.
- Used JSON.parse() to convert JSON strings back into JavaScript objects.
- Tested data storage and retrieval through browser developer tools.

**Concepts Included:**
- HTML structure.
- CSS styling.
- JavaScript functionality.
- LocalStorage.
- SessionStorage.
- JSON serialization and deserialization.
- Browser developer tools.

### Practical 6: Server-Side Rendering Using EJS and Jinja2

**Objective:** To understand server-side rendering by generating dynamic HTML pages using EJS and Jinja2 templates.

**Work Performed:**
- Created an Express.js application using EJS templates.
- Created a Flask application using Jinja2 templates.
- Designed HTML templates for displaying dynamic content.
- Connected backend routes with frontend templates.
- Compared template rendering using both frameworks.

**Concepts Included:**
- Server-side rendering (SSR).
- EJS templating engine.
- Jinja2 templating engine.
- Dynamic HTML generation.
- Template variables.
- Express.js and Flask integration.

## 3. Technologies and Tools Used

The following technologies and tools were used throughout the practicals:

| Technology/Tool | Purpose |
|---|---|
| Node.js | JavaScript runtime for backend development |
| Express.js | Creating web servers and APIs |
| Python | Backend programming |
| Flask | Developing web applications and APIs |
| FastAPI | Building RESTful APIs |
| Pydantic | Data validation |
| EJS | Server-side templating |
| Jinja2 | Server-side templating |
| HTML | Creating webpage structure |
| CSS | Styling webpages |
| JavaScript | Client-side functionality |
| npm | Managing Node.js packages |
| Requests | Sending HTTP requests using Python |
| Swagger UI | Testing and documenting APIs |
| VS Code | Writing and managing code |
| Browser DevTools | Inspecting cookies and browser storage |

## 4. Problems Faced During the Practicals

While completing the Unit 1 practicals, I encountered some difficulties during environment setup, application development, and testing.

1. **Environment Configuration:** Initially, setting up Node.js, npm, Python, and the required dependencies was challenging. Some packages needed to be installed separately for individual practical folders.

2. **Package Installation:** Faced difficulties installing and managing dependencies using npm and pip. Incorrect installation paths and missing packages sometimes prevented applications from running.

3. **Server Execution:** Understanding how to start backend servers and access them through localhost was initially confusing. Incorrect commands and port-related issues also caused difficulties.

4. **HTTP Methods:** Understanding the differences between GET, POST, PUT, and DELETE requests and how each method handles data required practice.

5. **API Testing:** Testing API endpoints, interpreting HTTP status codes, and understanding request and response headers took additional effort.

6. **Data Validation:** Implementing Pydantic models in FastAPI and understanding how invalid input is handled required careful testing.

7. **Session and Cookie Management:** Understanding the difference between browser cookies and server-side sessions was challenging, especially how session IDs maintain user state.

8. **Browser Storage:** Understanding the difference between LocalStorage and SessionStorage and handling JSON conversion using `JSON.stringify()` and `JSON.parse()` required practical experimentation.

9. **Template Rendering:** Integrating EJS with Express and Jinja2 with Flask required understanding how backend data is passed to HTML templates.

10. **Terminal Commands:** Working with multiple practical folders and executing commands from the correct directory required attention, especially when folder names contained brackets.

These problems were resolved through debugging, checking installation requirements, correcting commands, and testing the applications.

## 5. Learning Outcomes

After completing the six practicals, I gained an understanding of:

- Setting up and running backend servers using Node.js and Python.
- Creating web applications using Express.js and Flask.
- Understanding HTTP methods and the request-response cycle.
- Developing RESTful APIs using FastAPI.
- Performing CRUD operations and validating API data.
- Managing user information using cookies and sessions.
- Storing data in browsers using LocalStorage and SessionStorage.
- Handling JSON data in JavaScript.
- Generating dynamic webpages using EJS and Jinja2.
- Testing backend applications using browsers, API requests, and Swagger UI.

## 6. Conclusion

Unit 1 provided practical knowledge of web fundamentals and backend development frameworks. Through these six practicals, I learned how to create backend servers, handle HTTP requests, develop RESTful APIs, manage user sessions, store browser data, and generate dynamic web pages.

Working with Node.js, Express.js, Flask, and FastAPI helped me understand different approaches to backend development. I also gained experience in debugging errors, installing dependencies, managing project folders, and testing applications.

Overall, these practicals strengthened my understanding of the basic concepts required to develop and manage backend web applications.