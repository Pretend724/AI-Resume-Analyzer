# 开发计划

本文档描述从当前仓库状态到 MVP 可演示版本的推荐实现顺序。

## 阶段一：后端基础服务

目标：让 `apps/api` 成为可运行的 FastAPI 服务。

任务：

- 添加 FastAPI、uvicorn、pydantic、python-multipart。
- 建立 `app/main.py`。
- 添加 `GET /health`。
- 调整 `apps/api/package.json` 脚本，使用 uvicorn 启动服务。

建议目录：

```txt
apps/api/
  app/
    main.py
    routers/
    services/
    schemas/
```

验收：

```bash
cd apps/api
uv run uvicorn app.main:app --reload --port 8000
```

访问：

```txt
http://localhost:8000/health
```

## 阶段二：PDF 上传与解析

目标：完成 `POST /resumes/analyze` 的文件上传和文本解析。

任务：

- 添加 PyMuPDF。
- 校验文件扩展名和 MIME 类型。
- 限制文件大小。
- 多页提取文本。
- 对空文本 PDF 返回 `EMPTY_PDF_TEXT`。

核心服务：

```txt
services/pdf_parser.py
services/text_cleaner.py
```

验收：

- 上传文本型 PDF 可以返回页数和清洗文本。
- 上传非 PDF 返回结构化错误。

## 阶段三：关键信息抽取

目标：从简历文本中抽取结构化信息。

任务：

- 用正则提取电话和邮箱。
- 实现 `services/llm_client.py`。
- 实现 `services/extractor.py`。
- 使用 Pydantic 校验 AI 返回结构。

环境变量：

```txt
LLM_BASE_URL
LLM_API_KEY
LLM_MODEL
```

验收：

- 返回姓名、电话、邮箱、地址。
- AI 返回异常时仍能返回可解释错误。

## 阶段四：岗位匹配评分

目标：完成 `POST /resumes/match`。

任务：

- 从 JD 中提取关键词。
- 与简历文本做关键词覆盖率计算。
- 生成总分、命中关键词、缺失关键词。
- 可选调用 AI 生成简短摘要。

核心服务：

```txt
services/matcher.py
```

验收：

- 输入 JD 后返回 `0-100` 分数。
- 返回匹配关键词和缺失关键词。

## 阶段五：前端页面

目标：完成可公开演示的单页交互。

任务：

- 上传 PDF 表单。
- 解析结果展示。
- JD 输入框。
- 匹配结果展示。
- Loading、错误、空状态。

建议组件：

- `Button`
- `Card`
- `Textarea`
- `Input`
- `Badge`
- `Progress`

验收：

- 可以从页面完成上传、解析、输入 JD、查看评分的完整流程。

## 阶段六：部署准备

目标：满足线上验收。

任务：

- 后端部署到阿里云函数计算 FC。
- 前端部署到 Vercel、Cloudflare Pages 或 GitHub Pages。
- 配置 CORS。
- 配置生产环境变量。
- 更新 README 中的线上访问地址。

验收：

- 评审团队可以通过公开前端地址访问系统。
- 前端可以调用公网后端 API。

## 推荐提交顺序

1. `docs`: 项目文档和架构设计。
2. `api`: FastAPI 基础服务。
3. `api`: PDF 解析和文本清洗。
4. `api`: AI 抽取和匹配评分。
5. `web`: 前端 MVP 页面。
6. `deploy`: 部署配置和线上说明。
