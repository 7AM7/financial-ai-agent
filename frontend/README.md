# Financial Data Frontend

Next.js dashboard with CopilotKit-powered AI chatbot for natural language financial queries.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
cd frontend
npm install

# 2. Configure environment
cp .env.local.example .env.local
# Edit .env.local with your backend URL

# 3. Start development server
npm run dev
```

**Expected Output**:
```
▲ Next.js 15.1.6
- Local:   http://localhost:3000
✓ Starting...
✓ Ready in 2.5s
```

**Open**: http://localhost:3000

---

## 📊 What This Does

Interactive financial dashboard with AI-powered natural language querying.

**Core Features**:
- **Dashboard** - Interactive charts and metrics (revenue, profit, expenses)
- **AI Chatbot** - Ask questions in natural language via CopilotKit
- **Real-Time Updates** - See agent thinking status while processing
- **Widget Swapping** - Ask AI to rearrange dashboard widgets
- **Generative UI** - Dynamic UI components based on agent actions

**AI Workflow**: User Question → CopilotKit → Backend LangGraph Agent → SQL → Response

---

## 🏗️ Architecture

### Component Structure

```
Next.js Frontend
    ↓
CopilotKit Provider (app/layout.tsx)
    ↓
┌─────────────────────────────────────┐
│  Dashboard + CopilotSidebar         │
│  (app/page.tsx)                     │
│                                     │
│  ┌─────────────┐  ┌──────────────┐│
│  │  Dashboard  │  │ CopilotChat  ││
│  │  - Charts   │  │ - NL Queries ││
│  │  - Metrics  │  │ - Status     ││
│  │  - Actions  │  │ - History    ││
│  └─────────────┘  └──────────────┘│
└─────────────────────────────────────┘
    ↓                    ↓
REST API            CopilotKit API
(/api/dashboard)    (/api/copilotkit)
    ↓                    ↓
FastAPI Backend (localhost:8000)
```

---

## 💻 Key Components

### 1. **Dashboard** (`components/FinancialDashboard.tsx`)
Main financial visualization component

**Features**:
- Key metrics cards (revenue, profit, expenses, margin)
- Profit & Loss area chart
- Top revenue/expense bar charts
- Category performance donut chart
- Revenue trend chart

**CopilotKit Integration**:
- `useCopilotReadable` - Exposes dashboard data to AI
- `useCopilotAction` - Enables widget swapping via AI commands

**Example Action**:
```typescript
useCopilotAction({
  name: "swapDashboardWidgets",
  description: "Swap widget positions",
  parameters: [
    { name: "widget1", enum: ["revenue", "profit", "expenses", "margin"] },
    { name: "widget2", enum: ["revenue", "profit", "expenses", "margin"] }
  ],
  handler: async ({ widget1, widget2 }) => {
    // Swap widget positions in state
  }
});
```

---

### 2. **AI Chatbot** (`app/page.tsx`)
CopilotKit sidebar integration

```typescript
<CopilotSidebar
  instructions={prompt}
  AssistantMessage={CustomAssistantMessage}
  labels={{
    title: "Financial AI Assistant",
    initial: "Ask me about revenue, expenses, profit...",
    placeholder: "Ask about revenue, expenses, or trends...",
  }}
/>
```

**Features**:
- Natural language financial queries
- Real-time status updates
- Conversation history
- Custom styling

---

### 3. **Custom Assistant Message** (`components/AssistantMessage.tsx`)
Custom chat message component with status indicator

**Features**:
- Displays agent status ("Analyzing query...", "Writing SQL...", etc.)
- Fallback to "Thinking..." if status empty
- Smooth transitions with 300ms delay
- Markdown rendering

**State Sync**:
```typescript
const { status } = useFinancialAgent();

