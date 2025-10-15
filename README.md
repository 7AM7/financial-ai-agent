# AI-Powered Financial Data System

> Transform heterogeneous financial data into unified insights with AI-powered natural language querying.

---

## 🎯 The Business Problem

**Challenge**: Companies use multiple accounting platforms (QuickBooks, Rootfi, etc.) that generate data in different formats with different structures. Financial teams struggle to:
- Consolidate reports across systems
- Answer ad-hoc questions quickly
- Identify trends without manual spreadsheet work
- Make data-driven decisions in real-time

**Solution**: An AI-powered system that:
- ✅ **Unifies** diverse financial data sources into a single database
- ✅ **Queries** data using natural language (no SQL knowledge needed)
- ✅ **Visualizes** key metrics in an interactive dashboard
- ✅ **Adapts** dashboard layout based on user requests (e.g., "swap revenue and profit boxes")

**Real-World Example**:
- CFO asks: *"What was our Q1 profit compared to Q2?"*
- System: Understands query → Generates SQL → Validate SQL query →Returns answer with context
- User says: *"Switch the total profit and total revenue positions"*
- Dashboard: Instantly swaps component positions

---

## 🚀 Quick Start

**One command to run everything:**

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env with your OpenAI/Azure OpenAI credentials

# 2. Start the system
make start
```

**Access the system:**
- 🌐 **Dashboard**: http://localhost:3000
- 🔧 **API**: http://localhost:8000
- 📚 **API Docs**: http://localhost:8000/docs

**Key Commands:**
```bash
./start.sh       # Start everything (postgres → data pipeline → backend → frontend)
make stop        # Stop all services
make restart     # Restart with fresh data
make logs        # View logs
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Financial Data (QuickBooks + Rootfi JSON)                  │
│  • Different formats, dates, hierarchies                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Data Pipeline (ELT)                   📖 data_pipeline/    │
│  • Extract: Parse both JSON formats                          │
│  • Transform: Normalize & categorize                         │
│  • Load: Star schema in PostgreSQL                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  PostgreSQL Database                                         │
│  • Unified star schema (fact_financials + dimensions)        │
│  • Jan 2020 - Aug 2025 (66 months of data)                  │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Backend API (FastAPI + LangGraph)     📖 backend/          │
│  • REST endpoints for dashboard data                         │
│  • AI Agent: Natural language → SQL → Response              │
│  • Supports OpenAI and Azure OpenAI                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js + CopilotKit)       📖 frontend/         │
│  • Interactive dashboard with charts                         │
│  • AI chatbot for natural language queries                   │
│  • Component swapping: "swap revenue and profit boxes"       │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. Natural Language Queries
Ask questions in plain English:
- *"What was total revenue in Q1 2024?"*
- *"Show me top expense categories"*
- *"Compare Q1 and Q2 performance"*

### 2. Interactive Dashboard
- Real-time financial charts (P&L, Revenue, Expenses)
- Key metrics with growth indicators
- **Component Swapping**: Tell the AI to rearrange dashboard widgets
  - *"Switch the total profit with total revenue"*
  - *"Move the expenses chart to the top"*

### 3. Intelligent AI Agent
- LangGraph workflow with error recovery
- Automatically fixes and retries failed queries
- Streaming responses (see agent thinking in real-time)

### 4. Unified Data Model
- Handles QuickBooks (column-based, 1.1MB)
- Handles Rootfi (period-based, 485KB)
- Star schema optimized for fast analytics (<100ms queries)

---

## ⚙️ Configuration

### 1. Create Environment File
```bash
cp .env.example .env
```

### 2. Add LLM Credentials

**Option A: Azure OpenAI** (Recommended)
```env
MODEL=gpt-4o-mini
MODEL_PROVIDER=azure_openai
API_KEY=your_azure_api_key
AZURE_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT=gpt-4o-mini
OPENAI_API_VERSION=2025-03-01-preview
```

**Option B: OpenAI**
```env
MODEL=gpt-4o-mini
MODEL_PROVIDER=openai
API_KEY=sk-your_openai_api_key
```

---

## 🔧 Component Documentation

Each component has its own detailed README:

| Component | Purpose | Documentation |
|-----------|---------|---------------|
| **Data Pipeline** | ELT pipeline: extracts, transforms, loads financial data | [📖 data_pipeline/README.md](data_pipeline/README.md) |
| **Backend API** | FastAPI + LangGraph SQL agent | [📖 backend/README.md](backend/README.md) |
| **Frontend** | Next.js dashboard + AI chatbot | [📖 frontend/README.md](frontend/README.md) |

**Technical Reports:**
- [Data Structure Analysis](data_pipeline/docs/DATA_REPORT.md) - Deep dive into JSON formats
- [Pipeline Architecture](data_pipeline/docs/TECHNICAL_REPORT.md) - ELT design decisions
- [Backend Agent Design](backend/docs/BACKEND_REPORT.md) - LangGraph workflow
- [Frontend Integration](frontend/docs/FRONTEND_REPORT.md) - CopilotKit setup

