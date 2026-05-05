"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import {
  useAnalytics,
  type AnalyticsOverview,
  type ProviderUsage,
  type ActivityItem,
} from "@/hooks/use-analytics";
import { getContentTypeLabel, formatDateTime } from "@/lib/utils";

export default function AnalyticsPage() {
  const { loading, getOverview, getProviderUsage, getRecentActivity } = useAnalytics();

  const [overview, setOverview] = useState<AnalyticsOverview | null>(null);
  const [providerUsage, setProviderUsage] = useState<ProviderUsage | null>(null);
  const [activities, setActivities] = useState<ActivityItem[]>([]);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    const [overviewData, providerData, activityData] = await Promise.all([
      getOverview(),
      getProviderUsage(30),
      getRecentActivity(15),
    ]);
    setOverview(overviewData);
    setProviderUsage(providerData);
    setActivities(activityData);
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Analytics</h1>
        <p className="text-sm text-gray-500 mt-1">
          Operational metrics dan performa content production
        </p>
      </div>

      {/* Top Stats */}
      {overview && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-8">
          <StatCard
            label="Total Content"
            value={overview.content.total}
            color="gray"
          />
          <StatCard
            label="Published"
            value={overview.content.published}
            color="green"
          />
          <StatCard
            label="Scheduled"
            value={overview.content.scheduled}
            color="blue"
          />
          <StatCard
            label="Generation Runs"
            value={overview.generation.total_runs}
            color="purple"
          />
          <StatCard
            label="Total Cost"
            value={`$${overview.generation.total_cost_usd.toFixed(2)}`}
            color="orange"
            isText
          />
          <StatCard
            label="Avg Latency"
            value={`${(overview.generation.avg_latency_ms / 1000).toFixed(1)}s`}
            color="cyan"
            isText
          />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content Pipeline */}
          {overview && <ContentPipeline data={overview.content} />}

          {/* Provider Usage */}
          {providerUsage && <ProviderUsageCard data={providerUsage} />}

          {/* Model Breakdown */}
          {providerUsage && providerUsage.models.length > 0 && (
            <ModelBreakdown models={providerUsage.models} />
          )}
        </div>

        {/* Right Column (1/3) */}
        <div className="space-y-6">
          {/* Publishing Stats */}
          {overview && <PublishingStats data={overview.publishing} />}

          {/* Recent Activity */}
          <RecentActivityFeed activities={activities} />
        </div>
      </div>
    </DashboardLayout>
  );
}

// =============================================================================
// Components
// =============================================================================

function StatCard({
  label,
  value,
  color,
  isText = false,
}: {
  label: string;
  value: number | string;
  color: string;
  isText?: boolean;
}) {
  const bgColors: Record<string, string> = {
    gray: "bg-gray-50 border-gray-200",
    green: "bg-green-50 border-green-200",
    blue: "bg-blue-50 border-blue-200",
    purple: "bg-purple-50 border-purple-200",
    orange: "bg-orange-50 border-orange-200",
    cyan: "bg-cyan-50 border-cyan-200",
  };

  return (
    <div className={`rounded-xl border p-4 ${bgColors[color] || bgColors.gray}`}>
      <p className="text-xs text-gray-600 font-medium">{label}</p>
      <p className={`mt-1 font-bold ${isText ? "text-lg" : "text-2xl"} text-gray-900`}>
        {value}
      </p>
    </div>
  );
}

