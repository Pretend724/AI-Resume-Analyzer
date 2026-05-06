"use client"

import { type ChangeEvent, useState } from "react"
import {
  AlertCircleIcon,
  CheckCircle2Icon,
  FileTextIcon,
  SearchCheckIcon,
  UploadIcon,
} from "lucide-react"

import {
  analyzeResume,
  matchResume,
  type ResumeAnalyzeResponse,
  type ResumeMatchResponse,
} from "@/lib/api"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"

import { JobDescriptionCard } from "@/components/resume-analyzer/job-description-card"
import { LLMConfigCard } from "@/components/resume-analyzer/llm-config-card"
import { ResumeMatchCard } from "@/components/resume-analyzer/match-card"
import { ResumeProfileCard } from "@/components/resume-analyzer/profile-card"
import { ResultJsonCard } from "@/components/resume-analyzer/result-json-card"
import { ResumeTextCard } from "@/components/resume-analyzer/text-card"
import { ResumeUploadCard } from "@/components/resume-analyzer/upload-card"
import { WorkspaceHeader } from "@/components/resume-analyzer/workspace-header"

type WorkflowStep = "upload" | "analysis" | "match"

const workflowSteps: Array<{
  value: WorkflowStep
  title: string
  description: string
  icon: typeof UploadIcon
}> = [
  {
    value: "upload",
    title: "上传简历",
    description: "选择 PDF 并解析",
    icon: UploadIcon,
  },
  {
    value: "analysis",
    title: "查看解析",
    description: "核对文本和信息",
    icon: FileTextIcon,
  },
  {
    value: "match",
    title: "岗位评分",
    description: "输入 JD 生成评分",
    icon: SearchCheckIcon,
  },
]

export function ResumeAnalyzerWorkspace() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [analysis, setAnalysis] = useState<ResumeAnalyzeResponse | null>(null)
  const [matchResult, setMatchResult] = useState<ResumeMatchResponse | null>(null)
  const [jobDescription, setJobDescription] = useState("")
  const [currentStep, setCurrentStep] = useState<WorkflowStep>("upload")
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
      setCurrentStep("analysis")
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
      setCurrentStep("match")
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
    setCurrentStep("upload")
    setError("")
  }

  return (
    <main className="min-h-dvh bg-muted/30">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-5 px-4 py-5 md:px-6">
        <WorkspaceHeader />
        <WorkflowProgress
          currentStep={currentStep}
          hasAnalysis={Boolean(analysis)}
          hasMatchResult={Boolean(matchResult)}
          onStepChange={setCurrentStep}
        />

        {error ? (
          <Alert variant="destructive">
            <AlertCircleIcon />
            <AlertTitle>请求失败</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        {currentStep === "upload" ? (
          <section className="mx-auto grid w-full max-w-2xl gap-5">
            <LLMConfigCard onError={setError} />

            <ResumeUploadCard
              selectedFile={selectedFile}
              pageCount={analysis?.file.page_count}
              isAnalyzing={isAnalyzing}
              onFileChange={handleFileChange}
              onAnalyze={handleAnalyze}
            />

            {analysis ? (
              <Alert>
                <CheckCircle2Icon />
                <AlertTitle>简历已解析</AlertTitle>
                <AlertDescription className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                  <span>可以回看解析结果，也可以重新选择 PDF 重新解析。</span>
                  <Button type="button" size="sm" onClick={() => setCurrentStep("analysis")}>
                    查看解析结果
                  </Button>
                </AlertDescription>
              </Alert>
            ) : null}
          </section>
        ) : null}

        {currentStep === "analysis" ? (
          <section className="flex flex-col gap-5">
            <div className="flex flex-col gap-3 rounded-xl border bg-background p-4 md:flex-row md:items-center md:justify-between">
              <div>
                <div className="text-base font-medium">解析结果</div>
                <p className="text-sm text-muted-foreground">
                  先核对关键信息和 PDF 清洗文本，再进入岗位评分。
                </p>
              </div>
              <Button type="button" disabled={!analysis} onClick={() => setCurrentStep("match")}>
                <SearchCheckIcon data-icon="inline-start" />
                进入岗位评分
              </Button>
            </div>

            <div className="grid gap-5 xl:grid-cols-2">
              <ResumeProfileCard analysis={analysis} isAnalyzing={isAnalyzing} />
              <ResumeTextCard analysis={analysis} isAnalyzing={isAnalyzing} />
              <ResultJsonCard analysis={analysis} matchResult={matchResult} />
            </div>
          </section>
        ) : null}

        {currentStep === "match" ? (
          <section className="grid gap-5 lg:grid-cols-[minmax(320px,420px)_1fr]">
            <div className="flex flex-col gap-5">
              <div className="rounded-xl border bg-background p-4">
                <div className="text-base font-medium">岗位评分</div>
                <p className="mt-1 text-sm text-muted-foreground">
                  粘贴岗位描述后生成匹配度、关键词命中和 AI 评分依据。
                </p>
              </div>

              <JobDescriptionCard
                jobDescription={jobDescription}
                hasAnalysis={Boolean(analysis)}
                isMatching={isMatching}
                onChange={setJobDescription}
                onMatch={handleMatch}
              />
            </div>

            <div className="grid gap-5 xl:grid-cols-2">
              <div className="xl:col-span-2">
                <ResumeMatchCard matchResult={matchResult} isMatching={isMatching} />
              </div>
              <ResultJsonCard analysis={analysis} matchResult={matchResult} />
            </div>
          </section>
        ) : null}
      </div>
    </main>
  )
}

function WorkflowProgress({
  currentStep,
  hasAnalysis,
  hasMatchResult,
  onStepChange,
}: {
  currentStep: WorkflowStep
  hasAnalysis: boolean
  hasMatchResult: boolean
  onStepChange: (step: WorkflowStep) => void
}) {
  const currentIndex = workflowSteps.findIndex((step) => step.value === currentStep)

  function isStepEnabled(step: WorkflowStep) {
    if (step === "upload") {
      return true
    }

    if (step === "analysis") {
      return hasAnalysis
    }

    return hasAnalysis
  }

  function getStepStatus(index: number, step: WorkflowStep) {
    if (currentStep === step) {
      return "进行中"
    }

    if (index < currentIndex || (step === "match" && hasMatchResult)) {
      return "已完成"
    }

    return "待开始"
  }

  return (
    <nav className="grid gap-3 rounded-xl border bg-background p-3 lg:grid-cols-3">
      {workflowSteps.map((step, index) => {
        const Icon = step.icon
        const isActive = step.value === currentStep
        const isEnabled = isStepEnabled(step.value)

        return (
          <Button
            key={step.value}
            type="button"
            variant={isActive ? "secondary" : "ghost"}
            className="h-auto justify-start whitespace-normal p-3 text-left"
            disabled={!isEnabled}
            onClick={() => onStepChange(step.value)}
          >
            <Icon data-icon="inline-start" />
            <span className="flex min-w-0 flex-1 flex-col gap-1">
              <span className="flex flex-wrap items-center gap-2">
                <span className="font-medium">{step.title}</span>
                <Badge variant={isActive ? "default" : "outline"}>
                  {getStepStatus(index, step.value)}
                </Badge>
              </span>
              <span className="text-xs font-normal text-muted-foreground">
                {step.description}
              </span>
            </span>
          </Button>
        )
      })}
    </nav>
  )
}
