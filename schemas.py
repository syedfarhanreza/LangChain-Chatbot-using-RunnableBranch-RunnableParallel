from typing import List, Literal
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    """Primary structured response returned by every branch (Programming / Math / General)."""

    answer: str = Field(description="The direct, complete answer to the user's question.")
    category: Literal["Programming", "Mathematics", "General"] = Field(
        description="The category the query was routed to by RunnableBranch."
    )
    confidence: float = Field(
        ge=0.0, le=1.0,
        description="Model's confidence in the answer, between 0.0 and 1.0."
    )
    keywords: List[str] = Field(
        default_factory=list,
        description="3-5 keywords/tags relevant to the answer."
    )


class SummaryResponse(BaseModel):
    """Secondary structured response used inside RunnableParallel."""

    summary: str = Field(description="A concise 1-2 sentence summary of the answer.")
    difficulty_level: Literal["Beginner", "Intermediate", "Advanced"] = Field(
        description="Estimated difficulty level of the topic discussed."
    )
    follow_up_questions: List[str] = Field(
        default_factory=list,
        description="2-3 relevant follow-up questions the user might ask next."
    )


class FinalChatOutput(BaseModel):
    """
    The final combined structured object produced after RunnableParallel merges
    the ChatResponse and SummaryResponse branches. This is what gets rendered
    in the Streamlit UI.
    """

    answer: str
    category: str
    confidence: float
    keywords: List[str]
    summary: str
    difficulty_level: str
    follow_up_questions: List[str]