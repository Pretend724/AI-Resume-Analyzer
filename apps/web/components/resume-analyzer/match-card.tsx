import { BotMessageSquare, BriefcaseBusinessIcon } from "lucide-react"

import { Badge } from "@/components/ui/badge"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"

import { cn } from "@/lib/utils"
import {
  levelText,
  levelTone,
  scoringSourceText,
} from "@/components/resume-analyzer/utils"
import { EmptyState, KeywordList } from "@/components/resume-analyzer/shared"

import type { ResumeMatchResponse } from "@/lib/api"

export function ResumeMatchCard({
  matchResult,
  isMatching,
}: {
  matchResult: ResumeMatchResponse | null
  isMatching: boolean
}) {
  const tone = matchResult ? levelTone[matchResult.level] : null

  return (
    <Card>
      <CardHeader>
        <CardTitle>匹配评分</CardTitle>
        <CardDescription>
          {matchResult
            ? `${levelText[matchResult.level]} · ${scoringSourceText[matchResult.scoring.source]}`
            : "等待 JD"}
        </CardDescription>
        <CardAction>
          {matchResult ? (
            <Badge variant="outline" className={tone?.badgeClassName}>
              {matchResult.score} 分
            </Badge>
          ) : null}
        </CardAction>
      </CardHeader>
      <CardContent>
        {isMatching ? (
          <EmptyState title="评分中" description="正在计算关键词和经验相关性。" />
        ) : matchResult ? (
          <div className="flex flex-col gap-4">
            <div className={cn("rounded-lg border p-4", tone?.panelClassName)}>
              <div className="flex items-end justify-between gap-3">
                <div>
                  <div className="text-sm text-muted-foreground">综合匹配度</div>
                  <div className={cn("mt-1 text-4xl font-semibold", tone?.scoreClassName)}>
                    {matchResult.score}
                  </div>
                </div>
                <Badge variant="outline" className={tone?.badgeClassName}>
                  {levelText[matchResult.level]}
                </Badge>
              </div>
              <Progress value={matchResult.score} className="mt-4" />
            </div>

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border p-3">
                <div className="text-xs text-muted-foreground">关键词评分</div>
                <div className="mt-1 text-2xl font-semibold">
                  {matchResult.score_breakdown.keyword_score}
                </div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-xs text-muted-foreground">经验评分</div>
                <div className="mt-1 text-2xl font-semibold">
                  {matchResult.score_breakdown.experience_score}
                </div>
              </div>
              <div className="rounded-lg border p-3">
                <div className="text-xs text-muted-foreground">AI 评分</div>
                <div className="mt-1 text-2xl font-semibold">
                  {matchResult.score_breakdown.llm_score ?? "无"}
                </div>
              </div>
            </div>

            <p className="text-sm text-muted-foreground">{matchResult.summary}</p>

            <Separator />

            <KeywordList
              title={`命中关键词 · ${Math.round(matchResult.keyword_analysis.match_rate * 100)}%`}
              items={matchResult.keyword_analysis.matched_keywords}
              emptyText="暂无命中"
            />
            {/* <KeywordList
              title="缺失关键词"
              items={matchResult.keyword_analysis.missing_keywords}
              emptyText="无明显缺失"
              variant="outline"
            /> */}

            <Alert>
              <BriefcaseBusinessIcon />
              <AlertTitle>经验相关性</AlertTitle>
              <AlertDescription>
                {matchResult.experience_analysis.summary}
              </AlertDescription>
            </Alert>

            {matchResult.scoring.rationale ? (
              <Alert>
                <BotMessageSquare />
                <AlertTitle>AI 评分依据</AlertTitle>
                <AlertDescription>{matchResult.scoring.rationale}</AlertDescription>
              </Alert>
            ) : null}

            {matchResult.scoring.warnings.length > 0 ? (
              <Alert>
                <BriefcaseBusinessIcon />
                <AlertTitle>评分提示</AlertTitle>
                <AlertDescription>
                  {matchResult.scoring.warnings.join("；")}
                </AlertDescription>
              </Alert>
            ) : null}
          </div>
        ) : (
          <EmptyState
            title="暂无匹配结果"
            description="解析简历并输入 JD 后会展示评分、关键词和经验相关性。"
          />
        )}
      </CardContent>
    </Card>
  )
}
