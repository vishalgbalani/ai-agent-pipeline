"""
Simple smoke-test for the local FastAPI server.

Usage:
    # Start the server first:
    uvicorn app.main:app --reload

    # Then in a separate terminal:
    python test_api.py
"""

import json
import sys

import requests

BASE_URL = "http://localhost:8000"
QUERY = "What are the latest developments and key trends in AI agents and agentic frameworks in 2025?"


def test_health():
    print("── Health check ──────────────────────────────────")
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    resp.raise_for_status()
    print(f"Status: {resp.status_code}  Body: {resp.json()}\n")


def test_research_stream():
    print("── Research pipeline (SSE) ───────────────────────")
    print(f"Query: {QUERY}\n")

    with requests.post(
        f"{BASE_URL}/research",
        json={"query": QUERY},
        stream=True,
        timeout=300,
    ) as resp:
        resp.raise_for_status()

        for raw_line in resp.iter_lines():
            if not raw_line:
                continue

            line = raw_line.decode("utf-8") if isinstance(raw_line, bytes) else raw_line
            if not line.startswith("data: "):
                continue

            event = json.loads(line[len("data: "):])
            event_type = event.get("type")

            if event_type == "session":
                print(f"[SESSION] id={event['session_id']}")

            elif event_type == "status":
                print(f"[STATUS]  stage={event['stage']}  →  {event['message']}")

            elif event_type == "report":
                data = event["data"]
                print("\n══ EXECUTIVE SUMMARY ═════════════════════════════")
                print(data["executive_summary"])

                print("\n══ FULL REPORT ═══════════════════════════════════")
                print(data["markdown_report"])

                print("\n══ FOLLOW-UP QUESTIONS ═══════════════════════════")
                for i, q in enumerate(data["follow_up_questions"], 1):
                    print(f"  {i}. {q}")

            elif event_type == "error":
                print(f"[ERROR]   {event['message']}", file=sys.stderr)

            elif event_type == "done":
                print("\n[DONE]")


if __name__ == "__main__":
    test_health()
    test_research_stream()
