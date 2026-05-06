# 技术架构

## 背景

招聘流程中，大量 PDF 简历需要阅读、筛选并与岗位要求进行比对。AI Resume Analyzer 提供一套前后端分离的智能分析系统，用于解析 PDF 简历、抽取关键信息，并结合岗位描述输出匹配度评分和解释。

## 架构概览

```txt
Browser
  |
  | Next.js UI
  v
Web Workspace
  |
  | REST API / multipart/form-data / JSON
  v
FastAPI Backend
  |
  +-- PyMuPDF: PDF 文本解析
  +-- Text Cleaner: 文本清洗和分段
  +-- Extractor: 结构化信息抽取
  +-- Matcher: 关键词、经验和匹配度分析
  +-- LLM Client: OpenAI SDK + compatible provider
  +-- Runtime Config: LLM 提供商配置与连接测试
```

## Monorepo 结构

```txt
apps/
  web/
    app/
    components/
      resume-analyzer/
      ui/
    lib/
  api/
    app/
      main.py
      routers/
      services/
      schemas/
    pyproject.toml
docs/
```

## 前端架构

前端位于 `apps/web`，使用 Next.js App Router。

主要职责：

- 提供三步式工作台流程。
- 配置并测试 LLM 提供商。
- 上传 PDF 简历。
- 展示关键信息、解析文本和结构化 JSON。
- 输入岗位描述并展示匹配评分。

主要技术：

- Next.js: 应用路由与构建。
- React: 交互状态和组件组织。
- Tailwind CSS: 样式系统。
- shadcn/ui: 表单、按钮、卡片、徽章、进度条、提示等基础组件。
- lucide-react: 图标。

## 后端架构

后端位于 `apps/api`，使用 FastAPI 提供 RESTful API。

主要职责：

- 校验 PDF 上传文件。
- 使用 PyMuPDF 提取多页 PDF 文本。
- 清洗文本并识别中文、英文简历段落标题。
- 使用规则和 LLM 抽取结构化候选人信息。
- 提取岗位关键词并计算匹配基础分。
- 使用 LLM 增强岗位匹配评分和摘要。
- 支持运行时 LLM provider 配置和连接测试。

主要技术：

- FastAPI: API 服务。
- Pydantic: 请求和响应模型。
- uv: Python 依赖和运行环境管理。
- PyMuPDF: PDF 文本提取。
- OpenAI Python SDK: 调用 OpenAI-compatible Chat Completions API。

## 数据流

1. 用户在前端配置或测试 LLM 提供商。
2. 用户上传单个 PDF 简历。
3. 前端调用 `POST /resumes/analyze`。
4. 后端校验文件类型、大小和 PDF 内容。
5. PyMuPDF 逐页提取文本。
6. 文本清洗器生成清洗文本和分段。
7. 信息抽取服务结合规则和 LLM 生成结构化简历信息。
8. 前端展示解析结果和 JSON 数据。
9. 用户输入岗位描述。
10. 前端调用 `POST /resumes/match`。
11. 后端计算关键词、经验和规则评分。
12. 后端调用 LLM 生成增强评分、摘要和评分依据。
13. 前端展示综合评分、关键词命中、缺失关键词和解释。

## AI 设计

系统不使用 Vercel AI SDK 作为核心 AI 层。简历解析、信息抽取和评分逻辑集中在 Python/FastAPI 后端，便于统一校验、兜底和部署。

调用链：

```txt
FastAPI -> OpenAI Python SDK -> OpenAI-compatible API
```

配置方式：

- 后端环境变量：`LLM_BASE_URL`、`LLM_API_KEY`、`LLM_MODEL`
- 前端运行时配置：`GET/PUT/DELETE /llm/config`
- 连接测试：`POST /llm/config/test`

`LLM_BASE_URL` 未配置时默认使用：

```txt
https://api.openai.com/v1
```

## PDF 解析方案

系统使用 PyMuPDF 解析文本型 PDF：

- 支持多页 PDF。
- 文本提取速度快。
- API 简洁，适合部署到无状态服务。

扫描版 PDF 暂不做 OCR。若 PDF 没有可提取文本，后端返回明确的 `EMPTY_PDF_TEXT` 错误。

## 无状态设计

后端按无状态服务设计：

- 不持久化上传文件。
- 不依赖本地数据库。
- 不依赖 Redis。
- 运行时 LLM 配置保存在当前后端进程内。
- 生产密钥通过部署平台环境变量或页面运行时配置提供。

这种模式适合阿里云函数计算 FC、自定义容器和其他 Serverless/容器平台。
