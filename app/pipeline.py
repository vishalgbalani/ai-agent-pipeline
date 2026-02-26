import json
import os
import uuid
from typing import AsyncGenerator

import requests
from agents import Agent, Runner, function_tool

from .models import AnalystInsights, FinalReport, ResearchRequest


# ---------------------------------------------------------------------------
# Tavily search tool
# ---------------------------------------------------------------------------

@function_tool
def tavily_search(query: str, max_results: int = 5) -> str:
    """
    Search the web using Tavily to retrieve relevant, up-to-date information.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return (default 5).

    Returns:
        A formatted string containing search results with titles, URLs, and content snippets.
    """
    api_key = os.getenv("TAVILY_API_KEY")
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
    }
    response = requests.post("https://api.tavily.com/search", json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])
    if not results:
        return "No results found."

    formatted = []
    for i, r in enumerate(results, 1):
        title = r.get("title", "No title")
        url = r.get("url", "")
        content = r.get("content", "")
        formatted.append(f"[{i}] **{title}**\nURL: {url}\n{content}\n")

    return "\n".join(formatted)


# ---------------------------------------------------------------------------
# Researcher factory — swap this function to change the research domain
# ---------------------------------------------------------------------------

def build_researcher_agent() -> Agent:
    """
    Factory function that creates and returns the Researcher agent.
    Replace this function to swap the Researcher for a different domain.
    """
    return Agent(
        name="Researcher",
        instructions=(
            "You are an expert research assistant. When given a topic or question, "
            "you MUST use the tavily_search tool to gather information from the web before summarizing. "
            "Perform multiple targeted searches if needed to get comprehensive coverage. "
            "Synthesize the search results into a well-organized research summary that includes: "
            "key facts, recent developments, relevant statistics, and cited sources (URLs). "
            "Be thorough and objective."
        ),
        tools=[tavily_search],
        model="gpt-4o",
    )


# ---------------------------------------------------------------------------
# Analyst agent
# ---------------------------------------------------------------------------

analyst_agent = Agent(
    name="Analyst",
    instructions=(
        "You are a senior analyst. You will receive a research summary and must extract: "
        "(1) Key trends shaping the topic, "
        "(2) Significant risks or challenges, "
        "(3) Actionable insights and strategic observations. "
        "Be specific, evidence-based, and concise. Return your output as structured JSON."
    ),
    output_type=AnalystInsights,
    model="gpt-4o",
)


# ---------------------------------------------------------------------------
# Writer agent
# ---------------------------------------------------------------------------

writer_agent = Agent(
    name="Writer",
    instructions=(
        "You are a professional technical writer. You will receive a research summary and analyst insights. "
        "Produce a polished deliverable consisting of: "
        "(1) A concise executive summary (2-4 sentences suitable for a busy executive), "
        "(2) A full markdown-formatted report with sections: Overview, Key Findings, Trends & Risks, "
        "Recommendations, and Sources, "
        "(3) 3-5 thoughtful follow-up questions for further investigation. "
        "Return your output as structured JSON."
    ),
    output_type=FinalReport,
    model="gpt-4o",
)


# ---------------------------------------------------------------------------
# Pipeline — async generator streaming SSE events
# ---------------------------------------------------------------------------

def _sse(payload: dict) -> str:
    """Format a dict as a single SSE data line."""
    return f"data: {json.dumps(payload)}\n\n"


async def run_pipeline_stream(request: ResearchRequest) -> AsyncGenerator[str, None]:
    """
    Async generator that orchestrates Researcher → Analyst → Writer and
    yields SSE-formatted events for each stage.

    Event shapes:
        {"type": "session",  "session_id": str}
        {"type": "status",   "stage": str, "message": str}
        {"type": "report",   "data": FinalReport.model_dump()}
        {"type": "error",    "message": str}
        {"type": "done"}
    """
    session_id = str(uuid.uuid4())
    yield _sse({"type": "session", "session_id": session_id})

    try:
        # ── Stage 1: Research ──────────────────────────────────────────────
        yield _sse({
            "type": "status",
            "stage": "researching",
            "message": "Researcher is gathering sources from the web...",
        })

        researcher = build_researcher_agent()
        research_result = await Runner.run(researcher, request.query)
        research_summary = research_result.final_output

        yield _sse({
            "type": "status",
            "stage": "research_done",
            "message": "Research complete. Analyst is extracting insights...",
        })

        # ── Stage 2: Analyze ───────────────────────────────────────────────
        analyst_input = (
            f"Research Summary:\n{research_summary}\n\n"
            f"Original Query: {request.query}"
        )
        analyst_result = await Runner.run(analyst_agent, analyst_input)
        insights: AnalystInsights = analyst_result.final_output

        yield _sse({
            "type": "status",
            "stage": "analysis_done",
            "message": "Analysis complete. Writer is composing the final report...",
        })

        # ── Stage 3: Write ─────────────────────────────────────────────────
        writer_input = (
            f"Original Query: {request.query}\n\n"
            f"Research Summary:\n{research_summary}\n\n"
            f"Analyst Insights:\n"
            f"  Key Trends: {insights.key_trends}\n"
            f"  Risks: {insights.risks}\n"
            f"  Insights: {insights.insights}"
        )
        writer_result = await Runner.run(writer_agent, writer_input)
        final_report: FinalReport = writer_result.final_output

        yield _sse({"type": "report", "data": final_report.model_dump()})

    except Exception as exc:
        yield _sse({"type": "error", "message": str(exc)})

    finally:
        yield _sse({"type": "done"})
