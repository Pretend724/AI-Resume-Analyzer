from typing import Literal

from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""


class JobIntention(BaseModel):
    desired_position: str = ""
    expected_salary: str = ""


class EducationEntry(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    start_year: str = ""
    end_year: str = ""


class ProjectEntry(BaseModel):
    name: str = ""
    description: str = ""


class BackgroundInfo(BaseModel):
    years_of_experience: str = ""
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)


class ResumeProfile(BaseModel):
    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    job_intention: JobIntention = Field(default_factory=JobIntention)
    background: BackgroundInfo = Field(default_factory=BackgroundInfo)


class ProfileExtractionMetadata(BaseModel):
    source: Literal["heuristic", "llm", "llm_fallback"] = "heuristic"
    warnings: list[str] = Field(default_factory=list)
