from hashlib import sha256

from fastapi import APIRouter, File, HTTPException, UploadFile
from starlette.concurrency import run_in_threadpool

from app.schemas.resume import ResumeAnalyzeResponse, ResumeFileInfo, ResumeSection, ResumeTextPayload
from app.services.pdf_parser import EmptyPdfTextError, PdfParsingError, extract_pdf_text
from app.services.text_cleaner import clean_resume_text, split_resume_sections

router = APIRouter(prefix="/resumes", tags=["resumes"])

MAX_UPLOAD_SIZE_BYTES = 10 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {"application/pdf", "application/x-pdf"}


def _raise_api_error(status_code: int, code: str, message: str) -> None:
    raise HTTPException(status_code=status_code, detail={"code": code, "message": message})


def _is_pdf_upload(upload_file: UploadFile) -> bool:
    filename = (upload_file.filename or "").lower()
    content_type = (upload_file.content_type or "").lower()
    return filename.endswith(".pdf") or content_type in ALLOWED_CONTENT_TYPES


@router.post("/analyze", response_model=ResumeAnalyzeResponse)
async def analyze_resume(file: UploadFile = File(...)) -> ResumeAnalyzeResponse:
    if not _is_pdf_upload(file):
        _raise_api_error(
            400,
            "INVALID_FILE_TYPE",
            "Only PDF files are supported.",
        )

    pdf_bytes = await file.read()
    if not pdf_bytes:
        _raise_api_error(
            400,
            "EMPTY_UPLOAD",
            "The uploaded file is empty.",
        )

    if len(pdf_bytes) > MAX_UPLOAD_SIZE_BYTES:
        _raise_api_error(
            413,
            "FILE_TOO_LARGE",
            "The uploaded PDF exceeds the 10 MB limit.",
        )

    if not pdf_bytes.startswith(b"%PDF"):
        _raise_api_error(
            400,
            "INVALID_FILE_TYPE",
            "Only PDF files are supported.",
        )

    try:
        extraction = await run_in_threadpool(extract_pdf_text, pdf_bytes)
    except EmptyPdfTextError as exc:
        _raise_api_error(422, "EMPTY_PDF_TEXT", str(exc))
    except PdfParsingError as exc:
        _raise_api_error(400, "PDF_PARSE_FAILED", str(exc))

    cleaned_text = clean_resume_text(extraction.raw_text)
    if not cleaned_text.strip():
        _raise_api_error(
            422,
            "EMPTY_PDF_TEXT",
            "No extractable text was found in the PDF.",
        )

    sections = split_resume_sections(cleaned_text)
    resume_sections = [
        ResumeSection(title=section.title, content=section.content)
        for section in sections
    ]

    resume_id = sha256(pdf_bytes).hexdigest()
    filename = file.filename or "resume.pdf"

    return ResumeAnalyzeResponse(
        resume_id=resume_id,
        file=ResumeFileInfo(
            filename=filename,
            content_type=file.content_type,
            page_count=extraction.page_count,
            size_bytes=len(pdf_bytes),
        ),
        text=ResumeTextPayload(
            raw=extraction.raw_text,
            cleaned=cleaned_text,
            sections=resume_sections,
        ),
    )
