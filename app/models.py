from pydantic import BaseModel, Field
from typing import List


class ResearchRequest(BaseModel):
    query: str = Field(..., description="The research question or topic to investigate")


class AnalystInsights(BaseModel):
    key_trends: List[str] = Field(description="Major trends identified in the research")
    risks: List[str] = Field(description="Key risks or challenges identified")
    insights: List[str] = Field(description="Actionable insights and observations")


class FinalReport(BaseModel):
    executive_summary: str = Field(description="A concise executive summary (2-4 sentences)")
    markdown_report: str = Field(description="Full markdown-formatted report covering findings, analysis, and recommendations")
    follow_up_questions: List[str] = Field(description="3-5 follow-up questions for further investigation")
