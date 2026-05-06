from dataclasses import dataclass, field
import re

from pydantic import ValidationError

from app.schemas.profile import (
    BackgroundInfo,
    BasicInfo,
    JobIntention,
    ResumeProfile,
)
from app.services.llm_client import LLMClientError, call_chat_completion, extract_json_payload, load_llm_config


EMAIL_PATTERN = re.compile(
    r"(?<![\w.-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])"
)
NAME_PATTERN = re.compile(r"(?:姓名|name)[:：\s]*([^\n，。,;；]{2,40})", re.IGNORECASE)
ADDRESS_PATTERN = re.compile(
    r"(?:地址|现居住|居住地|所在地|address|location)[:：\s]*([^\n]{2,80})",
    re.IGNORECASE,
)
POSITION_PATTERN = re.compile(
    r"(?:求职意向|应聘岗位|目标岗位|职位意向|desired position|target role|position)[:：\s]*([^\n]{2,80})",
    re.IGNORECASE,
)
SALARY_PATTERN = re.compile(
    r"(?:期望薪资|期望工资|薪资期望|月薪|expected salary|salary)[:：\s]*([^\n]{2,80})",
    re.IGNORECASE,
)
YEARS_PATTERN = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:年|years?)\s*(?:工作经验|经验)?",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class ContactExtraction:
    name: str = ""
    phone: str = ""
    email: str = ""
    address: str = ""


@dataclass(frozen=True, slots=True)
class ResumeProfileExtractionResult:
    profile: ResumeProfile
    source: str = "heuristic"
    warnings: list[str] = field(default_factory=list)


async def extract_resume_profile(cleaned_text: str) -> ResumeProfileExtractionResult:
    contact_info = extract_contact_info(cleaned_text)
    heuristic_profile = build_heuristic_profile(cleaned_text, contact_info)

    config = load_llm_config()
    if not config.is_configured:
        missing_fields = ", ".join(config.missing_fields)
        return ResumeProfileExtractionResult(
            profile=heuristic_profile,
            source="heuristic",
            warnings=[
                f"LLM configuration is incomplete; missing {missing_fields}; used heuristic extraction."
            ],
        )

    try:
        llm_content = await call_chat_completion(
            [
                {
                    "role": "system",
                    "content": "You extract structured resume data. Return only a JSON object.",
                },
                {
                    "role": "user",
                    "content": build_extraction_prompt(cleaned_text, heuristic_profile),
                },
            ],
            config=config,
        )
        llm_profile = parse_llm_profile(llm_content)
    except LLMClientError as exc:
        return ResumeProfileExtractionResult(
            profile=heuristic_profile,
            source="llm_fallback",
            warnings=[str(exc)],
        )
    except ValidationError:
        return ResumeProfileExtractionResult(
            profile=heuristic_profile,
            source="llm_fallback",
            warnings=["LLM response did not match the expected profile schema."],
        )

    return ResumeProfileExtractionResult(
        profile=merge_profiles(heuristic_profile, llm_profile),
        source="llm",
    )


def extract_contact_info(text: str) -> ContactExtraction:
    name = _extract_name(text)
    phone = _extract_phone(text)
    email = _extract_email(text)
    address = _extract_address(text)
    return ContactExtraction(name=name, phone=phone, email=email, address=address)


def build_heuristic_profile(text: str, contact_info: ContactExtraction) -> ResumeProfile:
    desired_position = _extract_first_match(POSITION_PATTERN, text)
    expected_salary = _extract_first_match(SALARY_PATTERN, text)
    years_of_experience = _extract_years_of_experience(text)

    return ResumeProfile(
        basic_info=BasicInfo(
            name=contact_info.name,
            phone=contact_info.phone,
            email=contact_info.email,
            address=contact_info.address,
        ),
        job_intention=JobIntention(
            desired_position=desired_position,
            expected_salary=expected_salary,
        ),
        background=BackgroundInfo(
            years_of_experience=years_of_experience,
            education=[],
            projects=[],
        ),
    )


