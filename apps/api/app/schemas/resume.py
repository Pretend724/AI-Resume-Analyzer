from pydantic import BaseModel, Field


class ResumeSection(BaseModel):
    title: str = Field(min_length=1)
    content: str = Field(min_length=1)


class ResumeFileInfo(BaseModel):
    filename: str = Field(min_length=1)
    content_type: str | None = None
    page_count: int = Field(ge=1)
    size_bytes: int = Field(ge=1)


class ResumeTextPayload(BaseModel):
    raw: str
    cleaned: str
    sections: list[ResumeSection]


class ResumeAnalyzeResponse(BaseModel):
    resume_id: str = Field(min_length=1)
    file: ResumeFileInfo
    text: ResumeTextPayload
