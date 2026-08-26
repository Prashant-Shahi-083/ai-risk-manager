from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

RiskLevel = Literal["Low", "Medium", "High", "Critical"]


class RiskCategory(BaseModel):
    score: int = Field(ge=0, le=100)
    rationale: str = Field(min_length=1, max_length=800)
    signals: list[str] = Field(default_factory=list, max_length=8)


class Mitigation(BaseModel):
    priority: Literal["Immediate", "High", "Medium", "Low"]
    action: str = Field(min_length=1, max_length=500)
    owner: str = Field(default="Builder", max_length=100)


class RiskAssessment(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    summary: str = Field(min_length=1, max_length=1200)
    categories: dict[str, RiskCategory]
    mitigations: list[Mitigation] = Field(default_factory=list, max_length=12)
    assumptions: list[str] = Field(default_factory=list, max_length=10)
    engine: Literal["deterministic-demo", "llm"]


class AnalysisCreate(BaseModel):
    input_text: str = Field(min_length=10, max_length=10000)
    user_id: str | None = Field(default=None, min_length=1, max_length=120)

    @field_validator("input_text")
    @classmethod
    def normalize_input(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 10:
            raise ValueError("Input must contain at least 10 non-whitespace characters")
        return cleaned


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    input_text: str
    created_at: datetime
    assessment: RiskAssessment


class HistoryItem(BaseModel):
    id: int
    input_preview: str
    overall_score: int
    risk_level: RiskLevel
    created_at: datetime


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mode: str
    version: str
