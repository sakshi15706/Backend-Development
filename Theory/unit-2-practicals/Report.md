# Backend Development Lab Report – Unit 2
## Database Design, REST APIs, Security and Deployment

## 1. Introduction

Unit 2 focuses on database design, data modelling, REST API development, database optimisation, authentication, authorisation, security, API documentation, testing, and deployment.

The practicals helped in understanding how backend applications interact with databases, how APIs are designed and secured, how user permissions are managed, and how applications are prepared for deployment.

A total of eleven practicals were completed using Python, SQL, SQLite, SQLAlchemy, Mongoose, FastAPI, Pydantic, JWT, bcrypt, and pytest.

## 2. Practical Work and Concepts Covered

### Practical 1: Database Design and Normalisation

**Objective:** To understand relational database design, SQL schemas, constraints, and database normalisation.

**Work Performed:**
- Designed a library management database.
- Created tables for books, members, loans, authors, and related entities.
- Implemented primary keys and foreign keys.
- Applied UNIQUE, NOT NULL, and CHECK constraints.
- Added sample records to the database.
- Studied database normalisation from 1NF to 3NF.
- Created an ER diagram using Mermaid.
- Executed SQL scripts using SQLite and tested constraint violations.

**Concepts Included:**
- Relational database management systems.
- Database schema design.
- Primary and foreign keys.
- SQL constraints.
- Entity Relationship diagrams.
- Database normalisation (1NF, 2NF, 3NF).
- SQLite.

### Practical 2: Data Modelling Using SQLAlchemy and Mongoose

**Objective:** To understand data modelling and database operations using SQLAlchemy and Mongoose.

**Work Performed:**
- Created a conceptual database model.
- Defined SQLAlchemy models and relationships.
- Implemented CRUD operations using SQLAlchemy.
- Created blog schemas using Mongoose.
- Added validation rules for Mongoose schemas.
- Performed validation testing without requiring a database connection.

**Concepts Included:**
- Data modelling.
- Object Relational Mapping (ORM).
- SQLAlchemy.
- Mongoose.
- Database relationships.
- CRUD operations.
- Schema validation.

### Practical 3: CRUD API with a Database

**Objective:** To develop a database-connected REST API for managing courses, departments, and students.

**Work Performed:**
- Created database models for courses, departments, and students.
- Established relationships using foreign keys.
- Implemented CRUD operations through API endpoints.
- Added filtering and pagination.
- Wrote equivalent SQL queries.
- Tested API functionality using automated pytest tests.
- Prepared Postman testing instructions.

**Concepts Included:**
- Database integration with APIs.
- CRUD operations.
- Foreign key relationships.
- FastAPI.
- SQL queries.
- Filtering and pagination.
- API testing.

### Practical 4: Query Optimisation, Indexing and Connection Pooling

**Objective:** To understand database performance improvement through indexing, query optimisation, and connection pooling.

**Work Performed:**
- Created a database containing 100,000 student records.
- Compared query execution times with and without indexes.
- Analysed query execution plans.
- Identified slow SQL queries.
- Optimised queries using indexing and LIMIT.
- Compared pooled and unpooled database connections.
- Used a FastAPI application to demonstrate database connectivity.

**Concepts Included:**
- Database indexing.
- Query optimisation.
- SQL execution plans.
- Full table scans.
- Index-based searching.
- Connection pooling.
- Database performance benchmarking.

**Observations:**
- Indexing improved query performance, especially for common branch searches.
- Query execution plans changed from table scans to index-based searches.
- Using LIMIT reduced the number of returned records and improved response time.
- Performance measurements depended on database size and system resources.

### Practical 5: REST API Design Principles

**Objective:** To understand the principles and best practices of designing RESTful APIs.

**Work Performed:**
- Designed a library management REST API.
- Used plural nouns for resource endpoints.
- Implemented appropriate HTTP methods.
- Applied suitable HTTP status codes.
- Created consistent error response structures.
- Implemented pagination.
- Documented API design decisions.

**Concepts Included:**
- REST architecture.
- Resource-based URLs.
- HTTP methods.
- HTTP status codes.
- Error handling.
- API response consistency.
- Pagination.
- REST API best practices.

### Practical 6: Student Management API

