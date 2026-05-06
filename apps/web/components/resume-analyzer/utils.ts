import type { ResumeAnalyzeResponse, ResumeMatchResponse } from "@/lib/api"

export const levelText: Record<ResumeMatchResponse["level"], string> = {
  excellent: "高度匹配",
  good: "较匹配",
  fair: "可评估",
  weak: "弱匹配",
}

export const extractionSourceText: Record<
  ResumeAnalyzeResponse["profile_extraction"]["source"],
  string
> = {
  heuristic: "本地识别",
  llm: "AI 提取",
  llm_fallback: "AI 兜底",
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
