import { FileTextIcon, type LucideIcon } from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

import { valueOrEmpty } from "@/components/resume-analyzer/utils";

export function ResultSkeleton() {
  return (
    <div className="flex flex-col gap-3">
      <Skeleton className="h-8 w-1/2" />
      <Skeleton className="h-20 w-full" />
      <Skeleton className="h-24 w-full" />
    </div>
  );
}

export function EmptyState({
  title,
  description,
}: {
  title: string;
  description: string;
}) {
  return (
    <Alert>
      <FileTextIcon />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{description}</AlertDescription>
    </Alert>
  );
}

export function ProfileItem({
  icon: Icon,
  label,
  value,
}: {
  icon: LucideIcon;
  label: string;
  value: string;
}) {
  return (
    <div className="flex min-w-0 items-start gap-2 rounded-lg border bg-muted/20 p-3">
      <Icon className="mt-0.5 text-muted-foreground" />
      <div className="min-w-0">
        <div className="text-xs text-muted-foreground">{label}</div>
        <div className="break-words font-medium">{valueOrEmpty(value)}</div>
      </div>
    </div>
  );  
}

export function KeywordList({
  title,
  items,
  emptyText,
  variant = "secondary",
}: {
  title: string;
  items: string[];
  emptyText: string;
  variant?: "secondary" | "outline" | "destructive";
}) {
  return (
    <div className="flex flex-col gap-2">
      <div className="text-sm font-medium">{title}</div>
      <div className="flex flex-wrap gap-2">
        {items.length > 0 ? (
          items.map((item) => (
            <Badge key={item} variant={variant}>
              {item}
            </Badge>
          ))
        ) : (
          <span className="text-sm text-muted-foreground">{emptyText}</span>
        )}
      </div>
    </div>
  );
}
