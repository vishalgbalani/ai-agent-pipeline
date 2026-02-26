import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .models import ResearchRequest
from .pipeline import run_pipeline_stream

load_dotenv()


# ---------------------------------------------------------------------------
# Startup validation
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    missing = [k for k in ("OPENAI_API_KEY", "TAVILY_API_KEY") if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    yield


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Research Pipeline API",
    description="Multi-agent research → analysis → report pipeline with SSE streaming.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    """Liveness check for Railway / load balancer."""
    return {"status": "ok"}


@app.post("/research")
async def research(request: ResearchRequest):
    """
    Stream a research pipeline run as Server-Sent Events.

    Each event is a JSON object on a `data:` line. Event types:
      - session   — {"type": "session",  "session_id": str}
      - status    — {"type": "status",   "stage": str, "message": str}
      - report    — {"type": "report",   "data": FinalReport}
      - error     — {"type": "error",    "message": str}
      - done      — {"type": "done"}
    """
    if not request.query.strip():
        raise HTTPException(status_code=422, detail="query must not be empty")

    return StreamingResponse(
        run_pipeline_stream(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",  # disable Nginx buffering on Railway
        },
    )
