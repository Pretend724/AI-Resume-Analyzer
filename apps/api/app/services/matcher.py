from dataclasses import dataclass
import re

from app.schemas.match import (
    ExperienceAnalysis,
    KeywordAnalysis,
    MatchScoringMetadata,
    MatchLevel,
    ResumeMatchRequest,
    ResumeMatchResponse,
    ScoreBreakdown,
)
from app.schemas.profile import ResumeProfile
from app.services.llm_client import (
    LLMClientError,
    call_chat_completion,
    extract_json_payload,
    load_llm_config,
)


KEYWORD_ALIASES = {
    "Python": ("python",),
    "FastAPI": ("fastapi",),
    "Django": ("django",),
    "Flask": ("flask",),
    "RESTful API": ("restful", "rest api", "restful api"),
    "SQL": ("sql",),
    "MySQL": ("mysql",),
    "PostgreSQL": ("postgresql", "postgres"),
    "Redis": ("redis",),
    "Docker": ("docker",),
    "Kubernetes": ("kubernetes", "k8s"),
    "Linux": ("linux",),
    "Git": ("git",),
    "React": ("react",),
    "Next.js": ("next.js", "nextjs"),
    "TypeScript": ("typescript", "ts"),
    "JavaScript": ("javascript", "js"),
    "Tailwind CSS": ("tailwind", "tailwindcss"),
    "Node.js": ("node.js", "nodejs", "node"),
    "Java": ("java",),
    "Spring Boot": ("spring boot", "springboot"),
    "Go": ("golang", " go "),
    "微服务": ("微服务",),
    "Serverless": ("serverless", "函数计算"),
    "阿里云": ("阿里云", "aliyun", "alibaba cloud"),
    "AI": ("ai", "人工智能"),
    "LLM": ("llm", "大模型"),
    "NLP": ("nlp", "自然语言处理"),
    "PDF": ("pdf",),
    "OCR": ("ocr",),
    "后端开发": ("后端开发", "后端工程师", "backend development", "backend developer", "backend engineer"),
    "前端开发": ("前端开发", "前端工程师", "frontend development", "frontend developer", "frontend engineer"),
}

STOPWORDS = {
    "and",
    "or",
    "the",
    "with",
    "for",
    "job",
    "role",
    "team",
    "work",
    "岗位",
    "职责",
    "要求",
    "负责",
    "熟悉",
    "具有",
    "能力",
    "经验",
    "开发",
    "相关",
}
STOPWORD_FRAGMENTS = ("经验", "年限", "年以上", "要求", "职责", "负责", "熟悉", "具有")
MAX_LLM_RESUME_CHARS = 6000
MAX_LLM_JOB_CHARS = 3000


@dataclass(frozen=True, slots=True)
class LLMMatchScore:
    score: int
    summary: str
    rationale: str


async def match_resume_to_job(request: ResumeMatchRequest) -> ResumeMatchResponse:
    rule_based_response = build_rule_based_match_response(request)

    config = load_llm_config()
    if not config.is_configured:
        missing_fields = ", ".join(config.missing_fields)
        return rule_based_response.model_copy(
            update={
                "scoring": MatchScoringMetadata(
                    source="rule_based",
                    warnings=[
                        f"LLM configuration is incomplete; missing {missing_fields}; used rule-based score."
                    ],
                )
            }
        )

    try:
        llm_score = await score_match_with_llm(request, rule_based_response)
    except LLMClientError as exc:
        return rule_based_response.model_copy(
            update={
                "scoring": MatchScoringMetadata(
                    source="llm_fallback",
                    warnings=[str(exc)],
                )
            }
        )
    return rule_based_response.model_copy(
        update={
            "score": llm_score.score,
            "level": score_to_level(llm_score.score),
            "score_breakdown": rule_based_response.score_breakdown.model_copy(
                update={"llm_score": llm_score.score}
            ),
            "summary": llm_score.summary,
            "scoring": MatchScoringMetadata(
                source="llm",
                rationale=llm_score.rationale,
            ),
        }
    )


def build_rule_based_match_response(request: ResumeMatchRequest) -> ResumeMatchResponse:
    resume_corpus = build_resume_corpus(request.resume_text, request.resume_profile)
    required_keywords = extract_job_keywords(request.job_description)
    matched_keywords = [
        keyword
        for keyword in required_keywords
        if has_keyword_match(resume_corpus, keyword)
    ]
    missing_keywords = [
        keyword
        for keyword in required_keywords
        if keyword not in matched_keywords
    ]

    match_rate = len(matched_keywords) / len(required_keywords) if required_keywords else 0
    keyword_score = round(match_rate * 100)

    experience_analysis = analyze_experience(
        request.resume_text,
        request.resume_profile,
        request.job_description,
    )
    experience_score = 100 if experience_analysis.is_relevant else 55
    if experience_analysis.required_years is not None and experience_analysis.candidate_years is None:
        experience_score = 45

    score = round(keyword_score * 0.75 + experience_score * 0.25)
    level = score_to_level(score)

    return ResumeMatchResponse(
        score=score,
        level=level,
        keyword_analysis=KeywordAnalysis(
            required_keywords=required_keywords,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            match_rate=round(match_rate, 2),
        ),
        experience_analysis=experience_analysis,
        score_breakdown=ScoreBreakdown(
            keyword_score=keyword_score,
            experience_score=experience_score,
        ),
        summary=build_match_summary(score, matched_keywords, missing_keywords, experience_analysis),
    )


