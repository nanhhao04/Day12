import os
import time
import signal
import logging
import json
import redis
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, Security, Depends, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from .config import settings
from .auth import verify_api_key
from .rate_limiter import check_rate_limit, r as redis_client
from .cost_guard import check_budget, record_usage
from .core.mock_provider import MockProvider
from .agent.agent import ReActAgent
from .tools.tools import LAPTOP_TOOLS_CONFIG

# Logging — JSON structured
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}',
)
logger = logging.getLogger(__name__)

START_TIME = time.time()
_is_ready = False
_agent: Optional[ReActAgent] = None

# ─────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    global _is_ready, _agent
    logger.info(json.dumps({
        "event": "startup",
        "app": settings.app_name,
        "environment": settings.environment,
    }))
    
    # LLM Initialization (Mock Only as requested)
    try:
        provider = MockProvider(model_name=settings.llm_model)
        _agent = ReActAgent(llm=provider, tools=LAPTOP_TOOLS_CONFIG)
        logger.info(json.dumps({"event": "agent_initialized", "provider": "mock"}))
    except Exception as e:
        logger.error(json.dumps({"event": "agent_init_failed", "error": str(e)}))

    _is_ready = True
    yield
    _is_ready = False
    logger.info(json.dumps({"event": "shutdown"}))

# ─────────────────────────────────────────────────────────
# App Setup
# ─────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)

# ─────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────
class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: str = Field(default="default_session")

class AskResponse(BaseModel):
    question: str
    answer: str
    model: str
    timestamp: str

# ─────────────────────────────────────────────────────────
# Dependencies with user_id propagation
# ─────────────────────────────────────────────────────────
async def rate_limit_dependency(user_id: str = Depends(verify_api_key)):
    check_rate_limit(user_id)
    return user_id

async def budget_dependency(user_id: str = Depends(verify_api_key)):
    check_budget(user_id)
    return user_id

# ─────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────

@app.get("/health", tags=["Operations"])
def health():
    return {"status": "ok", "uptime": round(time.time() - START_TIME, 1)}

@app.get("/ready", tags=["Operations"])
def ready():
    """Readiness probe. Checks Redis connection."""
    if not _is_ready:
        raise HTTPException(503, "App not ready")
    try:
        redis_client.ping()
        return {"ready": True}
    except Exception as e:
        logger.error(f"Readiness check failed: Redis ping error {e}")
        raise HTTPException(503, "Redis connection failed")

@app.post("/ask", response_model=AskResponse, tags=["Agent"])
async def ask_agent(
    body: AskRequest,
    user_id: str = Depends(budget_dependency), # Chains auth -> budget
    _rl: str = Depends(rate_limit_dependency), # Chains auth -> rate limit
):
    if not _agent:
        raise HTTPException(503, "Agent not initialized")

    # 1. Load History from Redis
    history = []
    history_json = redis_client.get(f"chat:{body.session_id}")
    if history_json:
        history = json.loads(history_json)

    # 2. Run Agent
    try:
        agent_result = _agent.run(body.question, history=history)
        answer = agent_result["answer"]
        usage = agent_result["usage"]
    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}")
        raise HTTPException(500, f"Internal Agent Error: {str(e)}")

    # 3. Record Actual Usage (Cost)
    record_usage(user_id, usage["prompt_tokens"], usage["completion_tokens"])

    # 4. Save History (LRU style - last 10)
    history.append({"role": "user", "content": body.question})
    history.append({"role": "assistant", "content": answer})
    redis_client.set(f"chat:{body.session_id}", json.dumps(history[-10:]), ex=3600)

    return AskResponse(
        question=body.question,
        answer=answer,
        model=settings.llm_model,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

# ─────────────────────────────────────────────────────────
# Graceful Shutdown
# ─────────────────────────────────────────────────────────
def _handle_signal(signum, _frame):
    logger.info(json.dumps({"event": "signal_received", "signum": signum}))

signal.signal(signal.SIGTERM, _handle_signal)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=settings.debug)
