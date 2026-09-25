# VikriMitra — E-Commerce Sales Analytics Chatbot

VikriMitra is an AI-powered e-commerce sales analytics chatbot that converts plain-English business questions into database-backed analytics, interactive charts, and concise business insights.

Demo Video Link :(https://drive.google.com/file/d/1K86ovHqtWEAPXuol_ufOUSZIqUod7657/view?usp=sharing)

## Features

- Natural-language e-commerce sales analytics
- Groq-powered LLM agent with native tool calling
- Rule-based fallback mode
- MCP-based analytics tool layer
- PostgreSQL-backed analytics
- Brazilian E-Commerce Public Dataset by Olist
- Revenue, orders, products, sellers, reviews, payments, and delivery analytics
- Automatic chart selection based on analytical intent
- Line, bar, donut, stacked bar, and scatter visualizations
- Persistent dashboard with pinned charts
- Refresh pinned queries against current database data
- Significant-change detection for refreshed dashboard results
- Structured JSON error handling
- Docker Compose deployment

## Architecture

```text
React + Vite Frontend
        |
        v
FastAPI API
        |
        v
AI Agent
(Groq LLM / Rule-based Fallback)
        |
        v
MCP Analytics Server
        |
        v
PostgreSQL
        ^
        |
   Olist CSV Dataset
```

## Technology Stack

- Python 3.11
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL 16
- MCP Python SDK
- Groq API
- React
- Vite
- Chart.js
- react-chartjs-2
- Docker
- Docker Compose

## MCP Analytics Tools

The MCP server exposes six analytics tools:

1. **Order Trends**
   - Analyze order counts and trends over time.

2. **Product / Category Performance**
   - Analyze revenue, order counts, and category performance.
   - Supports ranking and category filtering.

3. **Seller Performance**
   - Analyze seller-level sales performance.

4. **Customer Review Analysis**
   - Analyze review scores by category, product, or state.

5. **Payment Breakdown**
   - Analyze payment methods and payment-value distribution.

6. **Delivery Performance**
   - Analyze delivery time and delivery-related performance.

All MCP tools return structured JSON results and structured errors instead of propagating raw exceptions.

## Agent Modes

The application supports two agent modes through `AGENT_MODE`.

### LLM Mode

Uses Groq native tool calling to select the appropriate MCP analytics tool and provide structured arguments.

```env
AGENT_MODE=llm
GROQ_MODEL=openai/gpt-oss-20b
LLM_TIMEOUT_SECONDS=15
```

### Fallback Mode

Uses deterministic rule-based query handling when LLM mode is unavailable or disabled.

```env
AGENT_MODE=fallback
```

## Configuration

Create a `.env` file in the project root.

```env
POSTGRES_DB=vikrimithra
POSTGRES_USER=vikrimithra
POSTGRES_PASSWORD=vikrimithra_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-20b
AGENT_MODE=llm
LLM_TIMEOUT_SECONDS=15
MCP_URL=http://mcp:8001/mcp
```

A safe configuration template is provided in `.env.example`.

**Do not commit `.env` or expose the Groq API key.**

## How to Run

### Prerequisites

- Docker Desktop
- Git
- A valid Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/HimaLonare/VikriMitra.git
cd VikriMitra
```

### 2. Create the environment file

Create `.env` in the project root using `.env.example` as the template.

Add your own Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key
```

### 3. Start the application

Run:

```bash
docker compose up --build
```

Docker Compose starts:

- PostgreSQL
- Database initialization
- Dataset loading
- MCP analytics server
- FastAPI backend
- React frontend

### 4. Open the application

After the containers are running, open:

```text
http://localhost:5173
```

## Application Services

| Service | URL | Purpose |
|---|---|---|
| Frontend | http://localhost:5173 | React analytics chatbot and dashboard |
| FastAPI | http://localhost:8000 | Application API |
| MCP Server | http://localhost:8001/mcp | Analytics tool server |
| PostgreSQL | localhost:5432 | Analytics database |

## Database Initialization

The project uses PostgreSQL as the main analytics database.

At startup, the database bootstrap process:

1. Initializes the schema.
2. Checks whether the database is already populated.
3. Loads the Olist CSV datasets only when the database is empty.
4. Skips the expensive CSV reload when the database already contains data.

This makes repeated `docker compose up` runs much faster while still supporting a fresh database.

## Dataset

This project uses the **Brazilian E-Commerce Public Dataset by Olist**.

The dataset contains approximately 100,000 orders and includes information about:

- Customers
- Sellers
- Products
- Product category translations
- Orders
- Order items
- Payments
- Reviews
- Geolocation

The application loads the datasets into PostgreSQL so analytics queries run against the database rather than directly against CSV files.

## Example Queries

### Query 1 — Top product categories

```text
What were the top 5 product categories by revenue?
```

Expected behavior:

- Calls `product_performance`
- Uses revenue as the ranking metric
- Limits the result to 5 categories
- Sorts descending
- Produces a horizontal bar chart
- Returns a concise business insight

### Query 2 — Monthly order trend

```text
Show monthly orders in 2017.
```

Expected behavior:

- Calls `order_trends`
- Interprets 2017 as the requested year
- Produces a line chart
- Shows monthly order volume

### Query 3 — Lowest-rated categories

```text
Which product categories have the lowest average review scores?
```

Expected behavior:

- Calls `review_analysis`
- Groups data by category
- Sorts average review score ascending
- Produces a ranked comparison visualization

### Query 4 — State delivery and review analysis

```text
Compare average delivery time and review score across Brazilian states.
```

Expected behavior:

- Combines delivery and review analytics
- Groups results by state
- Compares delivery performance and customer review score
- Produces an appropriate comparison visualization

### Query 5 — Relationship analysis

```text
Show the relationship between items sold and revenue across the top 10 product categories.
```

Expected behavior:

- Retrieves category-level product performance
- Selects the top 10 categories by revenue
- Produces a scatter chart
- Uses items sold on the x-axis
- Uses revenue on the y-axis

## Chart Selection Logic

The application automatically selects an appropriate visualization based on the analytical intent.

| Analytical Intent | Chart |
|---|---|
| Single metric over time | Line chart |
| Two metrics over the same time | Dual-axis line chart |
| Ranked top-N results | Horizontal bar chart |
| Category comparison | Vertical bar chart |
| Part-to-whole analysis | Donut chart |
| Relationship between two numerical variables | Scatter chart |
| Score distribution | Stacked horizontal bar chart |
| Ambiguous chart intent | Appropriate alternative chart options |

Each response includes the selected chart type and a one-line justification.

## Natural-Language Parameter Interpretation

The agent supports common natural-language expressions such as:

- `last year` → previous calendar year
- `first half of 2017` → January through June 2017
- `São Paulo` → `SP`
- `top 10` → limit 10 with descending ranking
- `worst rated` → ascending average review score
- `electronics` → corresponding English product category
- Unspecified date range → full available dataset with an explicit assumption

## Dashboard

Charts generated by the chatbot can be pinned to a persistent dashboard.

The dashboard supports:

- Pinning analytical results
- Persistent chart storage
- Refreshing the original query
- Re-running the query against current database data
- Significant-change detection
- Persistence across browser sessions and application restarts

Dashboard state is stored in PostgreSQL.

## API

### Query endpoint

```http
POST /api/query
Content-Type: application/json
```

Example request:

```json
{
  "query": "What were the top 5 product categories by revenue?"
}
```

Example response structure:

```json
{
  "agent": "llm",
  "tool": "product_performance",
  "arguments": {
    "limit": 5,
    "sort_by": "revenue"
  },
  "chart": {
    "chart_type": "horizontal_bar"
  },
  "insight": "..."
}
```

The full response also contains the underlying structured analytics result.

## Error Handling

The application uses structured error handling across the API, agent, and MCP layers.

Examples include:

- Invalid parameters
- Unsupported analytical requests
- Database errors
- MCP communication errors
- LLM timeout errors
- LLM availability failures

Errors are returned in structured form rather than exposing raw exceptions to the end user.

## Project Structure

```text
VikriMitra/
│
├── backend/
│   ├── agent/
│   │   └── groq_agent.py
│   │
│   ├── analytics/
│   │   ├── order_trends.py
│   │   ├── product_performance.py
│   │   ├── seller_performance.py
│   │   ├── review_analysis.py
│   │   ├── payment_breakdown.py
│   │   └── delivery_performance.py
│   │
│   ├── app/
│   │   ├── chart_builder.py
│   │   ├── database.py
│   │   └── main.py
│   │
│   ├── database/
│   │   ├── bootstrap_db.py
│   │   ├── init_db.py
│   │   ├── load_data.py
│   │   └── schema.sql
│   │
│   ├── mcp_server/
│   │   └── server.py
│   │
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── Dashboard.jsx
│   │   └── main.jsx
│   │
│   ├── Dockerfile
│   ├── package.json
│   └── vite.config.js
│
├── data/
│   └── Olist CSV datasets
│
├── tests/
│
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Design Decisions

### PostgreSQL instead of direct CSV analysis

The application runs analytics against PostgreSQL rather than directly against CSV files. This provides structured relational querying and supports the joins required by the Olist dataset.

### MCP for the analytics layer

Analytics capabilities are exposed as explicit MCP tools. This provides a structured interface between the agent and the analytics functions and makes the system easier to test and extend.

### Native LLM tool calling

The Groq agent uses native tool calling so the model can select an analytics capability and provide structured arguments instead of generating unrestricted SQL.

### Rule-based fallback

LLM failures should not make the application completely unusable. The fallback agent provides deterministic handling for supported query patterns.

### Automatic chart selection

The chart builder maps analytical intent and returned data to an appropriate visualization rather than forcing one chart type for every question.

### Docker Compose

Docker Compose provides a reproducible multi-container environment so the evaluator can start the complete application using a single command.

## Security

- Secrets are stored in `.env`
- `.env` is excluded through `.gitignore`
- `.env.example` contains placeholder values only
- API keys must never be committed to source control

## Docker Workflow

The complete application is intended to be evaluated locally using Docker Compose.

Run:

```bash
docker compose up --build
```

Then open:

```text
http://localhost:5173
```

No manual PostgreSQL configuration or manual CSV import is required after the environment variables have been configured.

## Submission Workflow

An evaluator can:

1. Clone the GitHub repository.
2. Create `.env` from `.env.example`.
3. Add a valid Groq API key.
4. Run:

```bash
docker compose up --build
```

5. Open:

```text
http://localhost:5173
```

The evaluator can then test natural-language analytics queries, MCP tool usage, chart generation, insights, dashboard persistence, and refresh behavior.

## Repository

GitHub repository:

https://github.com/HimaLonare/VikriMitra
