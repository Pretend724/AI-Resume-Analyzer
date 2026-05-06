# 文档索引

本目录用于记录 AI Resume Analyzer 的产品范围、技术架构、接口约定、部署方式和开发计划。

## 文档列表

- [技术架构](architecture.md): 系统分层、模块职责、数据流和技术选型。
- [API 设计](api-design.md): RESTful 接口、请求响应结构、错误格式和 LLM 配置接口。
- [产品范围](product-scope.md): 当前功能边界、暂不支持能力和运行约束。
- [部署与环境配置](deployment.md): 本地开发、环境变量、后端部署和前端部署说明。
- [开发计划](implementation-plan.md): 已完成模块、当前实现状态和后续方向。

## 当前实现原则

- 前后端分离，核心解析和 AI 调用集中在 FastAPI 后端。
- 后端保持无状态，上传文件仅在请求生命周期内处理。
- AI provider 使用 OpenAI-compatible Chat Completions API。
- 前端提供 LLM 提供商配置、连接测试、PDF 上传、解析展示和岗位评分流程。
- 不在当前版本中引入数据库、Redis、账号系统、批量上传和 OCR。