def build_extraction_prompt(text: str, fallback_profile: ResumeProfile) -> str:
    return (
        "Extract the following resume fields from the text below and return only JSON.\n"
        "Use empty strings for missing scalar values and empty arrays for missing lists.\n"
        "Schema:\n"
        "{\n"
        '  "basic_info": {"name": "", "phone": "", "email": "", "address": ""},\n'
        '  "job_intention": {"desired_position": "", "expected_salary": ""},\n'
        '  "background": {\n'
        '    "years_of_experience": "",\n'
        '    "education": [{"school": "", "degree": "", "major": "", "start_year": "", "end_year": ""}],\n'
        '    "projects": [{"name": "", "description": ""}]\n'
        "  }\n"
        "}\n\n"
        f"Fallback hints: {fallback_profile.model_dump_json(exclude_none=True)}\n\n"
        f"Resume text:\n{text}"
    )


def parse_llm_profile(raw_content: str) -> ResumeProfile:
    payload = extract_json_payload(raw_content)
    normalized_payload = {
        "basic_info": payload.get("basic_info") or {},
        "job_intention": payload.get("job_intention") or {},
        "background": payload.get("background") or {},
    }
    return ResumeProfile.model_validate(normalized_payload)


def merge_profiles(base_profile: ResumeProfile, llm_profile: ResumeProfile) -> ResumeProfile:
    return ResumeProfile(
        basic_info=BasicInfo(
            name=llm_profile.basic_info.name or base_profile.basic_info.name,
            phone=base_profile.basic_info.phone or llm_profile.basic_info.phone,
            email=base_profile.basic_info.email or llm_profile.basic_info.email,
            address=llm_profile.basic_info.address or base_profile.basic_info.address,
        ),
        job_intention=JobIntention(
            desired_position=llm_profile.job_intention.desired_position
            or base_profile.job_intention.desired_position,
            expected_salary=llm_profile.job_intention.expected_salary
            or base_profile.job_intention.expected_salary,
        ),
        background=BackgroundInfo(
            years_of_experience=llm_profile.background.years_of_experience
            or base_profile.background.years_of_experience,
            education=llm_profile.background.education or base_profile.background.education,
            projects=llm_profile.background.projects or base_profile.background.projects,
        ),
    )


def _extract_phone(text: str) -> str:
    mobile_match = re.search(r"(?<!\d)(?:\+?86[-\s]?)?(1[3-9]\d{9})(?!\d)", text)
    if mobile_match:
        return mobile_match.group(1)

    landline_match = re.search(r"(?<!\d)(0\d{2,3}[-\s]?\d{7,8})(?!\d)", text)
    if landline_match:
        return landline_match.group(1).replace(" ", "")

    return ""


def _extract_email(text: str) -> str:
    match = EMAIL_PATTERN.search(text)
    return match.group(0) if match else ""


def _extract_name(text: str) -> str:
    labeled_match = NAME_PATTERN.search(text)
    if labeled_match:
        return labeled_match.group(1).strip(" ,，。:：")

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:5]:
        if any(marker in line for marker in ("@", "电话", "邮箱", "手机", "地址")):
            continue
        compact_line = re.sub(r"\s+", "", line)
        if 2 <= len(compact_line) <= 8 and not re.search(r"\d", compact_line):
            return compact_line

    return ""


def _extract_address(text: str) -> str:
    match = ADDRESS_PATTERN.search(text)
    if match:
        return match.group(1).strip(" ,，。;；")

    return ""


def _extract_first_match(pattern: re.Pattern[str], text: str) -> str:
    match = pattern.search(text)
    return match.group(1).strip(" ,，。;；") if match else ""


def _extract_years_of_experience(text: str) -> str:
    match = YEARS_PATTERN.search(text)
    if match:
        return f"{match.group(1)}年"
    return ""
