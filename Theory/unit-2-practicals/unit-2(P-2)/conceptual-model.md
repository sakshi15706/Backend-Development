# Conceptual Data Model: E-Commerce System

Entities: **Customer, Product, Order, Cart** (plus the helper entities `CartItem` and `OrderItem` that resolve the many-to-many relationships).

```mermaid
erDiagram
    CUSTOMER ||--o| CART : "owns (1 active cart)"
    CUSTOMER ||--o{ ORDER : places
    CART     ||--o{ CART_ITEM : contains
    PRODUCT  ||--o{ CART_ITEM : "added as"
    ORDER    ||--|{ ORDER_ITEM : contains
    PRODUCT  ||--o{ ORDER_ITEM : "sold as"

    CUSTOMER   { int id PK  string name  string email  string phone }
    PRODUCT    { int id PK  string name  string description  decimal price  int stock }
    CART       { int id PK  int customer_id FK  datetime created_at }
    CART_ITEM  { int cart_id PK,FK  int product_id PK,FK  int quantity }
    ORDER      { int id PK  int customer_id FK  datetime placed_at  string status }
    ORDER_ITEM { int order_id PK,FK  int product_id PK,FK  int quantity  decimal unit_price }
```

## Business requirements turned into the model
| Requirement | Modelling decision |
|---|---|
| A customer can place many orders | Customer 1:M Order |
| A customer has one active cart | Customer 1:1 Cart |
| A cart holds many products, a product sits in many carts | Cart M:N Product through `CART_ITEM` |
| An order holds many products | Order M:N Product through `ORDER_ITEM` |
| Prices change over time | `ORDER_ITEM.unit_price` copies the price at the time of purchase |
| Email must be unique, price >= 0, quantity > 0 | constraints on the logical model |

## Three levels (from the lecture)
- **Conceptual:** this diagram (entities and relationships only).
- **Logical:** attributes, data types, keys, constraints (the entity boxes above).
- **Physical:** the actual tables. See `sqlalchemy-app/models.py` for the Student Management System physical model.