**Objective:** To develop a Student Management API for managing departments, students, courses, and enrolments.

**Work Performed:**
- Created API endpoints for departments, students, courses, and enrolments.
- Implemented CRUD operations.
- Used PUT for complete resource replacement.
- Used PATCH for partial resource updates.
- Created nested endpoints for student enrolments.
- Implemented database constraints.
- Handled conflict responses using HTTP 409.

**Concepts Included:**
- Student management systems.
- REST API development.
- CRUD operations.
- PUT and PATCH methods.
- Nested resources.
- Database constraints.
- HTTP conflict handling.

### Practical 7: JWT Authentication

**Objective:** To implement secure user authentication using JSON Web Tokens.

**Work Performed:**
- Created user registration and login endpoints.
- Implemented password hashing using bcrypt.
- Generated JWT tokens after successful authentication.
- Added token expiration.
- Created a protected `/me` endpoint.
- Implemented ownership checks.
- Tested authentication and authorisation behaviour.

**Concepts Included:**
- User authentication.
- JSON Web Tokens (JWT).
- Password hashing.
- bcrypt.
- Token generation and verification.
- Token expiration.
- Protected API endpoints.
- OAuth2 password form.

### Practical 8: Role-Based Access Control

**Objective:** To implement role-based access control for managing permissions of different users.

**Work Performed:**
- Created roles for admin, faculty, and student.
- Defined permissions for different user roles.
- Implemented access restrictions for API endpoints.
- Applied the deny-by-default security approach.
- Implemented ownership-based permissions.
- Restricted role changes to administrators.
- Added audit logging.
- Retrieved user roles from the database.

**Concepts Included:**
- Role-Based Access Control (RBAC).
- Authentication and authorisation.
- User permissions.
- Access control.
- Ownership validation.
- Audit logging.
- Secure API development.

### Practical 9: Validation, Rate Limiting and File Upload

**Objective:** To understand API security through input validation, rate limiting, and secure file uploads.

**Work Performed:**
- Implemented field-level and cross-field validation.
- Created consistent validation error responses.
- Implemented a sliding-window rate limiter.
- Tested rate limiting using an injectable clock.
- Added file upload functionality.
- Validated file extensions and file sizes.
- Checked file magic bytes.
- Generated server-side filenames for uploaded files.

**Concepts Included:**
- Input validation.
- Pydantic validators.
- HTTP 422 status code.
- API rate limiting.
- Sliding-window algorithm.
- File upload security.
- File type validation.
- Secure filename handling.

### Practical 10: OpenAPI Documentation, Versioning and Postman

**Objective:** To understand API documentation, version management, and API testing using Postman.

**Work Performed:**
- Customised OpenAPI documentation.
- Added API metadata and examples.
- Implemented versioned API endpoints using `/v1` and `/v2`.
- Added deprecation-related response headers.
- Implemented pagination in the newer API version.
- Generated a Postman collection from the API schema.
- Created development and production environments.
- Tested API endpoints using automated tests.

**Concepts Included:**
- OpenAPI specification.
- Swagger documentation.
- API versioning.
- API deprecation.
- Postman collections.
- Environment variables.
- API testing.
- Pagination.

### Practical 11: Assignment Review, Refactoring, Testing and Deployment

**Objective:** To understand code quality, project structure, testing, refactoring, and deployment preparation.

**Work Performed:**
- Created a layered backend project structure.
- Separated routers, services, models, schemas, configurations, and exceptions.
- Implemented automated tests using pytest.
- Performed mutation testing to verify access-control checks.
- Exported OpenAPI documentation.
- Created a Dockerfile and deployment configuration.
- Prepared deployment documentation.
- Created a code review checklist and peer-review template.
- Prepared refactoring notes.
- Tested production-mode configuration and application health endpoints.

**Concepts Included:**
- Software refactoring.
- Modular project architecture.
- Code organisation.
- Automated testing.
- Mutation testing.
- Docker.
- Deployment configuration.
- Production environment.
- API health checks.
- Code review.

## 3. Technologies and Tools Used

