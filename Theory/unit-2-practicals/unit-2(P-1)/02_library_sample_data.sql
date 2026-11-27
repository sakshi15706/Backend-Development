-- P-1: sample data for the Library Management System
INSERT INTO authors (id, name, nationality) VALUES
 (1, 'Robert C. Martin', 'American'),
 (2, 'Andrew Hunt',      'American'),
 (3, 'David Thomas',     'British'),
 (4, 'Martin Fowler',    'British');

INSERT INTO books (id, title, isbn, publisher, published_year, copies_total, copies_available) VALUES
 (1, 'Clean Code',                '9780132350884', 'Prentice Hall',    2008, 3, 2),
 (2, 'The Pragmatic Programmer',  '9780135957059', 'Addison-Wesley',   2019, 2, 2),
 (3, 'Refactoring',               '9780134757599', 'Addison-Wesley',   2018, 2, 1);

-- 'The Pragmatic Programmer' has TWO authors
INSERT INTO book_authors (book_id, author_id) VALUES
 (1, 1), (2, 2), (2, 3), (3, 4);

INSERT INTO members (id, name, email, phone, joined_on) VALUES
 (1, 'Aarav', 'aarav@upes.ac.in', '9876501001', '2024-08-01'),
 (2, 'Diya',  'diya@upes.ac.in',  '9876501002', '2024-08-05');

-- Aarav borrows TWO books, Diya borrows one
INSERT INTO loans (id, book_id, member_id, loan_date, due_date, return_date) VALUES
 (1, 1, 1, '2024-09-01', '2024-09-15', NULL),
 (2, 3, 1, '2024-09-02', '2024-09-16', NULL),
 (3, 1, 2, '2024-08-20', '2024-09-03', '2024-09-01');
