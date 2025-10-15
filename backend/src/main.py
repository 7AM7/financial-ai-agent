"""
FastAPI backend for Financial Data Dashboard.

Provides:
- Dashboard endpoints for charts and metrics
- Chatbot endpoint with streaming SQL agent
- CopilotKit integration for frontend
"""
import logging
import warnings
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.routes.dashboard import router as dashboard_router
from src.routes.agent import register_copilotkit_endpoint

warnings.filterwarnings("ignore", category=UserWarning, module="pydantic._internal._generate_schema")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logging.getLogger("uvicorn").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("src").setLevel(logging.INFO)


app = FastAPI(
    title="Financial Data API",
    description="API for financial data dashboard and AI-powered queries",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "financial-data-api"}


app.include_router(dashboard_router)
register_copilotkit_endpoint(app)


def main():
    """Run the uvicorn server."""
    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=True,
    )


if __name__ == "__main__":
    main()
