# Business Pulse

Business Pulse is an AI-assisted business operations and inventory management system designed for small businesses.

It helps business owners record and understand their day-to-day operations through a centralized system for sales, inventory, purchases, customers, suppliers, payments, credit, and business reporting.

The goal is simple: turn scattered business records into useful operational information that a business owner can actually use to make decisions.

> **Note:** Business Pulse is not intended to replace accounting software. It focuses on operational visibility and day-to-day business management.

## Live Demo

[Business Pulse Live Demo](https://business-pulse.onrender.com/)

> **Note:** The live demo uses synthetic data for demonstration purposes.

---

## The Problem

Many small businesses still manage their operations using notebooks, spreadsheets, or a combination of both.

This can make it difficult to quickly answer questions such as:

- How much did I sell today?
- Which products are selling the most?
- What inventory do I currently have?
- How much stock did I receive?
- Which customers owe me money?
- How much has a customer paid?
- What products are contributing to revenue?
- How is the business performing over time?

Business Pulse brings these operational records into one system and turns them into dashboards, reports, and AI-assisted insights.

---

## Key Features

### Inventory Management

- Create and manage products and categories
- Track current stock
- Record stock received from suppliers
- Record stock sold
- Track damaged, stolen, and adjusted stock
- Maintain an inventory movement history

Inventory changes are represented through stock movements, providing a record of how inventory changed over time.

### Sales Management

- Record customer transactions
- Support walk-in customers
- Add multiple products to a sale
- Record negotiated selling prices
- Track sales totals
- Calculate outstanding balances
- Track payment status

Sales are separated into "Sale" and "SaleItem" records so that one transaction can contain multiple products.

### Customer & Credit Management

- Maintain customer records
- View customer purchase history
- Track credit sales
- Record customer payments
- Track outstanding balances
- Support partial and installment payments

### Supplier & Purchase Management

- Manage suppliers
- Record purchases from suppliers
- Add multiple products to a purchase
- Track quantities received
- Track purchase costs
- Connect purchases with inventory movements

### Reports & Business Insights

Business Pulse provides reports that transform transactional data into useful business information.

Reports can be used to understand:

- Sales performance
- Product performance
- Inventory
- Purchases
- Customer activity
- Credit and payments
- Revenue and profit-related metrics

### AI-Assisted Analysis

AI is used as an assistant, rather than as the source of truth for business data.

Business Pulse uses Google's Gemini API to provide AI-generated business insights and conversational analysis.

The AI can work with business information from the application's reports to help users understand patterns and performance.

The core application does not depend on AI to perform normal business operations.

---

## Architecture

Business Pulse follows a layered architecture that separates the user interface, business logic, AI functionality, and data persistence.

```text
                     User
                       │
                       ▼
                Streamlit UI
                       │
                       ▼
              Business Services
                │            │
                │            │
                ▼            ▼
          PostgreSQL       AI Services
                │            │
                └──────┬─────┘
                       ▼
                 Business Data
```

### User Interface

The application interface is built with Streamlit.

The UI is responsible for:

- Collecting user input
- Displaying dashboards
- Displaying tables and reports
- Presenting business insights

### Business Services

Business logic is separated from the Streamlit pages.

Services handle operations such as:

- Sales
- Inventory
- Customers
- Suppliers
- Purchases
- Payments
- Reporting

This keeps business rules out of the UI and makes the underlying functionality easier to test and reuse.

### Database

PostgreSQL acts as the primary source of truth.

SQLAlchemy 2.0 is used as the ORM and database interaction layer.

Alembic manages database schema migrations.

### AI Layer

AI functionality is separated from the core business logic.

The application currently uses:

- Google Gemini API for production AI functionality
- Ollama for local AI experimentation

This separation means that the core business operations can continue independently of the AI layer.

---

## Database Design

The database is built around the major events and entities involved in running a small business.

```text
Category
   │
   └── Product
          │
          ├── PurchaseItem ── Purchase ── Supplier
          │
          ├── SaleItem ───── Sale ────── Customer
          │                    │
          │                    └──────── Payment
          │
          └── StockMovement
```

### Main Tables

| Table | Purpose |
|-------|---------|
| `categories` | Product categorization |
| `products` | Product information and current stock |
| `suppliers` | Supplier information |
| `purchases` | Purchase/stock receipt records |
| `purchase_items` | Products received in purchases |
| `customers` | Customer information |
| `sales` | Sale transaction headers |
| `sale_items` | Products sold in each sale |
| `payments` | Payments made toward sales |
| `stock_movements` | Inventory movement history |

### Historical Pricing

A product's current price can change over time.

For this reason, "SaleItem" stores the actual selling price and cost price at the time of the transaction.

This preserves historical sales information even when the product's current price changes later.

### Inventory History

Inventory changes are tracked through "StockMovement".

Examples include:

- `RECEIVED`
- `SOLD`
- `DAMAGED`
- `STOLEN`
- `ADJUSTMENT`

This provides an audit trail of inventory activity rather than relying only on the current stock number.

---

## Technology Stack

### Application

- Python
- Streamlit
- Pandas

### Database

- PostgreSQL
- SQLAlchemy 2.0
- Alembic
- Psycopg 3

### Artificial Intelligence

- Google Gemini API
- Ollama

### Infrastructure

- Docker
- Docker Compose
- Render

### Development

- Git
- GitHub
- Pytest

---

## Project Structure

```text
business-pulse/
│
├── Home.py
├── pages/
│   ├── 1_Dashboard.py
│   ├── 2_Products.py
│   ├── 3_Sales.py
│   ├── 4_Customers.py
│   ├── 5_Credit.py
│   ├── 6_Suppliers.py
│   └── 7_Reports.py
│
├── src/
│   ├── database/
│   │   ├── connection.py
│   │   ├── base.py
│   │   ├── models/
│   │   └── migrations/
│   │
│   ├── repositories/
│   │
│   ├── services/
│   │
│   ├── ai/
│   │   └── ...
│   │
│   └── utils/
│
├── scripts/
│   ├── seed_data.sql
│   └── ...
│
├── docs/
├── tests/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── alembic.ini
├── start.sh
└── README.md
```

---

## Running Locally

### Prerequisites

You will need:

- Python 3.12+
- PostgreSQL
- Docker and Docker Compose
- Git

### Clone the repository

```bash
git clone https://github.com/Emeka-EnergyData/business-pulse.git
cd business-pulse
```

### Create a virtual environment

```bash
python -m venv .venv
```

#### Activate it on Windows:

```bash
.venv\Scripts\Activate.ps1
```

#### On macOS/Linux:

```bash
source .venv/bin/activate
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file using `.env.example` as a reference.

The application uses environment variables for database configuration and AI credentials.

Example:

```text
POSTGRES_HOST=localhost
POSTGRES_PORT=5433
POSTGRES_DB=business_pulse
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

TEST_POSTGRES_DB=business_pulse_test

OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b

GEMINI_API_KEY=your_api_key
GEMINI_MODEL=gemini-3.7-flash
```

For production, `DATABASE_URL` is used instead of the local PostgreSQL connection variables.

### Start PostgreSQL

The project includes Docker Compose configuration for the local database.

```bash
docker compose up -d
```

### Run database migrations

```bash
alembic upgrade head
```

### Seed demonstration data

Synthetic demonstration data is provided in `scripts/seed_data.sql`.

It can be loaded into the database with:

```bash
psql "$DATABASE_URL" -f scripts/seed_data.sql
```

For local development, use the appropriate PostgreSQL connection configuration for your environment.

### Start the application

```bash
streamlit run Home.py
```

The application will be available through the Streamlit local URL.

---

## Database Migrations

Business Pulse uses Alembic to manage database schema changes.

### Create a migration after modifying the models:

```bash
alembic revision --autogenerate -m "describe change"
```

### Apply migrations:

```bash
alembic upgrade head
```

The production container automatically runs:

```bash
alembic upgrade head
```

before starting the Streamlit application.

---

## Deployment

Business Pulse is containerized with Docker and deployed to Render.

The production deployment consists of:

```text
GitHub
   │
   ▼
Render
   │
   ├── Docker Web Service
   │
   └── PostgreSQL
          │
          ▼
     Business Pulse
```

The container:

1. Installs the application dependencies.
2. Runs the latest Alembic migrations.
3. Seeds the demonstration database when required.
4. Starts the Streamlit application.

Production secrets such as the Gemini API key and database connection string are supplied through environment variables rather than committed to the repository.

---

## Testing

The project includes automated tests for core application functionality.

Testing focuses on validating business rules and database operations rather than only testing the Streamlit interface.

Examples include testing:

- Product operations
- Sales
- Sale items
- Purchases
- Payments
- Customers
- Suppliers
- Inventory movements

---

## Important Design Decisions

### Business Logic Is Separated From the UI

Streamlit pages should not be responsible for implementing core business rules.

Instead:

```text
Streamlit
    ↓
Service
    ↓
Repository / Database
```

This makes the application easier to maintain and allows the underlying business logic to potentially be reused by another interface in the future.

### AI Is an Assistant

AI does not represent the underlying business data.

Business transactions are stored and calculated by the application's normal database and service layers.

AI is used to help interpret information and provide additional assistance.

### Transactional Data Is Preserved

Business records such as sales, payments, purchases, and stock movements represent historical events.

Preserving these records allows the application to generate reports and analyze business activity over time.

### PostgreSQL as the Source of Truth

The database is responsible for persistent business information.

AI-generated responses are not treated as authoritative business records.

---

## Current MVP Scope

The current version focuses on:

- Product management
- Inventory management
- Sales
- Purchases
- Suppliers
- Customers
- Customer credit
- Payments
- Business reports
- AI-assisted reports and insights
- AI-assisted business chat
- PostgreSQL persistence
- Dockerized deployment

The application currently targets a single-business, single-user MVP.

---

## Future Improvements

Potential future improvements include:

- User authentication
- Multiple users and roles
- Multiple business branches
- Barcode scanning
- Receipt generation and printing
- Product images
- Expense tracking
- Customer returns
- Purchase returns
- Mobile access
- More advanced inventory forecasting
- Improved AI business analysis
- Notifications and alerts

These features are outside the scope of the current MVP.

---

## Project Motivation

Business Pulse was built to explore how software engineering, data analytics, database design, and AI can be combined to solve a practical business problem.

The project provided an opportunity to work across the full application lifecycle:

```text
Business Problem
      ↓
Requirements
      ↓
Database Design
      ↓
Business Logic
      ↓
Application Development
      ↓
AI Integration
      ↓
Testing
      ↓
Docker
      ↓
Cloud Deployment
```

Rather than building AI as a standalone feature, the project explores how AI can be integrated into an operational system where reliable business data remains the foundation.

---

## Status

MVP deployed and operational.

Business Pulse is currently a portfolio/MVP project and uses synthetic demonstration data.

---

## License

This project is currently intended for portfolio and demonstration purposes.
