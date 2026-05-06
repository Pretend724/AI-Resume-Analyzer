# API 设计

后端采用 RESTful API，返回 JSON。服务保持无状态，不依赖数据库和文件持久化存储。

## 通用约定

本地 Base URL:

```txt
http://localhost:8001
```

生产环境通过部署平台域名提供。

通用错误响应：

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Only PDF files are supported."
  }
}
```

## GET /health

健康检查。

响应：

```json
{
  "status": "ok"
}
```

## LLM 配置接口

### GET /llm/config

读取当前后端使用的 LLM provider 配置状态。API Key 不会回传。

响应：

```json
{
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "is_configured": true,
  "api_key_configured": true,
  "missing_fields": [],
  "source": "runtime"
}
```

`source`:

- `env`: 使用后端环境变量。
- `runtime`: 使用页面提交的运行时配置。

### PUT /llm/config

保存运行时 LLM provider 配置。保存后当前后端进程的解析和评分都会使用该配置。

请求：

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "your-api-key",
  "model": "gpt-4o-mini"
}
```

响应同 `GET /llm/config`。

### POST /llm/config/test

使用请求中的配置发起一次临时连接测试，不保存配置。

请求：

```json
{
  "base_url": "https://api.openai.com/v1",
  "api_key": "your-api-key",
  "model": "gpt-4o-mini"
}
```

响应：

```json
{
  "success": true,
  "message": "OK"
}
```

### DELETE /llm/config

清除运行时配置，恢复使用后端环境变量。

响应同 `GET /llm/config`。

## POST /resumes/analyze

上传单个 PDF 简历，解析文本并抽取关键信息。

Content-Type:

```txt
multipart/form-data
```

请求字段：

```txt
file: PDF file
```

成功响应：

```json
{
  "resume_id": "sha256",
  "file": {
    "filename": "resume.pdf",
    "content_type": "application/pdf",
    "page_count": 2,
    "size_bytes": 204800
  },
  "text": {
    "raw": "...",
    "cleaned": "...",
    "sections": [
      {
        "title": "项目经历",
        "content": "..."
      }
    ]
  },
  "profile": {
    "basic_info": {
      "name": "张三",
      "phone": "13800000000",
      "email": "zhangsan@example.com",
      "address": "上海"
    },
    "job_intention": {
      "desired_position": "后端工程师",
      "expected_salary": "20k-30k"
    },
    "background": {
      "years_of_experience": "3年",
      "education": [],
      "projects": []
    }
  },
  "profile_extraction": {
    "source": "llm",
    "warnings": []
  }
}
```

`profile_extraction.source`:

- `heuristic`: 使用规则抽取。
- `llm`: 使用 LLM 抽取并通过结构校验。
- `llm_fallback`: LLM 调用或解析失败，返回规则兜底结果。

可能错误：

- `INVALID_FILE_TYPE`: 非 PDF 文件。
- `EMPTY_UPLOAD`: 上传文件为空。
- `FILE_TOO_LARGE`: 文件超过大小限制。
- `EMPTY_PDF_TEXT`: PDF 中未提取到有效文本。
- `PDF_PARSE_FAILED`: PDF 解析失败。

## POST /resumes/match

接收岗位需求描述，对简历和岗位做匹配评分。

Content-Type:

```txt
application/json
```

请求：

```json
{
  "resume_text": "清洗后的简历文本",
  "resume_profile": {
    "basic_info": {
      "name": "张三",
      "phone": "13800000000",
      "email": "zhangsan@example.com",
      "address": "上海"
    }
  },
  "job_description": "岗位职责：负责 Python 后端开发，熟悉 FastAPI..."
}
```

成功响应：

```json
{
  "score": 82,
  "level": "good",
  "keyword_analysis": {
    "required_keywords": ["Python", "FastAPI", "RESTful API"],
    "matched_keywords": ["Python", "FastAPI"],
    "missing_keywords": ["Redis"],
    "match_rate": 0.67
  },
  "experience_analysis": {
    "is_relevant": true,
    "required_years": 3,
    "candidate_years": 5,
    "summary": "岗位要求约 3 年经验，候选人体现约 5 年经验。"
  },
  "score_breakdown": {
    "keyword_score": 67,
    "experience_score": 100,
    "llm_score": 82
  },
  "summary": "候选人与岗位整体匹配度较高，但缓存经验仍需进一步确认。",
  "scoring": {
    "source": "llm",
    "warnings": [],
    "rationale": "简历体现 Python 与 FastAPI 项目经验，经验年限满足要求。"
  }
}
```

`level`:

- `excellent`: 90-100
- `good`: 75-89
- `fair`: 60-74
- `weak`: 0-59

`scoring.source`:

- `rule_based`: 使用规则评分。
- `llm`: 使用 LLM 增强评分。
- `llm_fallback`: LLM 调用失败，返回规则评分。

## 评分策略

岗位匹配分为两个层次：

1. 规则分析：提取岗位关键词，计算命中和缺失关键词，分析工作年限相关性。
2. LLM 增强：把规则分析、简历文本、结构化信息和岗位描述提供给模型，由模型生成最终分数、摘要和评分依据。

LLM 不可用时，系统保留规则评分和可解释 warning。
