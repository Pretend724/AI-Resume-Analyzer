# AI Resume Analyzer

AI Resume Analyzer 是一个智能简历分析系统，支持上传 PDF 简历、提取结构化候选人信息，并结合岗位描述生成匹配度评分、关键词命中情况和分析摘要。

## 项目架构

```txt
AI-Resume-Analyzer/
  apps/
    web/          Next.js 前端工作台
    api/          FastAPI 后端服务
  docs/           架构、接口、部署和产品边界文档
```

系统采用前后端分离架构：

- 前端负责三步式交互流程：配置 LLM、上传简历、查看解析结果、输入岗位描述并查看评分。
- 后端负责 PDF 解析、文本清洗、信息抽取、岗位匹配、AI 调用和运行时 LLM 提供商配置。
- AI 服务通过 OpenAI-compatible Chat Completions API 接入，可使用 OpenAI、阿里云百炼/Qwen、DeepSeek 或其他兼容服务。

## 技术选型

- Monorepo: pnpm workspace + Turborepo
- Frontend: Next.js, React, Tailwind CSS, shadcn/ui, lucide-react
- Backend: Python, FastAPI, Pydantic, uv
- PDF: PyMuPDF
- AI: OpenAI Python SDK + OpenAI-compatible provider
- Runtime config: 后端提供 `/llm/config` 接口支持页面自定义模型服务

## 本地启动

安装依赖：

```bash
pnpm install
```

启动后端：

```bash
cd apps/api
pnpm dev
```

后端默认运行在：

```txt
http://localhost:8001
```

启动前端：

```bash
pnpm dev:web
```

前端默认运行在：

```txt
http://localhost:3000
```

## LLM 配置

开发阶段可以在 `apps/api/.env` 中配置默认模型服务：

```txt
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4o-mini
```

也可以在前端页面的「LLM 提供商」卡片中填写：

- Base URL
- Model
- API Key

点击「测试连接」可以验证模型服务是否可用；点击「保存配置」后，当前后端进程会使用页面提交的提供商配置。API Key 不会在页面中回显。

## 使用流程

1. 打开前端工作台。
2. 在「LLM 提供商」中配置或测试模型服务。
3. 上传单个 PDF 简历并解析。
4. 查看关键信息、清洗文本和 JSON 数据。
5. 输入岗位描述。
6. 生成匹配评分、关键词命中、缺失关键词、经验相关性和 AI 评分依据。

## 常用命令

```bash
pnpm dev             # 启动全部工作区
pnpm dev:web         # 仅启动前端
pnpm lint            # 运行 lint
pnpm check-types     # 类型检查
pnpm build           # 构建所有工作区
```

后端单独检查：

```bash
cd apps/api
uv run python -m compileall -q main.py app
```

## 部署方式

前端可部署到 Vercel、Cloudflare Pages 或其他支持 Next.js 的平台。部署时配置：

```txt
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.example.com
```

后端可部署到阿里云函数计算 FC、自定义容器、Cloud Run、Render 等支持 Python ASGI 服务的平台。生产环境建议通过平台环境变量配置：

```txt
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4o-mini
```

后端服务入口为：

```txt
apps/api/app/main.py
```

FastAPI app 对象为：

```txt
app
```

## 文档

- [文档索引](docs/README.md)
- [技术架构](docs/architecture.md)
- [API 设计](docs/api-design.md)
- [产品范围](docs/product-scope.md)
- [部署与环境配置](docs/deployment.md)
- [开发计划](docs/implementation-plan.md)