// Syncs with backend LangGraph agent state
```

---

### 4. **Agent State Hook** (`lib/hooks/use-financial-agent.tsx`)
React hook for LangGraph agent state synchronization

```typescript
const { state } = useCoAgent<FinancialAgentState>({
  name: "financial_assistant",
  initialState: {
    result_data: [],
    result_columns: [],
    status: "thinking...",
    sql: "",
    // ...
  },
});
```

**Synced Fields** (from backend):
- `status` - Current agent status
- `result_data` - Query results
- `result_columns` - Column names
- `sql` - Generated SQL query

---

## 📁 Project Structure

```
frontend/
├── app/
│   ├── layout.tsx              # Root layout with CopilotKit provider
│   ├── page.tsx                # Home page (Dashboard + Chatbot)
│   ├── globals.css             # Global styles + CopilotKit CSS
│   └── api/
│       └── copilotkit/
│           └── route.ts        # Proxies to backend LangGraph agent
├── components/
│   ├── FinancialDashboard.tsx  # Main dashboard with charts
│   ├── AssistantMessage.tsx    # Custom chat message component
│   ├── Header.tsx              # Page header
│   ├── Footer.tsx              # Page footer
│   ├── generative-ui/
│   │   └── SQLResultsChart.tsx # (unused - for future)
│   ├── hooks/
│   │   └── use-sql-results.tsx # (unused - for future)
│   └── ui/                     # Chart components
│       ├── area-chart.tsx
│       ├── bar-chart.tsx
│       ├── pie-chart.tsx
│       └── card.tsx
├── lib/
│   ├── api.ts                  # Type-safe API client
│   ├── hooks/
│   │   └── use-financial-agent.tsx  # Agent state hook
│   ├── prompt.ts               # AI assistant prompt
│   └── utils.ts                # Utilities
├── package.json
└── README.md                   # This file
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **README.md** | Quick start & usage (this file) |
| **[FRONTEND_REPORT.md](docs/FRONTEND_REPORT.md)** | ⭐ CopilotKit + LangGraph integration details |

---

## 🎯 Key Features

✅ **CopilotKit Integration** - AI-powered chatbot sidebar
✅ **LangGraph State Sync** - Real-time agent status updates
✅ **Generative UI** - Dynamic widget swapping via AI
✅ **Type-Safe API** - Full TypeScript support
✅ **Responsive Design** - Mobile-friendly dashboard
✅ **Custom Styling** - Tailwind CSS + shadcn/ui

---

## 🔧 Configuration

Create `.env.local` file:

```bash
# Backend API URL for CopilotKit (server-side)
REMOTE_ACTION_URL=http://localhost:8000/copilotkit

# Backend API URL for client-side requests
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Note**: `REMOTE_ACTION_URL` is used server-side by the CopilotKit proxy, while `NEXT_PUBLIC_API_URL` is used client-side for REST API calls.

---

## 💬 Example Queries

Try asking the AI assistant:

**Financial Queries**:
- "What was total revenue in Q1 2024?"
- "Show me top 5 expense categories"
- "What is the profit margin trend?"
- "Compare Q1 and Q2 revenue"

**Dashboard Actions**:
- "Swap the revenue and profit boxes"
- "Switch the expenses and margin widgets"

---

## 🐛 Troubleshooting

**Chatbot Not Working?**
```bash
# 1. Check backend is running
curl http://localhost:8000/health

# 2. Verify environment variables
cat .env.local | grep REMOTE_ACTION_URL

# 3. Check browser console for errors
# Open DevTools → Console
```

**Charts Not Loading?**
```bash
# 1. Verify backend API is accessible
curl http://localhost:8000/api/dashboard/overview

# 2. Check NEXT_PUBLIC_API_URL
cat .env.local | grep NEXT_PUBLIC_API_URL

# 3. Ensure database has data
# Run data pipeline: cd ../data_pipeline && python main.py run
```

**TypeScript Errors?**
```bash
npm run type-check
```

---

## 🛠️ Technology Stack

- **Next.js 15** (App Router)
- **React 19**
- **CopilotKit** (AI chatbot framework)
- **TypeScript** (Type safety)
- **Tailwind CSS** (Styling)
- **shadcn/ui** (UI components)
- **Recharts** (Charts)

---

## 🧪 Development

**Run development server**:
```bash
npm run dev
```

**Build for production**:
```bash
npm run build
npm start
```

**Type checking**:
```bash
npm run type-check
```

**Linting**:
```bash
npm run lint
```

