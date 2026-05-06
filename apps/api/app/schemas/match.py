from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.profile import ResumeProfile


MatchLevel = Literal["excellent", "good", "fair", "weak"]


class ResumeMatchRequest(BaseModel):
    resume_text: str = Field(min_length=1)
    resume_profile: ResumeProfile = Field(default_factory=ResumeProfile)
    job_description: str = Field(min_length=1)


class KeywordAnalysis(BaseModel):
    required_keywords: list[str]
    matched_keywords: list[str]
    missing_keywords: list[str]
    match_rate: float = Field(ge=0, le=1)


class ExperienceAnalysis(BaseModel):
    is_relevant: bool
    required_years: float | None = None
    candidate_years: float | None = None
    summary: str


class ScoreBreakdown(BaseModel):
    keyword_score: int = Field(ge=0, le=100)
    experience_score: int = Field(ge=0, le=100)
    llm_score: int | None = Field(default=None, ge=0, le=100)


class MatchScoringMetadata(BaseModel):
    source: Literal["rule_based", "llm", "llm_fallback"] = "rule_based"
    warnings: list[str] = Field(default_factory=list)
    rationale: str = ""


class ResumeMatchResponse(BaseModel):
    score: int = Field(ge=0, le=100)
    level: MatchLevel
    keyword_analysis: KeywordAnalysis
    experience_analysis: ExperienceAnalysis
    score_breakdown: ScoreBreakdown
    summary: str
    scoring: MatchScoringMetadata = Field(default_factory=MatchScoringMetadata)
