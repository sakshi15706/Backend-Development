# ER Diagram: Library Management System

```mermaid
erDiagram
    AUTHOR ||--o{ BOOK_AUTHOR : writes
    BOOK   ||--|{ BOOK_AUTHOR : "written by"
    MEMBER ||--o{ LOAN : borrows
    BOOK   ||--o{ LOAN : "is borrowed in"

    AUTHOR {
        int id PK
        string name
        string nationality
    }
    BOOK {
        int id PK
        string title
        string isbn UK
        string publisher
        int published_year
        int copies_total
        int copies_available
    }
    BOOK_AUTHOR {
        int book_id PK,FK
        int author_id PK,FK
    }
    MEMBER {
        int id PK
        string name
        string email UK
        string phone
        date joined_on
        string status
    }
    LOAN {
        int id PK
        int book_id FK
        int member_id FK
        date loan_date
        date due_date
        date return_date
    }
```

Open this file with the Markdown preview in VS Code (install the "Markdown Preview Mermaid Support" extension if the diagram does not render), or push it to GitHub where it renders automatically. For the lab record you can also export it as an image from https://mermaid.live.

## Cardinality summary
- One Book has one or more Authors, and one Author writes many Books (M:N via `BOOK_AUTHOR`).
- One Member has many Loans, and one Book appears in many Loans (so Member and Book are M:N via `LOAN`).
