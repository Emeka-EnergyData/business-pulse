# System Architecture

# Overview

Business Pulse follows a layered architecture.

Each layer has a single responsibility and communicates only with the layers directly above or below it.

The application is divided into five major parts:

1. User Interface
2. Business Logic
3. Artificial Intelligence
4. Database
5. Infrastructure

Separating these responsibilities makes the application easier to maintain, test, and extend.

---

## High-Level Architecture

```text

                    User
                      │
                      ▼
              Streamlit Interface
                      │
                      ▼
             Business Services Layer
        (Inventory, Sales, Reports...)
                      │
          ┌───────────┴───────────┐
          │                       │
          ▼                       ▼
      AI Services            Database Layer
          │                       │
          └───────────┬───────────┘
                      ▼
                 PostgreSQL
```

The user never communicates directly with the database.

All operations pass through the business services.

---

## Layer 1 — User Interface

Technology

- Streamlit

Responsibilities

- Display dashboards
- Display tables
- Display charts
- Collect user input
- Record voice (future)
- Display reports

The UI should contain very little business logic.

Its job is simply to send requests to the service layer and display results.

---

## Layer 2 — Business Services

This is the heart of the application.

Examples include:

- Inventory Service
- Sales Service
- Customer Service
- Supplier Service
- Credit Service
- Reporting Service

Responsibilities

- Validate data
- Apply business rules
- Perform calculations
- Coordinate database operations
- Call AI when necessary

Example

When a sale is recorded:

The Inventory Service should:

1. Save the sale.
2. Reduce stock.
3. Calculate profit.
4. Update dashboard metrics.

The Streamlit page should never perform these operations directly.

---

## Layer 3 — AI Services

AI is completely independent from the core application.

Responsibilities

- Speech transcription
- Structured information extraction
- Report generation
- Natural language search
- Business insights

The rest of the application should continue working if AI is disabled.

This is an important architectural principle.

---

## Layer 4 — Database Layer

Technology

- PostgreSQL

Responsibilities

- Store business information
- Maintain relationships
- Preserve data integrity

Examples of stored data:

- Products
- Sales
- Customers
- Suppliers
- Credit
- Inventory movements

The database should never contain AI logic.

---

## Layer 5 — Infrastructure

Infrastructure includes everything required to run the application.

Examples

- Docker
- Docker Compose
- Environment variables
- Persistent volumes
- Database backups

Infrastructure should be replaceable without affecting business logic.

---

## Data Flow

Manual Workflow

```text
User

↓

Streamlit Page

↓

Business Service

↓

PostgreSQL

↓

Updated Dashboard
```

AI Workflow:

```text
User

↓

Voice

↓

Speech Recognition

↓

AI Extraction

↓

Business Service

↓

PostgreSQL

↓

Dashboard
```

No component writes directly to the database except through the service layer.

---

## Why This Architecture?

This design provides:

- Separation of concerns
- Easier testing
- Easier maintenance
- Easier debugging
- Reusable business logic
- Future scalability

For example:

The Inventory Service can later be used by:

- Streamlit
- Mobile App
- REST API

without rewriting business logic.

---

Guiding Principles

1. The UI should not contain business logic.

2. Business rules belong inside services.

3. AI is an optional assistant, never a dependency.

4. The database is the single source of truth.

5. Every layer should have one clear responsibility.

6. Features should be modular so they can be reused across different businesses.

---

## Future Architecture

The initial version is a desktop application.

The architecture should allow future expansion into:

- Web application
- Mobile application
- Multi-branch businesses
- Cloud deployment
- Multi-user authentication
- Remote synchronization

without redesigning the core business logic.

business-pulse/
│
├── Home.py                      # Streamlit entry point
├── requirements.txt
├── docker-compose.yml
├── .env
├── .gitignore
├── README.md
│
├── pages/                       # Streamlit pages
│   ├── 1_Dashboard.py
│   ├── 2_Products.py
│   ├── 3_Sales.py
│   ├── 4_Customers.py
|   ├── 5_Credit.py
│   ├── 6_Suppliers.py
│   ├── 7_Reports.py
│
├── src/
│   ├── database/
│   │   ├── connection.py        # SQLAlchemy engine/session
│   │   ├── base.py              # Declarative Base
│   │   ├── models/              # SQLAlchemy models
│   │   │   ├── category.py
│   │   │   ├── product.py
│   │   │   ├── supplier.py
│   │   │   ├── purchase.py
│   │   │   ├── purchase_item.py
│   │   │   ├── customer.py
│   │   │   ├── sale.py
│   │   │   ├── sale_item.py
│   │   │   ├── payment.py
│   │   │   └── stock_movement.py
│   │   │
│   │   └── migrations/          # Alembic migrations
│   │
│   ├── services/                # Business logic
│   │   ├── inventory_service.py
│   │   ├── sales_service.py
│   │   ├── customer_service.py
│   │   ├── supplier_service.py
│   │   ├── payment_service.py
│   │   └── report_service.py
│   │
│   ├── ai/
│   │   ├── speech_to_text.py
│   │   ├── ollama_client.py
│   │   ├── prompts.py
│   │   └── insights.py
│   │
│   ├── utils/
│   │   ├── enums.py
│   │   ├── validators.py
│   │   ├── helpers.py
│   │   └── constants.py
│   │
│   └── config.py                # Application configuration
│
├── docs/
│   ├── 01_product_vision.md
│   ├── 02_system_architecture.md
│   ├── 03_database_design.md
│   ├── 04_ai_design.md
│   ├── 05_deployment.md
│   └── 06_api_reference.md      # Reserved for future use
│
├── tests/
│
└── scripts/