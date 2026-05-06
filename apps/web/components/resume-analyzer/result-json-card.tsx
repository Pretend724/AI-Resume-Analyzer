"use client"

import { useMemo, useState } from "react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"

import { EmptyState } from "@/components/resume-analyzer/shared"

import type { ResumeAnalyzeResponse, ResumeMatchResponse } from "@/lib/api"

type JsonView = "analysis" | "profile" | "match"

const viewLabels: Record<JsonView, string> = {
  analysis: "解析结果",
  profile: "关键信息",
  match: "匹配评分",
}

export function ResultJsonCard({
  analysis,
  matchResult,
}: {
  analysis: ResumeAnalyzeResponse | null
  matchResult: ResumeMatchResponse | null
}) {
  const [view, setView] = useState<JsonView>("analysis")
  const jsonPayload = useMemo(() => {
    if (view === "profile") {
      return analysis?.profile ?? null
    }

    if (view === "match") {
      return matchResult
    }

    return analysis
  }, [analysis, matchResult, view])

  return (
    <Card className="xl:col-span-2">
      <CardHeader>
        <CardTitle>JSON 数据</CardTitle>
        <CardDescription>{viewLabels[view]}</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <ToggleGroup
            type="single"
            variant="outline"
            value={view}
            onValueChange={(value) => {
              if (value) {
                setView(value as JsonView)
              }
            }}
            className="flex-wrap"
          >
            <ToggleGroupItem value="analysis">解析结果</ToggleGroupItem>
            <ToggleGroupItem value="profile">关键信息</ToggleGroupItem>
            <ToggleGroupItem value="match">匹配评分</ToggleGroupItem>
          </ToggleGroup>

          {jsonPayload ? (
            <pre className="max-h-96 overflow-auto rounded-lg border bg-muted/20 p-4 text-sm leading-6 whitespace-pre-wrap">
              {JSON.stringify(jsonPayload, null, 2)}
            </pre>
          ) : (
            <EmptyState
              title="暂无 JSON 数据"
              description="完成对应步骤后可查看结构化响应。"
            />
          )}
        </div>
      </CardContent>
    </Card>
  )
}
