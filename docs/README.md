# 文档索引

本目录用于沉淀 AI Resume Analyzer 的产品边界、技术架构、接口约定和部署说明。

## 文档列表

- [技术架构](architecture.md): 系统分层、模块职责、数据流和技术选型。
- [API 设计](api-design.md): RESTful 接口、请求响应结构和错误格式。
- [MVP 范围](mvp-scope.md): 必做功能、不做功能和验收标准。
- [部署与环境配置](deployment.md): 本地开发、环境变量、Serverless 和前端部署建议。
- [开发计划](implementation-plan.md): MVP 实现阶段拆分和推荐顺序。

## 当前实现原则

- 优先完成最小可演示闭环。
- 后端保持无状态，适配阿里云函数计算 FC。
- 不在 MVP 阶段引入数据库、Redis、OCR、批量上传和账号系统。
- AI 调用集中在 Python 后端，前端只负责上传、输入 JD 和展示结果。