function ContentPipeline({ data }: { data: AnalyticsOverview["content"] }) {
  const stages = [
    { label: "Draft", count: data.drafts, color: "bg-gray-400" },
    { label: "In Review", count: data.in_review, color: "bg-yellow-400" },
    { label: "Approved", count: data.approved, color: "bg-green-400" },
    { label: "Scheduled", count: data.scheduled, color: "bg-blue-400" },
    { label: "Published", count: data.published, color: "bg-emerald-500" },
    { label: "Failed", count: data.failed, color: "bg-red-400" },
  ];

  const maxCount = Math.max(...stages.map((s) => s.count), 1);

  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900">Content Pipeline</h3>
        <p className="text-sm text-gray-500">Status distribution semua content</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {stages.map((stage) => (
            <div key={stage.label} className="flex items-center gap-3">
              <span className="text-sm text-gray-600 w-24 text-right">{stage.label}</span>
              <div className="flex-1 h-8 bg-gray-100 rounded-lg overflow-hidden relative">
                <div
                  className={`h-full ${stage.color} rounded-lg transition-all duration-500`}
                  style={{ width: `${(stage.count / maxCount) * 100}%`, minWidth: stage.count > 0 ? "24px" : "0" }}
                />
                {stage.count > 0 && (
                  <span className="absolute inset-y-0 left-2 flex items-center text-xs font-medium text-white mix-blend-difference">
                    {stage.count}
                  </span>
                )}
              </div>
              <span className="text-sm font-medium text-gray-900 w-8 text-right">
                {stage.count}
              </span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function ProviderUsageCard({ data }: { data: ProviderUsage }) {
  const providerColors: Record<string, string> = {
    openai: "bg-green-100 text-green-800",
    anthropic: "bg-orange-100 text-orange-800",
    google_gemini: "bg-blue-100 text-blue-800",
    local: "bg-gray-100 text-gray-800",
  };

  const providerLabels: Record<string, string> = {
    openai: "OpenAI",
    anthropic: "Anthropic",
    google_gemini: "Google Gemini",
    local: "Local",
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Provider Usage</h3>
            <p className="text-sm text-gray-500">Last 30 days</p>
          </div>
          <div className="text-right">
            <p className="text-sm text-gray-500">Total Cost</p>
            <p className="text-lg font-bold text-gray-900">
              ${data.totals.total_cost_usd.toFixed(2)}
            </p>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {data.providers.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">
            Belum ada data generation
          </p>
        ) : (
          <div className="space-y-4">
            {data.providers.map((provider) => (
              <div key={provider.provider} className="p-4 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <Badge className={providerColors[provider.provider]}>
                      {providerLabels[provider.provider] || provider.provider}
                    </Badge>
                    <span className="text-sm text-gray-500">
                      {provider.total_runs} runs
                    </span>
                  </div>
                  <span className="text-sm font-semibold text-gray-900">
                    ${provider.total_cost_usd.toFixed(4)}
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-4 text-xs">
                  <div>
                    <p className="text-gray-500">Tokens</p>
                    <p className="font-medium text-gray-700">
                      {(provider.total_tokens / 1000).toFixed(1)}K
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Avg Latency</p>
                    <p className="font-medium text-gray-700">
                      {(provider.avg_latency_ms / 1000).toFixed(1)}s
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-500">Cost/Run</p>
                    <p className="font-medium text-gray-700">
                      ${(provider.total_cost_usd / provider.total_runs).toFixed(4)}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

function ModelBreakdown({ models }: { models: ProviderUsage["models"] }) {
  return (
    <Card>
      <CardHeader>
        <h3 className="text-lg font-semibold text-gray-900">Model Breakdown</h3>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-2 text-gray-500 font-medium">Model</th>
                <th className="text-right py-2 text-gray-500 font-medium">Runs</th>
                <th className="text-right py-2 text-gray-500 font-medium">Cost</th>
                <th className="text-right py-2 text-gray-500 font-medium">Avg Latency</th>
              </tr>
            </thead>
            <tbody>
              {models.map((m, i) => (
                <tr key={i} className="border-b border-gray-50">
                  <td className="py-2">
                    <span className="font-medium text-gray-900">{m.model}</span>
                    <span className="text-xs text-gray-400 ml-2">{m.provider}</span>
                  </td>
                  <td className="text-right py-2 text-gray-700">{m.runs}</td>
                  <td className="text-right py-2 text-gray-700">${m.cost_usd.toFixed(4)}</td>
                  <td className="text-right py-2 text-gray-700">
                    {(m.avg_latency_ms / 1000).toFixed(1)}s
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
}

function PublishingStats({ data }: { data: AnalyticsOverview["publishing"] }) {
  const total = data.published + data.failed + data.queued;
  const successRate = total > 0 ? ((data.published / (data.published + data.failed)) * 100) : 0;

  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-gray-900">Publishing</h3>
      </CardHeader>
      <CardContent className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Published</span>
          <span className="text-sm font-medium text-green-700">{data.published}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Failed</span>
          <span className="text-sm font-medium text-red-700">{data.failed}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">Queued</span>
          <span className="text-sm font-medium text-blue-700">{data.queued}</span>
        </div>
        <div className="border-t border-gray-100 pt-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Success Rate</span>
            <span className="text-sm font-bold text-gray-900">
              {successRate.toFixed(0)}%
            </span>
          </div>
          {/* Progress bar */}
          <div className="mt-2 h-2 bg-gray-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full"
              style={{ width: `${successRate}%` }}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

function RecentActivityFeed({ activities }: { activities: ActivityItem[] }) {
  const statusIcons: Record<string, { icon: string; color: string }> = {
    completed: { icon: "✓", color: "text-green-600 bg-green-100" },
    failed: { icon: "✗", color: "text-red-600 bg-red-100" },
    running: { icon: "⟳", color: "text-yellow-600 bg-yellow-100" },
    published: { icon: "▶", color: "text-emerald-600 bg-emerald-100" },
    queued: { icon: "◷", color: "text-blue-600 bg-blue-100" },
    processing: { icon: "⚙", color: "text-indigo-600 bg-indigo-100" },
    scheduled: { icon: "📅", color: "text-blue-600 bg-blue-100" },
  };

  return (
    <Card>
      <CardHeader>
        <h3 className="text-sm font-semibold text-gray-900">Recent Activity</h3>
      </CardHeader>
      <CardContent>
        {activities.length === 0 ? (
          <p className="text-sm text-gray-400 text-center py-4">No recent activity</p>
        ) : (
          <div className="space-y-3">
            {activities.map((activity) => {
              const statusInfo = statusIcons[activity.status] || {
                icon: "•",
                color: "text-gray-600 bg-gray-100",
              };
              return (
                <div key={`${activity.type}-${activity.id}`} className="flex items-start gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0 mt-0.5 ${statusInfo.color}`}
                  >
                    {statusInfo.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-900 truncate">{activity.title}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs text-gray-500 capitalize">
                        {activity.type}
                      </span>
                      {activity.provider && (
                        <span className="text-xs text-gray-400">{activity.provider}</span>
                      )}
                      {activity.cost_usd != null && activity.cost_usd > 0 && (
                        <span className="text-xs text-gray-400">
                          ${activity.cost_usd.toFixed(4)}
                        </span>
                      )}
                      <span className="text-xs text-gray-300">
                        {formatDateTime(activity.timestamp)}
                      </span>
                    </div>
                    {activity.error && (
                      <p className="text-xs text-red-500 mt-0.5 truncate">{activity.error}</p>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