async def score_match_with_llm(
    request: ResumeMatchRequest,
    rule_based_response: ResumeMatchResponse,
) -> LLMMatchScore:
    llm_content = await call_chat_completion(
        [
            {
                "role": "system",
                "content": (
                    "You are an expert technical recruiter. Score how well a resume "
                    "matches a job description. Return only a JSON object."
                ),
            },
            {
                "role": "user",
                "content": build_llm_match_prompt(request, rule_based_response),
            },
        ]
    )
    return parse_llm_match_score(llm_content)


def build_llm_match_prompt(
    request: ResumeMatchRequest,
    rule_based_response: ResumeMatchResponse,
) -> str:
    return (
        "Evaluate the candidate-job fit more accurately than simple keyword matching.\n"
        "Consider skills, role relevance, seniority, project evidence, missing requirements, "
        "and experience years. Use the rule-based analysis as evidence, but you may adjust "
        "the final score when the resume context supports it.\n"
        "Return only JSON with this schema:\n"
        "{\n"
        '  "score": 0,\n'
        '  "summary": "A short Chinese summary for recruiters.",\n'
        '  "rationale": "A short Chinese explanation of why this score was assigned."\n'
        "}\n\n"
        f"Rule-based analysis:\n{rule_based_response.model_dump_json(exclude_none=True)}\n\n"
        f"Resume profile:\n{request.resume_profile.model_dump_json(exclude_none=True)}\n\n"
        f"Job description:\n{request.job_description[:MAX_LLM_JOB_CHARS]}\n\n"
        f"Resume text:\n{request.resume_text[:MAX_LLM_RESUME_CHARS]}"
    )


def parse_llm_match_score(raw_content: str) -> LLMMatchScore:
    payload = extract_json_payload(raw_content)
    score = _coerce_score(payload.get("score"))
    summary = str(payload.get("summary") or "").strip()
    rationale = str(payload.get("rationale") or "").strip()

    if not summary:
        raise LLMClientError("LLM match scoring response is missing summary.")

    return LLMMatchScore(
        score=score,
        summary=summary,
        rationale=rationale,
    )


def _coerce_score(value: object) -> int:
    if isinstance(value, bool):
        raise LLMClientError("LLM match scoring response has invalid score.")

    if isinstance(value, (int, float)):
        numeric_score = round(value)
    elif isinstance(value, str) and re.fullmatch(r"\d+(?:\.\d+)?", value.strip()):
        numeric_score = round(float(value))
    else:
        raise LLMClientError("LLM match scoring response has invalid score.")

    return max(0, min(100, numeric_score))


def build_resume_corpus(resume_text: str, profile: ResumeProfile) -> str:
    profile_parts = [
        profile.job_intention.desired_position,
        profile.background.years_of_experience,
        " ".join(project.description for project in profile.background.projects),
        " ".join(
            f"{education.school} {education.degree} {education.major}"
            for education in profile.background.education
        ),
    ]
    return normalize_text(" ".join([resume_text, *profile_parts]))


def extract_job_keywords(job_description: str) -> list[str]:
    normalized_job = normalize_text(job_description)
    keywords: list[str] = []

    for keyword, aliases in KEYWORD_ALIASES.items():
        if any(has_alias_match(normalized_job, alias) for alias in aliases):
            keywords.append(keyword)

    term_keywords = extract_significant_terms(job_description)
    for keyword in term_keywords:
        if keyword not in keywords and not is_redundant_keyword(keyword, keywords):
            keywords.append(keyword)

    return keywords[:20]


def has_keyword_match(resume_corpus: str, keyword: str) -> bool:
    aliases = KEYWORD_ALIASES.get(keyword, (keyword,))
    return any(has_alias_match(resume_corpus, alias) for alias in aliases)


