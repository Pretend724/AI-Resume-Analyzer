from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class TextSection:
    title: str
    content: str


SECTION_TITLE_MAP = (
    ("个人信息", "基本信息"),
    ("基本信息", "基本信息"),
    ("联系方式", "基本信息"),
    ("personal information", "基本信息"),
    ("basic information", "基本信息"),
    ("contact", "基本信息"),
    ("contact information", "基本信息"),
    ("profile", "基本信息"),
    ("求职意向", "求职意向"),
    ("objective", "求职意向"),
    ("career objective", "求职意向"),
    ("工作经历", "工作经历"),
    ("工作经验", "工作经历"),
    ("实习经历", "工作经历"),
    ("work experience", "工作经历"),
    ("professional experience", "工作经历"),
    ("employment history", "工作经历"),
    ("experience", "工作经历"),
    ("教育经历", "教育背景"),
    ("教育背景", "教育背景"),
    ("education", "教育背景"),
    ("education background", "教育背景"),
    ("项目经历", "项目经历"),
    ("项目经验", "项目经历"),
    ("projects", "项目经历"),
    ("project experience", "项目经历"),
    ("project", "项目经历"),
    ("专业技能", "技能栈"),
    ("技能", "技能栈"),
    ("技术栈", "技能栈"),
    ("skills", "技能栈"),
    ("technical skills", "技能栈"),
    ("professional skills", "技能栈"),
    ("tech stack", "技能栈"),
    ("自我评价", "自我评价"),
    ("summary", "自我评价"),
    ("self evaluation", "自我评价"),
)


def clean_resume_text(raw_text: str) -> str:
    if not raw_text.strip():
        return ""

    normalized_text = raw_text.replace("\r\n", "\n").replace("\r", "\n").replace("\f", "\n")
    normalized_text = normalized_text.replace("\u00a0", " ")

    cleaned_lines: list[str] = []
    last_was_blank = False

    for raw_line in normalized_text.split("\n"):
        line = re.sub(r"[ \t]+", " ", raw_line).strip()
        if not line:
            if cleaned_lines and not last_was_blank:
                cleaned_lines.append("")
            last_was_blank = True
            continue

        cleaned_lines.append(line)
        last_was_blank = False

    cleaned_text = "\n".join(cleaned_lines).strip()
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text


def split_resume_sections(cleaned_text: str) -> list[TextSection]:
    if not cleaned_text.strip():
        return []

    sections: list[TextSection] = []
    current_title = "简历正文"
    current_lines: list[str] = []
    has_heading = False

    for raw_line in cleaned_text.splitlines():
        line = raw_line.strip()
        if not line:
            if current_lines and current_lines[-1] != "":
                current_lines.append("")
            continue

        heading_title, heading_content = _detect_heading(line)
        if heading_title is not None:
            has_heading = True
            if current_lines:
                sections.append(
                    TextSection(
                        title=current_title,
                        content=_join_lines(current_lines),
                    )
                )
            current_title = heading_title
            current_lines = [heading_content] if heading_content else []
            continue

        current_lines.append(line)

    if current_lines:
        sections.append(
            TextSection(
                title=current_title,
                content=_join_lines(current_lines),
            )
        )

    if not has_heading:
        return [TextSection(title="简历正文", content=cleaned_text.strip())]

    return [section for section in sections if section.content.strip()]


def _detect_heading(line: str) -> tuple[str | None, str]:
    heading_candidate = re.split(r"[:：]", line, maxsplit=1)[0].strip()
    if not heading_candidate or len(heading_candidate) > 40:
        return None, ""

    normalized_heading = heading_candidate.lower()
    for keyword, title in SECTION_TITLE_MAP:
        normalized_keyword = keyword.lower()
        if normalized_keyword not in normalized_heading:
            continue
        if normalized_heading != normalized_keyword and normalized_keyword not in normalized_heading:
            continue

        heading_content = ""
        if "：" in line:
            heading_content = line.split("：", maxsplit=1)[1].strip()
        elif ":" in line:
            heading_content = line.split(":", maxsplit=1)[1].strip()

        return title, heading_content

    return None, ""


def _join_lines(lines: list[str]) -> str:
    joined_lines = [line for line in lines if line or line == ""]
    content = "\n".join(joined_lines).strip()
    return re.sub(r"\n{3,}", "\n\n", content)
