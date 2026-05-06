# 部署与环境配置

## 本地开发

安装依赖：

```bash
pnpm install
```

启动后端：

```bash
cd apps/api
pnpm dev
```

后端默认地址：

```txt
http://localhost:8001
```

启动前端：

```bash
pnpm dev:web
```

前端默认地址：

```txt
http://localhost:3000
```

## 环境变量

后端：

```txt
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=your-api-key
LLM_MODEL=gpt-4o-mini
MAX_UPLOAD_SIZE_MB=10
```

本地开发时可写入：

```txt
apps/api/.env
```

生产环境建议配置到部署平台的环境变量中。页面中的 LLM provider 配置会覆盖当前后端进程的环境变量配置，适合临时切换模型服务。

前端：

```txt
NEXT_PUBLIC_API_BASE_URL=http://localhost:8001
```

生产环境需要将该值指向已部署的后端 API 域名。

## 后端部署

后端是标准 FastAPI ASGI 应用，入口：

```txt
apps/api/app/main.py
```

应用对象：

```txt
app
```

### 阿里云函数计算 FC

后端可部署到阿里云函数计算 FC。

推荐方式：

- 使用自定义容器部署 FastAPI。
- 或使用 Python runtime + HTTP 触发器适配 ASGI。

部署原则：

- 通过环境变量注入默认模型配置。
- 不依赖本地持久化存储。
- 上传文件仅在请求生命周期内处理。
- 运行时 LLM 配置保存在当前进程内，实例重启后恢复环境变量配置。

### 容器部署

也可以部署到任意支持 Python ASGI 的容器平台，例如 Cloud Run、Render、Railway 或 ECS。

启动命令示例：

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 前端部署

前端位于 `apps/web`，可部署到：

- Vercel
- Cloudflare Pages
- Netlify
- 其他支持 Next.js 的平台

部署时配置：

```txt
NEXT_PUBLIC_API_BASE_URL=https://your-api-domain.example.com
```

如果选择纯静态部署，需要确认当前页面不依赖服务端运行时能力，并根据目标平台调整 `next.config.js`。

## 跨域配置

当前后端 CORS 允许所有来源，便于本地和多平台部署调试。生产环境可按实际前端域名收紧：

```txt
https://your-web-domain.example.com
```

## 构建检查

提交前建议运行：

```bash
pnpm lint
pnpm check-types
pnpm build
```

后端单独检查：

```bash
cd apps/api
uv run python -m compileall -q main.py app
```
