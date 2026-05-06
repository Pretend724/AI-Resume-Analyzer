import {
  BriefcaseBusinessIcon,
  MailIcon,
  MapPinIcon,
  PhoneIcon,
  UserRoundIcon,
} from "lucide-react";

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";

import {
  extractionSourceText,
  valueOrEmpty,
} from "@/components/resume-analyzer/utils";
import { EmptyState, ProfileItem } from "@/components/resume-analyzer/shared";

import type { ResumeAnalyzeResponse } from "@/lib/api";

export function ResumeProfileCard({
  analysis,
  isAnalyzing,
}: {
  analysis: ResumeAnalyzeResponse | null;
  isAnalyzing: boolean;
}) {
  const profile = analysis?.profile;

  return (
    <Card>
      <CardHeader>
        <CardTitle>关键信息</CardTitle>
        <CardDescription>
          {analysis
            ? extractionSourceText[analysis.profile_extraction.source]
            : "等待解析"}
        </CardDescription>
      </CardHeader>
      <CardContent>
        {isAnalyzing ? (
          <EmptyState
            title="解析中"
            description="请稍候，正在提取简历关键信息。"
          />
        ) : profile ? (
          <div className="flex flex-col gap-4">
            <div className="grid gap-3 sm:grid-cols-2">
              <ProfileItem
                icon={UserRoundIcon}
                label="姓名"
                value={profile.basic_info.name}
              />
              <ProfileItem
                icon={PhoneIcon}
                label="电话"
                value={profile.basic_info.phone}
              />
              <ProfileItem
                icon={MailIcon}
                label="邮箱"
                value={profile.basic_info.email}
              />
              <ProfileItem
                icon={MapPinIcon}
                label="地址"
                value={profile.basic_info.address}
              />
            </div>

            <Separator />

            <div className="grid gap-3 sm:grid-cols-3">
              <div className="rounded-lg border bg-muted/20 p-3">
                <div className="text-xs text-muted-foreground">求职意向</div>
                <div className="mt-1 font-medium">
                  {valueOrEmpty(profile.job_intention.desired_position)}
                </div>
              </div>
              <div className="rounded-lg border bg-muted/20 p-3">
                <div className="text-xs text-muted-foreground">期望薪资</div>
                <div className="mt-1 font-medium">
                  {valueOrEmpty(profile.job_intention.expected_salary)}
                </div>
              </div>
              <div className="rounded-lg border bg-muted/20 p-3">
                <div className="text-xs text-muted-foreground">工作年限</div>
                <div className="mt-1 font-medium">
                  {valueOrEmpty(profile.background.years_of_experience)}
                </div>
              </div>
            </div>

            {analysis.profile_extraction.warnings.length > 0 ? (
              <Alert>
                <BriefcaseBusinessIcon />
                <AlertTitle>提取提示</AlertTitle>
                <AlertDescription>
                  {analysis.profile_extraction.warnings.join("；")}
                </AlertDescription>
              </Alert>
            ) : null}
          </div>
        ) : (
          <EmptyState
            title="暂无简历信息"
            description="上传 PDF 后会展示基础信息、求职信息和背景信息。"
          />
        )}
      </CardContent>
    </Card>
  );
}
