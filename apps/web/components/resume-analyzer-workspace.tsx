"use client"

import { type ChangeEvent, useState } from "react"
import { AlertCircleIcon } from "lucide-react"

import {
  analyzeResume,
  matchResume,
  type ResumeAnalyzeResponse,
  type ResumeMatchResponse,
} from "@/lib/api"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"

import { JobDescriptionCard } from "@/components/resume-analyzer/job-description-card"
import { ResumeMatchCard } from "@/components/resume-analyzer/match-card"
import { ResumeProfileCard } from "@/components/resume-analyzer/profile-card"
import { ResumeTextCard } from "@/components/resume-analyzer/text-card"
import { ResumeUploadCard } from "@/components/resume-analyzer/upload-card"
import { WorkspaceHeader } from "@/components/resume-analyzer/workspace-header"

export function ResumeAnalyzerWorkspace() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<ResumeAnalyzeResponse | null>(null)
  const [matchResult, setMatchResult] = useState<ResumeMatchResponse | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [error, setError] = useState("")
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [isMatching, setIsMatching] = useState(false)

  async function handleAnalyze() {
    if (!selectedFile) {
      setError("请选择 PDF 简历")
      return
    }

    setError("")
    setIsAnalyzing(true)
    setMatchResult(null)

    try {
      const result = await analyzeResume(selectedFile)
      setAnalysis(result)
    } catch (caughtError) {
      setAnalysis(null)
      setError(caughtError instanceof Error ? caughtError.message : "简历解析失败")
    } finally {
      setIsAnalyzing(false)
    }
  }

  async function handleMatch() {
    if (!analysis) {
      setError("请先完成简历解析")
      return
    }

    if (!jobDescription.trim()) {
      setError("请输入岗位需求")
      return
    }

    setError("")
    setIsMatching(true)

    try {
      const result = await matchResume({
        resumeText: analysis.text.cleaned,
        resumeProfile: analysis.profile,
        jobDescription,
      })
      setMatchResult(result)
    } catch (caughtError) {
      setMatchResult(null)
      setError(caughtError instanceof Error ? caughtError.message : "岗位匹配失败")
    } finally {
      setIsMatching(false)
    }
  }

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0] ?? null
    setSelectedFile(file)
    setAnalysis(null)
    setMatchResult(null)
    setError("")
  }

  return (
    <main className="min-h-dvh bg-muted/30">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-5 md:px-6">
        <WorkspaceHeader />

        {error ? (
          <Alert variant="destructive">
            <AlertCircleIcon />
            <AlertTitle>请求失败</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        <div className="grid gap-5 lg:grid-cols-[minmax(320px,420px)_1fr]">
          <div className="flex flex-col gap-5">
            <ResumeUploadCard
              selectedFile={selectedFile}
              pageCount={analysis?.file.page_count}
              isAnalyzing={isAnalyzing}
              onFileChange={handleFileChange}
              onAnalyze={handleAnalyze}
            />

            <JobDescriptionCard
              jobDescription={jobDescription}
              hasAnalysis={Boolean(analysis)}
              isMatching={isMatching}
              onChange={setJobDescription}
              onMatch={handleMatch}
            />
          </div>

          <div className="grid gap-5 xl:grid-cols-2">
            <ResumeProfileCard analysis={analysis} isAnalyzing={isAnalyzing} />
            <ResumeMatchCard matchResult={matchResult} isMatching={isMatching} />
            <ResumeTextCard analysis={analysis} isAnalyzing={isAnalyzing} />
          </div>
        </div>
      </div>
    </main>
  )
}
