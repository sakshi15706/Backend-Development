-- P-1 Part 2: Library Management System schema
-- Works on MySQL 8+, PostgreSQL and SQLite (ids are supplied explicitly in the sample data).
-- For auto ids: MySQL -> "id INT AUTO_INCREMENT PRIMARY KEY", PostgreSQL -> "id SERIAL PRIMARY KEY".

DROP TABLE IF EXISTS loans;
DROP TABLE IF EXISTS book_authors;
DROP TABLE IF EXISTS members;
DROP TABLE IF EXISTS books;
DROP TABLE IF EXISTS authors;

CREATE TABLE authors (
    id          INT PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    nationality VARCHAR(50)
);

CREATE TABLE books (
    id               INT PRIMARY KEY,
    title            VARCHAR(200) NOT NULL,
    isbn             VARCHAR(20)  NOT NULL UNIQUE,
    publisher        VARCHAR(100),
    published_year   INT CHECK (published_year BETWEEN 1400 AND 2100),
    copies_total     INT NOT NULL DEFAULT 1 CHECK (copies_total >= 1),
    copies_available INT NOT NULL DEFAULT 1 CHECK (copies_available >= 0),
    CHECK (copies_available <= copies_total)
);

-- M:N  Book <-> Author  (a book can have multiple authors, an author can write many books)
CREATE TABLE book_authors (
    book_id   INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id)   REFERENCES books(id)   ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE TABLE members (
    id        INT PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    email     VARCHAR(100) NOT NULL UNIQUE,
    phone     VARCHAR(20),
    joined_on DATE NOT NULL DEFAULT CURRENT_DATE,
    status    VARCHAR(10) NOT NULL DEFAULT 'ACTIVE' CHECK (status IN ('ACTIVE', 'SUSPENDED'))
);

-- M:N  Member <-> Book  resolved by the Loan entity (a member borrows many books, a book is borrowed many times)
CREATE TABLE loans (
    id          INT PRIMARY KEY,
    book_id     INT  NOT NULL,
    member_id   INT  NOT NULL,
    loan_date   DATE NOT NULL,
    due_date    DATE NOT NULL,
    return_date DATE,
    FOREIGN KEY (book_id)   REFERENCES books(id),
    FOREIGN KEY (member_id) REFERENCES members(id),
    CHECK (due_date >= loan_date),
    CHECK (return_date IS NULL OR return_date >= loan_date)
);

CREATE INDEX idx_loans_member ON loans(member_id);
CREATE INDEX idx_loans_book   ON loans(book_id);
