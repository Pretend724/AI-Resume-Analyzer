import type { ChangeEvent } from "react"
import { LoaderCircleIcon, UploadIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

import { formatFileSize } from "@/components/resume-analyzer/utils"

export function ResumeUploadCard({
  selectedFile,
  pageCount,
  isAnalyzing,
  onFileChange,
  onAnalyze,
}: {
  selectedFile: File | null
  pageCount?: number
  isAnalyzing: boolean
  onFileChange: (event: ChangeEvent<HTMLInputElement>) => void
  onAnalyze: () => void
}) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>简历上传</CardTitle>
        <CardDescription>PDF 文件最大 10 MB</CardDescription>
        <CardAction>
          {pageCount ? <Badge variant="outline">{pageCount} 页</Badge> : null}
        </CardAction>
      </CardHeader>
      <CardContent>
        <FieldGroup>
          <Field>
            <FieldLabel htmlFor="resume-file">PDF 简历</FieldLabel>
            <Input
              id="resume-file"
              type="file"
              accept="application/pdf,.pdf"
              onChange={onFileChange}
              disabled={isAnalyzing}
            />
            <FieldDescription>
              {selectedFile
                ? `${selectedFile.name} · ${formatFileSize(selectedFile.size)}`
                : "尚未选择文件"}
            </FieldDescription>
          </Field>
          <Button type="button" onClick={onAnalyze} disabled={!selectedFile || isAnalyzing}>
            {isAnalyzing ? (
              <LoaderCircleIcon data-icon="inline-start" className="animate-spin" />
            ) : (
              <UploadIcon data-icon="inline-start" />
            )}
            {isAnalyzing ? "解析中" : "上传并解析"}
          </Button>
        </FieldGroup>
      </CardContent>
    </Card>
  )
}
