import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

import { EmptyState } from "@/components/resume-analyzer/shared"
import { formatFileSize } from "@/components/resume-analyzer/utils"

import type { ResumeAnalyzeResponse } from "@/lib/api"

export function ResumeTextCard({
  analysis,
  isAnalyzing,
}: {
  analysis: ResumeAnalyzeResponse | null
  isAnalyzing: boolean
}) {
  const sectionsPreview = analysis?.text.sections.slice(0, 4) ?? []

  return (
    <Card className="xl:col-span-2">
      <CardHeader>
        <CardTitle>解析文本</CardTitle>
        <CardDescription>
          {analysis
            ? `${analysis.file.filename} · ${formatFileSize(analysis.file.size_bytes)}`
            : "等待 PDF 文本"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isAnalyzing ? (
          <EmptyState title="解析中" description="请稍候，正在读取 PDF 文本。" />
        ) : analysis ? (
          <div className="grid gap-4 lg:grid-cols-[280px_1fr]">
            <div className="flex flex-col gap-3">
              {sectionsPreview.map((section) => (
                <div
                  key={`${section.title}-${section.content.slice(0, 16)}`}
                  className="rounded-lg border p-3"
                >
                  <div className="font-medium">{section.title}</div>
                  <p className="mt-1 line-clamp-3 text-sm text-muted-foreground">
                    {section.content}
                  </p>
                </div>
              ))}
            </div>
            <pre className="max-h-96 overflow-auto rounded-lg border bg-muted/20 p-4 text-sm leading-6 whitespace-pre-wrap">
              {analysis.text.cleaned}
            </pre>
          </div>
        ) : (
          <EmptyState
            title="暂无解析文本"
            description="多页 PDF 的清洗文本会在这里展示。"
          />
        )}
      </CardContent>
    </Card>
  )
}
