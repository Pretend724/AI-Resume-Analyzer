# 部署与环境配置

## 本地开发

安装前端依赖：

```bash
pnpm install
```

启动全部工作区：

```bash
pnpm dev
```

仅启动前端：

```bash
pnpm dev:web
```

后端开发建议进入 `apps/api` 后直接使用 uv：

```bash
cd apps/api
uv run main.py
```

FastAPI 实现后建议使用：

```bash
uv run fastapi dev app/main.py
```

或：

```bash
uv run uvicorn app.main:app --reload --port 8000
```

## 环境变量

后端：

```txt
LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_API_KEY=your-api-key
LLM_MODEL=qwen-plus
MAX_UPLOAD_SIZE_MB=10
```

前端：

```txt
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

生产环境中，密钥只配置在后端 Serverless 环境变量中，不暴露到前端。

## 阿里云函数计算 FC

后端目标部署到阿里云函数计算 FC。

部署原则：

- FastAPI 作为 HTTP 服务入口。
- 使用环境变量注入模型配置。
- 不依赖本地持久化存储。
- 上传文件只在请求生命周期内读取和解析。

建议后端入口：

```txt
apps/api/app/main.py
```

应用对象：

```python
app = FastAPI()
```

具体 FC 适配方式可以在实现阶段根据所选运行时决定：

- 使用自定义容器部署 FastAPI。
- 或使用 FC Python runtime + HTTP 触发器适配 ASGI。

MVP 推荐优先选择自定义容器或平台支持最直接的 FastAPI 部署方式，减少适配成本。

## 前端部署

评审要求前端需要公开访问。可选方案：

- Vercel: 最适合 Next.js，部署最简单。
- Cloudflare Pages: 适合静态导出。
- GitHub Pages: 需要将 Next.js 配置为静态导出。

如果选择 GitHub Pages，前端需要避免依赖服务端渲染能力，并配置静态导出：

```js
// apps/web/next.config.js
const nextConfig = {
  output: "export",
};

export default nextConfig;
```

后端 API 地址通过 `NEXT_PUBLIC_API_BASE_URL` 指向已部署的 FastAPI 服务。

## 构建验证

提交前建议运行：

```bash
pnpm lint
pnpm check-types
pnpm build
```

当前仓库通过 Turborepo 同时调度 `web` 和 `api` 工作区。