def analyze_experience(
    resume_text: str,
    profile: ResumeProfile,
    job_description: str,
) -> ExperienceAnalysis:
    required_years = extract_required_years(job_description)
    candidate_years = extract_candidate_years(resume_text, profile)

    if required_years is None:
        return ExperienceAnalysis(
            is_relevant=True,
            required_years=None,
            candidate_years=candidate_years,
            summary="岗位描述未明确工作年限要求，按经验相关处理。",
        )

    if candidate_years is None:
        return ExperienceAnalysis(
            is_relevant=False,
            required_years=required_years,
            candidate_years=None,
            summary=f"岗位要求约 {format_years(required_years)} 年经验，简历未明确体现工作年限。",
        )

    is_relevant = candidate_years >= required_years
    if is_relevant:
        summary = (
            f"岗位要求约 {format_years(required_years)} 年经验，"
            f"候选人体现约 {format_years(candidate_years)} 年经验。"
        )
    else:
        summary = (
            f"岗位要求约 {format_years(required_years)} 年经验，"
            f"候选人体现约 {format_years(candidate_years)} 年经验，年限略有差距。"
        )

    return ExperienceAnalysis(
        is_relevant=is_relevant,
        required_years=required_years,
        candidate_years=candidate_years,
        summary=summary,
    )


def score_to_level(score: int) -> MatchLevel:
    if score >= 90:
        return "excellent"
    if score >= 75:
        return "good"
    if score >= 60:
        return "fair"
    return "weak"


def build_match_summary(
    score: int,
    matched_keywords: list[str],
    missing_keywords: list[str],
    experience_analysis: ExperienceAnalysis,
) -> str:
    if score >= 75:
        fit_summary = "候选人与岗位要求整体匹配度较高。"
    elif score >= 60:
        fit_summary = "候选人与岗位要求存在一定匹配，但仍有明显补充空间。"
    else:
        fit_summary = "候选人与岗位要求匹配度较弱，需要进一步人工确认。"

    matched_text = "、".join(matched_keywords[:5]) if matched_keywords else "暂无明显命中关键词"
    missing_text = "、".join(missing_keywords[:5]) if missing_keywords else "暂无明显缺失关键词"

    return (
        f"{fit_summary} 命中关键词：{matched_text}。"
        f" 缺失关键词：{missing_text}。{experience_analysis.summary}"
    )


def extract_required_years(job_description: str) -> float | None:
    patterns = (
        r"(\d+(?:\.\d+)?)\s*(?:年|年以上|年以上经验|年经验|years?)",
        r"(?:至少|不少于|minimum|min\.?)\s*(\d+(?:\.\d+)?)\s*(?:年|years?)",
    )
    return extract_first_year_value(job_description, patterns)


def extract_candidate_years(resume_text: str, profile: ResumeProfile) -> float | None:
    profile_years = extract_first_number(profile.background.years_of_experience)
    if profile_years is not None:
        return profile_years

    patterns = (
        r"(\d+(?:\.\d+)?)\s*(?:年|年工作经验|年经验|years?)",
        r"(?:工作经验|经验)\s*(\d+(?:\.\d+)?)\s*(?:年|years?)",
    )
    return extract_first_year_value(resume_text, patterns)


def extract_first_year_value(text: str, patterns: tuple[str, ...]) -> float | None:
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))
    return None


def extract_first_number(text: str) -> float | None:
    match = re.search(r"\d+(?:\.\d+)?", text)
    return float(match.group(0)) if match else None


def extract_significant_terms(text: str) -> list[str]:
    terms = re.findall(r"[A-Za-z][A-Za-z0-9.+#-]{2,}|[\u4e00-\u9fff]{2,8}", text)
    keywords: list[str] = []
    for term in terms:
        normalized_term = term.strip()
        if not normalized_term:
            continue
        if any(fragment in normalized_term for fragment in STOPWORD_FRAGMENTS):
            continue
        if normalized_term.lower() in STOPWORDS or normalized_term in STOPWORDS:
            continue
        if normalized_term not in keywords:
            keywords.append(normalized_term)
    return keywords[:10]


def is_redundant_keyword(keyword: str, existing_keywords: list[str]) -> bool:
    normalized_keyword = keyword.lower()
    if len(normalized_keyword) <= 3:
        return True

    return any(
        normalized_keyword in existing_keyword.lower()
        or existing_keyword.lower() in normalized_keyword
        for existing_keyword in existing_keywords
    )


def has_alias_match(text: str, alias: str) -> bool:
    normalized_alias = alias.strip().lower()
    if not normalized_alias:
        return False

    if re.fullmatch(r"[a-z0-9+#.]{1,3}", normalized_alias):
        return re.search(rf"(?<![a-z0-9+#.]){re.escape(normalized_alias)}(?![a-z0-9+#.])", text) is not None

    return normalized_alias in text


def normalize_text(text: str) -> str:
    lowered_text = text.lower()
    return re.sub(r"\s+", " ", lowered_text)


def format_years(value: float) -> str:
    if value.is_integer():
        return str(int(value))
    return str(value)
