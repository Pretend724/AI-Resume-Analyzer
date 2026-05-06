# 技术架构

## 背景

招聘流程中，大量 PDF 简历需要人工阅读、筛选和比对岗位要求。系统目标是构建一个轻量的智能简历分析服务，帮助招聘者快速完成简历解析、关键信息抽取和岗位匹配评分。

## 架构概览

```txt
Browser
  |
  | REST API
  v
Next.js Web App
  |
  | multipart/form-data / JSON
  v
FastAPI Backend
  |
  +-- PyMuPDF: PDF 文本解析
  +-- Text Cleaner: 文本清洗和分段
  +-- Extractor: 关键信息抽取
  +-- Matcher: 岗位匹配评分
  +-- LLM Client: OpenAI-compatible 模型调用
```

## Monorepo 结构

```txt
apps/
  web/
    app/
    components/
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

当前 `apps/api` 还处于 uv 初始化状态，后续实现时建议逐步演进为上面的目录结构。

## 前端技术栈

- Next.js: 页面和静态站点构建。
- React: 交互 UI。
- Tailwind CSS: 样式系统。
- shadcn/ui: 表单、按钮、卡片、徽章、进度条等基础组件。

前端只负责用户交互，不直接调用大模型：

- 上传 PDF。
- 展示解析结果。
- 输入岗位需求描述。
- 展示匹配分数、命中关键词、缺失关键词和分析摘要。

## 后端技术栈

- FastAPI: RESTful API 服务。
- uv: Python 依赖和运行环境管理。
- PyMuPDF: PDF 文本提取，兼容多页简历。
- Pydantic: 请求和响应模型。
- OpenAI-compatible LLM client: 对接阿里云百炼/Qwen 或其他兼容模型服务。

后端负责全部核心业务：

- 校验上传文件。
- 解析 PDF 文本。
- 清洗和分段。
- 抽取结构化简历信息。
- 提取 JD 关键词。
- 计算匹配评分。

## 数据流

1. 用户在前端上传单个 PDF 简历。
2. 前端调用 `POST /resumes/analyze`。
3. 后端校验文件类型和大小。
4. PyMuPDF 逐页提取文本。
5. 文本清洗器去除冗余空白、异常字符和重复段落。
6. 后端调用 AI 模型抽取姓名、电话、邮箱、地址等结构化信息。
7. 前端展示结构化信息和文本预览。
8. 用户输入岗位 JD。
9. 前端调用 `POST /resumes/match`。
10. 后端提取 JD 关键词并与简历信息匹配。
11. 后端返回匹配分数和解释。

## AI 设计

MVP 阶段不使用 Vercel AI SDK 作为核心 AI 层。原因是项目后端采用 Python/FastAPI，简历解析、信息抽取和评分逻辑都应集中在后端，避免业务逻辑分散到 Next.js API Route 或前端。

推荐方案：

```txt
FastAPI -> OpenAI Python SDK -> OpenAI-compatible API
```

通过环境变量配置：

```txt
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

这样可以灵活切换阿里云百炼/Qwen、DeepSeek、OpenAI 等服务。
后端会加载 `apps/api/.env`，`LLM_BASE_URL` 未配置时默认使用 `https://api.openai.com/v1`。

## PDF 解析方案

首选 PyMuPDF：

- 多页 PDF 支持好。
- 文本提取速度快。
- API 简洁。
- 适合 Serverless 部署。

MVP 暂不支持扫描版 PDF OCR。如果 PDF 无可提取文本，后端返回明确错误提示。

## Serverless 适配

后端设计为无状态服务：

- 不依赖本地持久化文件。
- 上传文件只在请求生命周期内处理。
- 不使用 Redis 和数据库。
- 模型密钥通过环境变量注入。

这与阿里云函数计算 FC 的运行模型匹配。
