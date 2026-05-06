import { Badge } from "@/components/ui/badge";

import { getApiBaseUrl } from "@/lib/api";

export function WorkspaceHeader() {
  return (
    <header className="flex flex-col gap-3 rounded-xl border bg-background p-4 md:flex-row md:items-center md:justify-between">
      <div className="flex flex-col gap-1">
        {/* <div className="flex flex-wrap items-center gap-2">
          <Badge variant="outline">MVP</Badge>
          <Badge variant="secondary">FastAPI</Badge>
          <Badge variant="secondary">PyMuPDF</Badge>
        </div> */}
        <h1 className="flex items-center gap-2 text-2xl font-semibold tracking-normal">
          AI 简历分析工作台
          <a
            href="https://github.com/Pretend724/AI-Resume-Analyzer"
            target="_blank"
            className="inline-flex"
          >
            <Badge
              variant="secondary"
              className="cursor-pointer transition-colors hover:bg-primary hover:text-primary-foreground"
            >
              Johnny Leon
            </Badge>
          </a>
        </h1>
        {/* <p className="text-sm text-muted-foreground">API: {getApiBaseUrl()}</p> */}
      </div>
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span className="inline-flex size-4 items-center justify-center">
          ✓
        </span>
        单份 PDF 简历分析
      </div>
    </header>
  );
}
