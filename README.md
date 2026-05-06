# AI Resume Analyzer

AI 赋能的智能简历分析系统，用于上传 PDF 简历、解析文本、提取关键信息，并根据岗位 JD 计算候选人与岗位的匹配度。

## 技术栈

- Monorepo: pnpm workspace + Turborepo
- Frontend: Next.js, React, Tailwind CSS, shadcn/ui
- Backend: Python, FastAPI, uv
- PDF parsing: PyMuPDF
- AI provider: OpenAI-compatible LLM API, 可接阿里云百炼/Qwen、DeepSeek、OpenAI 等

## 工作区

```txt
apps/
  web/  前端交互页面
  api/  Python 后端服务
docs/   项目设计与交付文档
```

## 常用命令

```bash
pnpm dev       # 启动全部工作区
pnpm dev:web   # 仅启动前端
pnpm lint
pnpm check-types
pnpm build
```

## 文档

- [文档索引](docs/README.md)
- [技术架构](docs/architecture.md)
- [API 设计](docs/api-design.md)
- [MVP 范围](docs/mvp-scope.md)
- [部署与环境配置](docs/deployment.md)
