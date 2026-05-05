"use client";

import { useState } from "react";
import { api } from "@/lib/api";

export interface AnalyticsOverview {
  content: {
    total: number;
    by_status: Record<string, number>;
    drafts: number;
    in_review: number;
    approved: number;
    scheduled: number;
    published: number;
    failed: number;
  };
  generation: {
    total_runs: number;
    completed: number;
    failed: number;
    avg_latency_ms: number;
    total_cost_usd: number;
    total_tokens: number;
  };
  publishing: {
    published: number;
    failed: number;
    queued: number;
  };
}

export interface ProviderUsage {
  providers: {
    provider: string;
    total_runs: number;
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
    total_cost_usd: number;
    avg_latency_ms: number;
  }[];
  models: {
    model: string;
    provider: string;
    runs: number;
    cost_usd: number;
    avg_latency_ms: number;
  }[];
  totals: {
    total_runs: number;
    total_cost_usd: number;
  };
}

export interface ActivityItem {
  type: "generation" | "publish";
  id: string;
  title: string;
  content_type: string;
  status: string;
  provider?: string;
  model?: string;
  cost_usd?: number;
  latency_ms?: number;
  platform_url?: string;
  error?: string;
  scheduled_at?: string;
  timestamp: string;
}

export function useAnalytics() {
  const [loading, setLoading] = useState(false);

  const getOverview = async (): Promise<AnalyticsOverview | null> => {
    setLoading(true);
    try {
      const response = await api.get<AnalyticsOverview>("/analytics/overview");
      return response.data;
    } catch (err) {
      return null;
    } finally {
      setLoading(false);
    }
  };

  const getProviderUsage = async (days?: number): Promise<ProviderUsage | null> => {
    try {
      const params: Record<string, string> = {};
      if (days) {
        const end = new Date();
        const start = new Date(end.getTime() - days * 86400000);
        params.start_date = start.toISOString().split("T")[0];
        params.end_date = end.toISOString().split("T")[0];
      }
      const response = await api.get<ProviderUsage>("/analytics/provider-usage", { params });
      return response.data;
    } catch (err) {
      return null;
    }
  };

  const getRecentActivity = async (limit = 20): Promise<ActivityItem[]> => {
    try {
      const response = await api.get<{ activities: ActivityItem[] }>("/analytics/recent-activity", {
        params: { limit },
      });
      return response.data.activities;
    } catch (err) {
      return [];
    }
  };

  const getContentStats = async () => {
    try {
      const response = await api.get("/analytics/content-stats");
      return response.data;
    } catch (err) {
      return null;
    }
  };

  const getPublishStats = async () => {
    try {
      const response = await api.get("/analytics/publish-stats");
      return response.data;
    } catch (err) {
      return null;
    }
  };

  return { loading, getOverview, getProviderUsage, getRecentActivity, getContentStats, getPublishStats };
}
