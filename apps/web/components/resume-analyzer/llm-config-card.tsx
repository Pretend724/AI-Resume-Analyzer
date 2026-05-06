"use client"

import { useEffect, useState } from "react"
import { BotMessageSquareIcon, LoaderCircleIcon, RotateCcwIcon, SaveIcon } from "lucide-react"

import {
  getLLMConfig,
  resetLLMConfig,
  updateLLMConfig,
  type LLMConfigResponse,
} from "@/lib/api"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardAction,
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
import { Input } from "@/components/ui/input"

export function LLMConfigCard({
  onError,
}: {
  onError: (message: string) => void
}) {
  const [config, setConfig] = useState<LLMConfigResponse | null>(null)
  const [baseUrl, setBaseUrl] = useState("")
  const [apiKey, setApiKey] = useState("")
  const [model, setModel] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isResetting, setIsResetting] = useState(false)

  useEffect(() => {
    let isMounted = true

    getLLMConfig()
      .then((result) => {
        if (!isMounted) {
          return
        }
        syncConfig(result)
      })
      .catch((caughtError) => {
        if (!isMounted) {
          return
        }
        onError(caughtError instanceof Error ? caughtError.message : "读取 LLM 配置失败")
      })
      .finally(() => {
        if (isMounted) {
          setIsLoading(false)
        }
      })

    return () => {
      isMounted = false
    }
  }, [onError])

  function syncConfig(nextConfig: LLMConfigResponse) {
    setConfig(nextConfig)
    setBaseUrl(nextConfig.base_url)
    setModel(nextConfig.model)
    setApiKey("")
  }

  async function handleSave() {
    if (!apiKey.trim()) {
      onError("请输入 LLM API Key")
      return
    }

    setIsSaving(true)
    try {
      const result = await updateLLMConfig({
        baseUrl,
        apiKey,
        model,
      })
      syncConfig(result)
    } catch (caughtError) {
      onError(caughtError instanceof Error ? caughtError.message : "保存 LLM 配置失败")
    } finally {
      setIsSaving(false)
    }
  }

  async function handleReset() {
    setIsResetting(true)
    try {
      const result = await resetLLMConfig()
      syncConfig(result)
    } catch (caughtError) {
      onError(caughtError instanceof Error ? caughtError.message : "恢复默认 LLM 配置失败")
    } finally {
      setIsResetting(false)
    }
  }

  const isConfigured = Boolean(config?.is_configured)
  const isRuntime = config?.source === "runtime"

  return (
    <Card>
      <CardHeader>
        <CardTitle>LLM 提供商</CardTitle>
        <CardDescription>
          {isLoading ? "正在读取配置" : isRuntime ? "当前使用自定义提供商" : "配置用于简历解析与匹配评分"}
        </CardDescription>
        <CardAction>
          <Badge variant={isConfigured ? "default" : "outline"}>
            {isConfigured ? "可用" : "未配置"}
          </Badge>
        </CardAction>
      </CardHeader>
      <CardContent>
        <FieldGroup>
          <Alert>
            <BotMessageSquareIcon />
            <AlertTitle>自定义模型服务</AlertTitle>
            <AlertDescription>
              填写兼容 OpenAI Chat Completions 的服务地址、模型和 API Key。
            </AlertDescription>
          </Alert>

          <Field>
            <FieldLabel htmlFor="llm-base-url">Base URL</FieldLabel>
            <Input
              id="llm-base-url"
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              placeholder="https://api.openai.com/v1"
              disabled={isLoading || isSaving || isResetting}
            />
            <FieldDescription>OpenAI 或 OpenAI-compatible 服务地址</FieldDescription>
          </Field>

          <Field data-invalid={!model.trim()}>
            <FieldLabel htmlFor="llm-model">模型</FieldLabel>
            <Input
              id="llm-model"
              value={model}
              onChange={(event) => setModel(event.target.value)}
              placeholder="gpt-4o-mini / qwen-plus / MiMo-V2.5-Pro"
              aria-invalid={!model.trim()}
              disabled={isLoading || isSaving || isResetting}
            />
            {!model.trim() ? <FieldError>请输入模型名称</FieldError> : null}
          </Field>

          <Field>
            <FieldLabel htmlFor="llm-api-key">API Key</FieldLabel>
            <Input
              id="llm-api-key"
              type="password"
              value={apiKey}
              onChange={(event) => setApiKey(event.target.value)}
              placeholder="请输入 API Key"
              disabled={isLoading || isSaving || isResetting}
            />
            <FieldDescription>API Key 不会在页面中回显</FieldDescription>
          </Field>

          <div className="flex flex-col gap-2 sm:flex-row">
            <Button
              type="button"
              onClick={handleSave}
              disabled={isLoading || isSaving || isResetting || !model.trim()}
            >
              {isSaving ? (
                <LoaderCircleIcon data-icon="inline-start" className="animate-spin" />
              ) : (
                <SaveIcon data-icon="inline-start" />
              )}
              保存配置
            </Button>
            <Button
              type="button"
              variant="outline"
              onClick={handleReset}
              disabled={isLoading || isSaving || isResetting}
            >
              {isResetting ? (
                <LoaderCircleIcon data-icon="inline-start" className="animate-spin" />
              ) : (
                <RotateCcwIcon data-icon="inline-start" />
              )}
              恢复默认
            </Button>
          </div>
        </FieldGroup>
      </CardContent>
    </Card>
  )
}
