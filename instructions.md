# Coding Agent Prompt (OpenAI Agents SDK)

Build a **modular Jupyter notebook (Python)** that implements a **research → analysis → report** multi-agent workflow using the **OpenAI Agents SDK**. The notebook must be structured so that the **Researcher agent can be swapped out** later for a different project without changing the rest of the pipeline.

**Requirements**
1. **Notebook format**: Use clear section headings and separate code/markdown cells.
2. **Dependencies**: Include a setup cell installing `openai-agents`, `python-dotenv`, `pydantic`, and `requests`.
3. **Modularity**: Create a dedicated function to build the `Researcher` agent. The pipeline should accept a `research_agent` object so it can be replaced later.
4. **Agents**:
   - `Researcher` (uses a web search tool).
   - `Analyst` (summarizes trends/risks/insights).
   - `Writer` (returns structured output: executive summary, markdown report, follow-up questions).
5. **Tooling**: Implement a real Tavily search `function_tool`. The Tavily API key is in the environment (`TAVILY_API_KEY`). Use endpoint `https://api.tavily.com/search` with JSON payload: `api_key`, `query`, `max_results`.
6. **Pipeline**: A manager function `run_pipeline(user_query, researcher_agent)` that orchestrates: Researcher → summary, Analyst → insights, Writer → final report.
7. **Output formatting**: Display the executive summary, markdown report, and follow-up questions cleanly.
8. **Example run**: Include a sample query and show the output.

**Notes**
- Use the correct import path: `from agents import Agent, Runner, function_tool` (do **not** use `openai_agents`).
- Keep the Researcher creation isolated so it can be swapped for a different domain-specific researcher.
- Use Pydantic output models for structured outputs.
- Ensure the Researcher's instructions explicitly say to use the Tavily search tool to gather sources before summarizing.

Deliver only the notebook code and markdown cells, ready to run.
```

Save it (Cmd+S).

**Step 6 — Generate the notebook.** Back in the Claude Code terminal, type:
```
Read @instructions.md and generate the complete notebook as research_pipeline_generated.ipynb