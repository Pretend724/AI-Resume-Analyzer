# API 设计

后端采用 RESTful API，返回 JSON。MVP 阶段接口保持无状态，不依赖数据库。

## 通用约定

Base URL:

```txt
http://localhost:8000
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
  "resume_id": "sha256-or-request-id",
  "file": {
    "filename": "resume.pdf",
    "page_count": 2
  },
  "text": {
    "raw": "...",
    "cleaned": "...",
    "sections": [
      {
        "title": "工作经历",
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
      "education": [
        {
          "school": "某某大学",
          "degree": "本科",
          "major": "计算机科学与技术"
        }
      ],
      "projects": [
        {
          "name": "智能简历分析系统",
          "description": "..."
        }
      ]
    }
  }
}
```

可能错误：

- `INVALID_FILE_TYPE`: 非 PDF 文件。
- `EMPTY_PDF_TEXT`: PDF 中未提取到有效文本。
- `PDF_PARSE_FAILED`: PDF 解析失败。
- `LLM_RESPONSE_INVALID`: AI 返回无法解析为目标 JSON。

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
  "score": 78,
  "level": "good",
  "keyword_analysis": {
    "required_keywords": ["Python", "FastAPI", "RESTful API"],
    "matched_keywords": ["Python", "FastAPI"],
    "missing_keywords": ["Redis"],
    "match_rate": 0.67
  },
  "experience_analysis": {
    "is_relevant": true,
    "summary": "候选人的后端项目经历与岗位要求相关。"
  },
  "summary": "候选人与岗位整体匹配度较高，但缓存和部署经验体现不足。"
}
```

评分建议：

- `90-100`: excellent
- `75-89`: good
- `60-74`: fair
- `0-59`: weak

## MVP 评分策略

MVP 可先采用规则评分：

- 技能关键词覆盖率。
- 岗位关键词覆盖率。
- 工作年限或项目经验是否相关。
- AI 生成简短解释，但不完全依赖 AI 产生分数。

后续可升级为规则评分 + AI 评分融合。