---

## ⚡ Critical: Startup Order

**The system has 3 components that MUST start in this order:**

```
1. PostgreSQL          (Docker container)
2. Data Pipeline       (Separate Python project - NOT in Docker)
3. Backend + Frontend  (Docker containers)
```

**Why this matters:**
- ❌ Backend will CRASH if database has no data
- ⚠️ Data pipeline is a SEPARATE Python project in `./data_pipeline/`
- ✅ Use `make start` - it handles everything automatically

**Manual startup (if needed):**
```bash
# 1. Start database
docker compose up -d postgres

# 2. Run data pipeline (SEPARATE project!)
cd data_pipeline
source venv/bin/activate  # or create venv if first time
python main.py init && python main.py run
cd ..

# 3. Start backend and frontend
docker compose up -d backend frontend
```

---

## 🐛 Troubleshooting

### "fetch failed" in Chatbot?
**Cause**: Wrong URLs in frontend configuration

**Fix**:
```bash
# Check frontend/.env.local has correct URLs:
cat frontend/.env.local

# Should contain:
# REMOTE_ACTION_URL=http://backend:8000/copilotkit  (server-side)
# NEXT_PUBLIC_API_URL=http://localhost:8000          (client-side)

# Restart frontend
docker compose restart frontend
```

### Backend Not Connecting to Database?
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Verify data was loaded
docker exec -it financial-postgres \
  psql -U postgres -d financial_data -c "SELECT COUNT(*) FROM fact_financials;"
# Should return a count > 0

# If no data, re-run pipeline
cd data_pipeline && python main.py run && cd ..
```

### Port Already in Use?
```bash
# Check what's using ports
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL

# Stop conflicting services or change ports in docker-compose.yml
```

---

## 📊 Example Usage

### Dashboard Interactions

**Ask questions:**
- *"What was total profit in Q1 2024?"*
- *"Show me revenue trends over time"*
- *"Which expense category had the highest increase?"*

**Rearrange components:**
- *"Swap the revenue and profit boxes"*
- *"Switch the total profit with total revenue"*
- *"Move the chart to the top"*

### REST API

```bash
# Get dashboard overview
curl http://localhost:8000/api/dashboard/overview

# Ask natural language question
curl -X POST http://localhost:8000/api/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What was total revenue in Q1 2024?"}'
```

---

## 🛠️ Technology Stack

| Layer | Technologies |
|-------|-------------|
| **Data Pipeline** | Python, SQLAlchemy, PostgreSQL, Pydantic |
| **Backend** | FastAPI, LangGraph, LangChain, CopilotKit |
| **LLM** | OpenAI GPT-4o-mini or Azure OpenAI |
| **Database** | PostgreSQL 16 (Star Schema) |
| **Frontend** | Next.js 15, React 19, TypeScript, CopilotKit |
| **Infrastructure** | Docker, Docker Compose |

---

## 📁 Project Structure

```
financial-ai-agent/
├── README.md              # ← You are here
├── start.sh               # 🚀 One-command startup
├── Makefile               # Convenient commands
├── docker-compose.yml     # Docker orchestration
├── .env.example           # Configuration template
│
├── data_pipeline/         # 📖 ELT Pipeline
│   ├── README.md          # Pipeline documentation
│   ├── data/              # Source JSON files
│   ├── src/               # Python ETL code
│   └── docs/              # Technical reports
│
├── backend/               # 📖 FastAPI + LangGraph
│   ├── README.md          # Backend documentation
│   ├── src/               # API and agent code
│   ├── tests/             # Unit + integration tests
│   └── docs/              # Architecture report
│
└── frontend/              # 📖 Next.js + CopilotKit
    ├── README.md          # Frontend documentation
    ├── app/               # Next.js routes
    ├── components/        # React components
    └── docs/              # Integration report
```

---

## 🎯 What This Demonstrates

✅ **AI Integration** - Natural language querying with LangGraph agents
✅ **Data Engineering** - ELT pipeline with star schema design
✅ **Backend Architecture** - FastAPI + LangGraph + CopilotKit streaming
✅ **Frontend Development** - Next.js with AI chatbot + component swapping
✅ **Production Readiness** - Docker, tests, monitoring, documentation

### Requirements Met
- ✅ Integrated heterogeneous financial data (QuickBooks + Rootfi)
- ✅ Natural language querying with AI agent
- ✅ RESTful API with OpenAPI documentation
- ✅ Interactive dashboard with AI capabilities
- ✅ Clean architecture with comprehensive docs
- ✅ Docker containerization
- ✅ Test coverage (unit + integration)

---

## 📞 Support

**Issues?** Check troubleshooting section above or component READMEs:
- [Data Pipeline README](data_pipeline/README.md)
- [Backend README](backend/README.md)
- [Frontend README](frontend/README.md)

---

**Built by AM7** | AI-Powered Financial Data System
