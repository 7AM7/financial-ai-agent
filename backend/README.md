# Financial Data Backend

FastAPI backend with AI-powered SQL agent for natural language financial queries.

---

## 🚀 Quick Start

```bash
# 1. Setup Python environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your database credentials and Azure OpenAI API key

# 3. Start server
uvicorn src.main:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Test the API**:
```bash
curl http://localhost:8000/health
# {"status": "healthy"}
```

---

## 📊 What This Does

Provides REST API and AI-powered natural language interface for financial data analysis.

**Core Features**:
- **Dashboard API** - RESTful endpoints for charts and metrics (no AI overhead)
- **SQL Agent** - Natural language to SQL conversion using LangGraph
- **CopilotKit Integration** - Real-time streaming chat interface
- **Schema-Aware** - Optimized for star schema with aggregate views

**AI Workflow**: NL Query → LangGraph Agent → SQL Generation → Validation → Execution → Natural Language Response

---

## 🏗️ Architecture

### Layered Agent Design

```
Frontend (CopilotKit)
       ↓
FastAPI /copilotkit Endpoint
       ↓
Financial Assistant (Main Agent)
  ├─► Respond directly (greetings, help)
  └─► Query data → SQL Agent
              ↓
        LangGraph Workflow:
        1. write_query (generate SQL)
        2. check_query (validate)
        3. exec_query (execute)
        4. repair_query (fix errors)
              ↓
        PostgreSQL
```

**Why This Design?**
- **Efficiency**: Simple questions don't need database queries
- **Reliability**: Dashboard works even if LLM is down
- **Separation**: SQL logic isolated and testable
- **Context**: Maintains conversation history

---

## 💻 API Endpoints

### Health Check
```bash
GET /health
```

### Dashboard Data (Direct Queries)
```bash
GET /api/dashboard/profit-loss?year=2024
GET /api/dashboard/top-accounts?account_type=expense&limit=10
GET /api/dashboard/trend-analysis?year=2024
GET /api/dashboard/category-performance
GET /api/dashboard/overview
```

### AI Chat
```bash
POST /api/chat/query
{
  "question": "What was total revenue in Q1 2024?"
}
```

### CopilotKit (Frontend Integration)
```bash
POST /copilotkit
```

**Interactive Docs**: http://localhost:8000/docs

---

## 🤖 SQL Agent

### How It Works

1. **Schema Discovery** - Agent lists available tables/views
2. **Query Generation** - Converts natural language to SQL
3. **Validation** - Checks query for errors before execution
4. **Execution** - Runs validated query on PostgreSQL
5. **Error Recovery** - Repairs and retries failed queries
6. **Response** - Returns results in natural language

**Example Questions**:
- "What was total profit in Q1 2024?"
- "Show me top 5 expense categories"
- "What is year-over-year revenue growth?"
- "Which accounts had the biggest increase?"

**Agent Nodes**:
- `write_query` - Generate SQL from natural language
- `check_query` - Validate SQL syntax and logic
- `exec_query` - Execute on PostgreSQL
- `repair_query` - Fix errors and retry

---

## 📁 Project Structure

```
backend/
├── src/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings & environment variables
│   ├── db.py                # Database connection
│   ├── llm/
│   │   └── provider_manager.py  # LLM provider management (OpenAI/Azure)
│   ├── agent/
│   │   ├── graph.py         # LangGraph agent definition
│   │   ├── state.py         # Agent state management
│   │   ├── tools.py         # Agent tools
│   │   ├── sql_utils.py     # SQL utilities
│   │   ├── nodes/
│   │   │   ├── sql.py       # SQL generation & execution nodes
│   │   │   ├── chat.py      # Chat interaction nodes
│   │   │   ├── schema.py    # Schema discovery nodes
│   │   │   └── helpers.py   # Helper functions
│   │   └── prompts/
│   │       ├── loader.py
│   │       ├── context.yaml
│   │       └── templates/   # Prompt templates
│   ├── routes/
│   │   ├── dashboard.py     # Dashboard API endpoints
│   │   └── agent.py         # Agent endpoints
│   ├── services/
│   │   └── analytics_service.py
│   └── models/
│       └── analytics.py
├── tests/
│   ├── conftest.py          # Shared test fixtures
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | Quick start & usage (this file) |
| **[BACKEND_REPORT.md](docs/BACKEND_REPORT.md)** | ⭐ Architecture, agent design, API details |

---

## 🎯 Key Features

✅ **Natural Language Queries** - Ask questions in plain English
✅ **Schema-Aware Agent** - Understands star schema and aggregate views
✅ **Query Validation** - Double-checks SQL before execution
✅ **Error Recovery** - Automatically fixes and retries failed queries
✅ **Streaming Responses** - Real-time updates via CopilotKit
✅ **Dashboard API** - Fast direct queries without AI overhead

---

## 🔧 Configuration

