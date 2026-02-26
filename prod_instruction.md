# Production Deployment Prompt

Convert the research pipeline notebook into a production-ready FastAPI app with SSE streaming, ready to deploy via Railway from GitHub.

**What to build:**
1. `app/main.py` — FastAPI server with CORS, `GET /health` endpoint, `POST /research` endpoint with SSE streaming
2. `app/pipeline.py` — async generator that yields stage events (Researching... Analyzing... Writing...) and the final report
3. `app/models.py` — `ResearchRequest` (with a `query` field) and `FinalReport` Pydantic models
4. `Procfile` — `web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. `railway.toml` — basic Railway config
6. `requirements.txt` — all dependencies

**Key details:**
- Reuse the same agent architecture: Researcher (with Tavily search tool), Analyst, Writer
- Use `from agents import Agent, Runner, function_tool` (not `openai_agents`)
- Generate a unique session ID per request using uuid
- API keys (OPENAI_API_KEY, TAVILY_API_KEY) loaded from environment variables
- SSE streams real-time status updates to the client
- Use `gpt-4o` as the model
- Use Pydantic output models for structured agent outputs
- Include a simple test script `test_api.py` that sends a request to the local server

Ready to deploy with `git push` to GitHub → Railway auto-deploys.
```

Save with Cmd+S.

**Step 2 — Generate the production app.** In your Claude Code terminal, type:
```
Read @prod_instruction.md and generate the complete production FastAPI app