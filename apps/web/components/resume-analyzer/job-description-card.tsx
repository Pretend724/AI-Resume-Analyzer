import { LoaderCircleIcon, SearchCheckIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  Field,
  FieldDescription,
  FieldError,
  FieldGroup,
  FieldLabel,
} from "@/components/ui/field"
import { Textarea } from "@/components/ui/textarea"

export function JobDescriptionCard({
  jobDescription,
  hasAnalysis,
  isMatching,
  onChange,
  onMatch,
}: {
  jobDescription: string
  hasAnalysis: boolean
  isMatching: boolean
  onChange: (value: string) => void
  onMatch: () => void
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>岗位需求</CardTitle>
        <CardDescription>粘贴 JD 文本生成匹配评分</CardDescription>
      </CardHeader>
      <CardContent>
        <FieldGroup>
          <Field data-invalid={Boolean(jobDescription.length > 0 && !hasAnalysis)}>
            <FieldLabel htmlFor="job-description">JD 文本</FieldLabel>
            <Textarea
              id="job-description"
              value={jobDescription}
              onChange={(event) => onChange(event.target.value)}
              placeholder="例如：负责 Next.js 前端开发，熟悉 TypeScript、组件化工程，有 3 年以上 Web 项目经验。"
              className="min-h-60 resize-y max-h-160"
              aria-invalid={Boolean(jobDescription.length > 0 && !hasAnalysis)}
            />
            {!hasAnalysis && jobDescription.length > 0 ? (
              <FieldError>请先解析简历后再匹配岗位</FieldError>
            ) : (
              <FieldDescription>当前 {jobDescription.trim().length} 个字符</FieldDescription>
            )}
          </Field>
          <Button type="button" onClick={onMatch} disabled={!hasAnalysis || isMatching}>
            {isMatching ? (
              <LoaderCircleIcon data-icon="inline-start" className="animate-spin" />
            ) : (
              <SearchCheckIcon data-icon="inline-start" />
            )}
            {isMatching ? "评分中" : "生成匹配评分"}
          </Button>
        </FieldGroup>
      </CardContent>
    </Card>
  )
}