| Technology/Tool | Purpose |
|---|---|
| Python | Backend programming |
| SQL | Database operations |
| SQLite | Relational database management |
| SQLAlchemy | Object Relational Mapping |
| Mongoose | MongoDB data modelling |
| FastAPI | REST API development |
| Pydantic | Data validation |
| JWT | Token-based authentication |
| bcrypt | Password hashing |
| pytest | Automated testing |
| Postman | API testing |
| OpenAPI | API documentation |
| Swagger UI | Interactive API documentation |
| Docker | Application containerisation |
| Uvicorn | Running FastAPI applications |
| Mermaid | ER diagram creation |
| VS Code | Code development and management |

## 4. Testing and Verification

Automated testing was performed throughout the practicals to verify API functionality, database operations, validation, authentication, and security.

| Practical | Automated Tests Passed |
|---|---:|
| P-1 | SQL constraint verification |
| P-2 | Mongoose validation test |
| P-3 | 7 |
| P-4 | Benchmark scripts executed |
| P-5 | 7 |
| P-6 | 8 |
| P-7 | 26 |
| P-8 | 23 |
| P-9 | 37 |
| P-10 | 15 |
| P-11 | 28 |

A total of **151 automated pytest tests passed**, along with additional SQL constraint checks and Mongoose validation tests.

## 5. Problems Faced During the Practicals

While completing Unit 2, I encountered several difficulties related to database management, API development, security implementation, testing, and deployment.

1. **Database Design:** Understanding relationships between different tables and implementing primary keys, foreign keys, and database constraints required careful planning.

2. **Database Normalisation:** Understanding the differences between 1NF, 2NF, and 3NF and eliminating data redundancy was initially challenging.

3. **SQLAlchemy and Mongoose:** Working with two different data modelling approaches required understanding their syntax, schemas, relationships, and validation methods.

4. **Database Connectivity:** Configuring database connections and understanding how backend applications communicate with databases required additional practice.

5. **Query Optimisation:** Understanding database indexes, execution plans, and the difference between table scans and index searches was challenging.

6. **REST API Design:** Selecting appropriate HTTP methods, status codes, endpoint structures, and response formats required careful implementation.

7. **Authentication:** Implementing JWT authentication, password hashing, token generation, and token expiration required understanding several security concepts.

8. **Role-Based Access Control:** Managing different permissions for administrators, faculty, and students and implementing ownership-based access restrictions was challenging.

9. **Input Validation and File Upload:** Applying validation rules, handling invalid requests, and checking uploaded files for security required additional testing.

10. **API Versioning:** Understanding how to maintain multiple API versions and handle deprecated endpoints required learning new API design concepts.

11. **Automated Testing:** Writing pytest test cases, understanding failed test results, and debugging errors helped improve the reliability of the applications.

12. **Deployment Configuration:** Preparing Docker and cloud deployment files required understanding production configurations and environment variables. Actual Docker image building and cloud deployment were not completed during the practical verification.

These difficulties were addressed through debugging, reading documentation, testing different API requests, modifying code, and running automated test cases.

## 6. Learning Outcomes

After completing the eleven practicals, I gained knowledge of:

- Designing relational databases and creating SQL schemas.
- Understanding database normalisation and relationships.
- Performing CRUD operations using SQLAlchemy.
- Understanding Mongoose schemas and validation.
- Developing database-connected REST APIs.
- Optimising database queries using indexes.
- Understanding connection pooling.
- Following REST API design principles.
- Implementing JWT-based authentication.
- Applying password hashing using bcrypt.
- Implementing role-based access control.
- Securing APIs using validation and rate limiting.
- Handling file uploads securely.
- Creating API documentation using OpenAPI and Swagger.
- Managing API versions using Postman.
- Writing automated tests using pytest.
- Understanding code refactoring and deployment preparation.

## 7. Conclusion

Unit 2 provided practical knowledge of database design, REST API development, backend security, testing, and deployment preparation.

Through these eleven practicals, I learned how to design relational databases, connect databases with backend applications, develop RESTful APIs, optimise queries, implement authentication and authorisation, validate user inputs, and manage API documentation.

Working with SQLAlchemy, Mongoose, FastAPI, JWT, bcrypt, and pytest helped me understand different aspects of modern backend development.

The practicals also improved my debugging, problem-solving, database management, and software testing skills. Overall, Unit 2 strengthened my understanding of how to develop secure, efficient, structured, and maintainable backend applications.