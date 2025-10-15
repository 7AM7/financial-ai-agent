#!/bin/bash
set -e

echo "=========================================="
echo "🚀 Starting AI-Powered Financial System"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Step 1: Start PostgreSQL from ROOT docker-compose
echo -e "${YELLOW}📊 Step 1/4: Starting PostgreSQL...${NC}"
docker compose up -d postgres

echo -e "${YELLOW}⏳ Waiting for PostgreSQL to be ready...${NC}"
for i in {1..30}; do
    if docker compose exec -T postgres pg_isready -U postgres -d financial_data > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PostgreSQL is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ PostgreSQL failed to start after 30 seconds${NC}"
        exit 1
    fi
    sleep 1
done
echo ""

# Step 2: Run DATA PIPELINE (separate Python project)
echo -e "${YELLOW}📥 Step 2/4: Running DATA PIPELINE (separate project)...${NC}"
echo -e "${BLUE}Location: ./data_pipeline/${NC}"
echo "This will:"
echo "  - Initialize database schema"
echo "  - Load QuickBooks data (data_set_1.json)"
echo "  - Load Rootfi data (data_set_2.json)"
echo "  - Create aggregate views for fast queries"
echo ""

# Check if data_pipeline venv exists
if [ ! -d "data_pipeline/venv" ]; then
    echo -e "${YELLOW}📦 Creating Python virtual environment for data pipeline...${NC}"
    cd data_pipeline
    python3 -m venv venv
    source venv/bin/activate
    pip install -q -r requirements.txt
    cd ..
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi

# Run data pipeline
cd data_pipeline
source venv/bin/activate
echo -e "${YELLOW}🔄 Initializing database schema...${NC}"
python main.py init
echo -e "${YELLOW}🔄 Loading financial data...${NC}"
python main.py run
deactivate
cd ..

# Check if data was loaded
echo -e "${YELLOW}🔍 Verifying data was loaded...${NC}"
DATA_COUNT=$(docker compose exec -T postgres psql -U postgres -d financial_data -t -c "SELECT COUNT(*) FROM fact_financials;" 2>/dev/null | tr -d '[:space:]')

if [ "$DATA_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Data loaded successfully! ($DATA_COUNT records)${NC}"
else
    echo -e "${RED}❌ Data pipeline failed - no data in database${NC}"
    exit 1
fi
echo ""

# Step 3: Build and start backend
echo -e "${YELLOW}🔨 Step 3/4: Building and starting backend API...${NC}"
docker compose build backend
docker compose up -d backend

echo -e "${YELLOW}⏳ Waiting for backend to be ready...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is ready!${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Backend failed to start after 60 seconds${NC}"
        echo "Check logs with: docker compose logs backend"
        exit 1
    fi
    sleep 1
done
echo ""

# Step 4: Build and start frontend
echo -e "${YELLOW}🌐 Step 4/4: Building and starting frontend...${NC}"
docker compose build frontend
docker compose up -d frontend

echo -e "${YELLOW}⏳ Waiting for frontend to be ready...${NC}"
for i in {1..60}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend is ready!${NC}"
        break
    fi
    if [ $i -eq 60 ]; then
        echo -e "${RED}❌ Frontend failed to start after 60 seconds${NC}"
        echo "Check logs with: docker compose logs frontend"
        exit 1
    fi
    sleep 1
done

echo ""
echo "=========================================="
echo -e "${GREEN}✅ System is ready!${NC}"
echo "=========================================="
echo ""
echo "📊 Access the application:"
echo "  • Frontend:  http://localhost:3000"
echo "  • Backend:   http://localhost:8000"
echo "  • API Docs:  http://localhost:8000/docs"
echo "  • Database:  localhost:5432"
echo ""
echo "📝 Useful commands:"
echo "  • View logs:     docker compose logs -f"
echo "  • Stop system:   docker compose down"
echo "  • Restart:       ./start.sh"
echo ""
echo "🎉 Start asking questions in the chatbot!"
echo ""
