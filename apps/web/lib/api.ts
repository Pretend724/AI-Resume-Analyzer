const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8001"

export type ResumeSection = {
  title: string
  content: string
}

export type ResumeProfile = {
  basic_info: {
    name: string
    phone: string
    email: string
    address: string
  }
  job_intention: {
    desired_position: string
    expected_salary: string
  }
  background: {
    years_of_experience: string
    education: Array<{
      school: string
      degree: string
      major: string
      start_year: string
      end_year: string
    }>
    projects: Array<{
      name: string
      description: string
    }>
  }
}

export type ResumeAnalyzeResponse = {
  resume_id: string
  file: {
    filename: string
    content_type: string | null
    page_count: number
    size_bytes: number
  }
  text: {
    raw: string
    cleaned: string
    sections: ResumeSection[]
  }
  profile: ResumeProfile
  profile_extraction: {
    source: "heuristic" | "llm" | "llm_fallback"
    warnings: string[]
  }
}

export type ResumeMatchResponse = {
  score: number
  level: "excellent" | "good" | "fair" | "weak"
  keyword_analysis: {
    required_keywords: string[]
    matched_keywords: string[]
    missing_keywords: string[]
    match_rate: number
  }
  experience_analysis: {
    is_relevant: boolean
    required_years: number | null
    candidate_years: number | null
    summary: string
  }
  score_breakdown: {
    keyword_score: number
    experience_score: number
  }
  summary: string
}

type ApiErrorPayload = {
  error?: {
    code?: string
    message?: string
    details?: unknown
  }
  detail?: {
    code?: string
    message?: string
  }
}

export function getApiBaseUrl() {
  return API_BASE_URL
}

function getErrorMessage(payload: ApiErrorPayload, fallback: string) {
  return (
    payload.error?.message ??
    payload.detail?.message ??
    payload.error?.code ??
    payload.detail?.code ??
    fallback
  )
}

async function readJson<T>(response: Response, fallbackError: string) {
  const payload = (await response.json().catch(() => ({}))) as ApiErrorPayload

  if (!response.ok) {
    throw new Error(getErrorMessage(payload, fallbackError))
  }

  return payload as T
}

export async function analyzeResume(file: File) {
  const formData = new FormData()
  formData.append("file", file)

  const response = await fetch(`${API_BASE_URL}/resumes/analyze`, {
    method: "POST",
    body: formData,
  })

  return readJson<ResumeAnalyzeResponse>(response, "简历解析失败")
}

export async function matchResume(input: {
  resumeText: string
  resumeProfile: ResumeProfile
  jobDescription: string
}) {
  const response = await fetch(`${API_BASE_URL}/resumes/match`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      resume_text: input.resumeText,
      resume_profile: input.resumeProfile,
      job_description: input.jobDescription,
    }),
  })

  return readJson<ResumeMatchResponse>(response, "岗位匹配失败")
}
