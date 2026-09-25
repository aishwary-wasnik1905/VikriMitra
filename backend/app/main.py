import os
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agent.fallback_agent import FallbackAgent
from backend.agent.groq_agent import GroqAgent
from backend.app.analytics_pipeline import build_response
from backend.app.dashboard import (
    pin_chart,
    get_dashboard_charts,
    refresh_chart,
)


app = FastAPI(
    title="VikriMithra API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    query: str


class PinChartRequest(BaseModel):
    query: str
    chart_type: str
    chart_config: dict[str, Any]
    insight: str | None = None
    data_snapshot: dict[str, Any] | None = None


def get_agent():
    mode = os.getenv("AGENT_MODE", "fallback").lower()

    if mode == "llm":
        try:
            return GroqAgent()
        except Exception:
            return FallbackAgent()

    return FallbackAgent()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "vikrimithra-api",
    }


@app.post("/api/query")
def query_analytics(request: QueryRequest):
    agent = get_agent()

    try:
        agent_result = agent.process_query(request.query)
        return build_response(agent_result)

    except Exception as exc:
        return {
            "error": {
                "code": "API_QUERY_ERROR",
                "message": str(exc),
            }
        }


@app.post("/api/dashboard/pin")
def pin_dashboard_chart(request: PinChartRequest):
    return pin_chart(
        query=request.query,
        chart_type=request.chart_type,
        chart_config=request.chart_config,
        insight=request.insight,
        data_snapshot=request.data_snapshot,
    )


@app.get("/api/dashboard")
def get_dashboard():
    return get_dashboard_charts()


@app.post("/api/dashboard/{chart_id}/refresh")
def refresh_dashboard_chart(chart_id: int):
    return refresh_chart(chart_id)