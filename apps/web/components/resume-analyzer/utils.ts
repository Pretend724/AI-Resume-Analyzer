import type { ResumeAnalyzeResponse, ResumeMatchResponse } from "@/lib/api"

export const levelText: Record<ResumeMatchResponse["level"], string> = {
  excellent: "高度匹配",
  good: "较匹配",
  fair: "可评估",
  weak: "弱匹配",
}

export const scoringSourceText: Record<
  ResumeMatchResponse["scoring"]["source"],
  string
> = {
  rule_based: "规则评分",
  llm: "AI 评分",
  llm_fallback: "AI 兜底",
}

export const extractionSourceText: Record<
  ResumeAnalyzeResponse["profile_extraction"]["source"],
  string
> = {
  heuristic: "本地识别",
  llm: "AI 提取",
  llm_fallback: "AI 兜底",
}

export const levelTone: Record<
  ResumeMatchResponse["level"],
  {
    badgeClassName: string
    panelClassName: string
    scoreClassName: string
  }
> = {
  excellent: {
    badgeClassName: "border-emerald-200 bg-emerald-50 text-emerald-700",
    panelClassName: "border-emerald-200 bg-emerald-50/70",
    scoreClassName: "text-emerald-700",
  },
  good: {
    badgeClassName: "border-sky-200 bg-sky-50 text-sky-700",
    panelClassName: "border-sky-200 bg-sky-50/70",
    scoreClassName: "text-sky-700",
  },
  fair: {
    badgeClassName: "border-amber-200 bg-amber-50 text-amber-700",
    panelClassName: "border-amber-200 bg-amber-50/70",
    scoreClassName: "text-amber-700",
  },
  weak: {
    badgeClassName: "border-destructive/30 bg-destructive/10 text-destructive",
    panelClassName: "border-destructive/30 bg-destructive/10",
    scoreClassName: "text-destructive",
  },
}

export function formatFileSize(bytes: number) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`
  }

  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

export function valueOrEmpty(value: string) {
  return value.trim() || "无"
}