Create `.env` file:

```bash
# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=financial_data
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# LLM Provider - Choose "openai" or "azure_openai"
MODEL=gpt-4o-mini
MODEL_PROVIDER=azure_openai
API_KEY=your_api_key

# Azure OpenAI (required when MODEL_PROVIDER=azure_openai)
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT=gpt-4o-mini
OPENAI_API_VERSION=2025-03-01-preview

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000
```

### LLM Provider Configuration

The backend supports **two LLM providers**:

#### Option 1: Azure OpenAI (Default)
```bash
MODEL_PROVIDER=azure_openai
MODEL=gpt-4o-mini
API_KEY=your_azure_api_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT=gpt-4o-mini
OPENAI_API_VERSION=2025-03-01-preview
```

**Required Fields**:
- `API_KEY` - Your Azure OpenAI API key
- `AZURE_ENDPOINT` - Your Azure OpenAI resource endpoint
- `AZURE_DEPLOYMENT` - Your deployment name
- `OPENAI_API_VERSION` - API version (default: 2025-03-01-preview)

#### Option 2: OpenAI (Direct API)
```bash
MODEL_PROVIDER=openai
MODEL=gpt-4o-mini
API_KEY=sk-your_openai_api_key
```

**Required Fields**:
- `API_KEY` - Your OpenAI API key (starts with `sk-`)
- `MODEL` - Model name (e.g., gpt-4o-mini, gpt-4, gpt-3.5-turbo)

**Switching Providers**: Simply change `MODEL_PROVIDER` in your `.env` file and restart the server.

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| **Conversational Query** | 1-2 seconds |
| **Simple Data Query** | 3-5 seconds |
| **Complex Data Query** | 5-10 seconds |
| **Dashboard API** | < 1 second |

**Optimization**:
- Pre-calculated views (v_profit_loss, etc.)
- Connection pooling (size=10, max_overflow=20)
- Schema caching
- Streaming responses

---

## 🐛 Troubleshooting

**Database Connection Issues?**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify credentials in .env
cat .env | grep POSTGRES
```

**SQL Agent Errors?**
```bash
# Check logs for details
uvicorn src.main:app --reload --log-level debug

# Verify Azure OpenAI credentials
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "hello"}'
```

**CORS Errors?**
```bash
# Add frontend URL to .env
echo "CORS_ORIGINS=http://localhost:3000" >> .env

# Restart server
```

---

## 🛠️ Technology Stack

- **Python 3.9+**
- **FastAPI** (REST API framework)
- **LangGraph** (Agent workflow)
- **LangChain** (LLM integration)
- **CopilotKit** (Frontend integration)
- **PostgreSQL** (Database)
- **SQLAlchemy** (ORM)
- **LLM Providers** (OpenAI or Azure OpenAI)

---

## 🧪 Development

**Run with auto-reload**:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Test the agent**:
```bash
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What was total revenue in 2024?"}'
```

**View API docs**:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## 🧪 Testing

### Setup Testing Environment

```bash
# Install test dependencies
pip install -e ".[test]"

# Or with specific packages
pip install pytest pytest-asyncio pytest-cov httpx faker pytest-mock
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html

# Run only unit tests (fast)
pytest tests/unit/ -m unit

# Run only integration tests
pytest tests/integration/ -m integration

# Run specific test file
pytest tests/unit/test_analytics_service.py

# Run in verbose mode
pytest -v

# Run tests in parallel (faster)
pytest -n auto
```

### Test Categories

**Unit Tests** (`tests/unit/`):
- Fast, isolated tests
- Mock database responses
- Test business logic without external dependencies
- Example: `test_analytics_service.py`

**Integration Tests** (`tests/integration/`):
- Test full API stack
- Require running PostgreSQL database
- Test actual HTTP endpoints
- Example: `test_api_dashboard.py`

### Coverage Goals

- **Minimum**: 70% code coverage
- **Target**: 85% code coverage
- **Critical paths**: 100% (API routes, analytics service)

**View coverage report**:
```bash
pytest --cov=src --cov-report=html
open htmlcov/index.html
```

### Test Markers

Tests are categorized with pytest markers:

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only API tests
pytest -m api

# Run only agent tests
pytest -m agent

# Skip slow tests
pytest -m "not slow"
```

### Writing Tests

**Example Unit Test**:
```python
@pytest.mark.unit
def test_get_profit_loss(mocker):
    mock_db = mocker.MagicMock()
    result = get_profit_loss(mock_db, year=2024)
    assert len(result) > 0
```

**Example Integration Test**:
```python
@pytest.mark.integration
@pytest.mark.api
def test_dashboard_endpoint(test_client):
    response = test_client.get("/api/dashboard/profit-loss")
    assert response.status_code == 200
```

### CI/CD Integration

**GitHub Actions** (example):
```yaml
- name: Run tests
  run: |
    pytest --cov=src --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
```

---