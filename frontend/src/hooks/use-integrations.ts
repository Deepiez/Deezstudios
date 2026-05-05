"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { PlatformAccount } from "@/types";

interface YouTubeStatus {
  configured: boolean;
  connected_accounts: {
    id: string;
    account_name: string;
    channel_id: string;
    is_connected: boolean;
    connected_at: string | null;
  }[];
  total_connected: number;
}

interface ChannelInfo {
  channel_id: string;
  title: string;
  description: string;
  thumbnail: string | null;
  subscriber_count: string | null;
  video_count: string | null;
}

export function useIntegrations() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Platform accounts
  const fetchAccounts = async (brandId?: string): Promise<PlatformAccount[]> => {
    try {
      const params = brandId ? { brand_id: brandId } : {};
      const response = await api.get("/integrations/accounts", { params });
      return response.data;
    } catch (err) {
      return [];
    }
  };

  // YouTube
  const getYouTubeStatus = async (): Promise<YouTubeStatus | null> => {
    try {
      const response = await api.get<YouTubeStatus>("/integrations/youtube/status");
      return response.data;
    } catch (err) {
      return null;
    }
  };

  const connectYouTube = async (brandId: string): Promise<string | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get<{ auth_url: string }>("/integrations/youtube/connect", {
        params: { brand_id: brandId },
      });
      return response.data.auth_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to initiate YouTube connection");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const disconnectYouTube = async (accountId: string): Promise<boolean> => {
    setLoading(true);
    try {
      await api.post(`/integrations/youtube/disconnect/${accountId}`);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to disconnect");
      return false;
    } finally {
      setLoading(false);
    }
  };

  const getChannelInfo = async (accountId: string): Promise<ChannelInfo | null> => {
    try {
      const response = await api.get<ChannelInfo>(`/integrations/youtube/channel/${accountId}`);
      return response.data;
    } catch (err) {
      return null;
    }
  };

  return {
    loading,
    error,
    fetchAccounts,
    getYouTubeStatus,
    connectYouTube,
    disconnectYouTube,
    getChannelInfo,
  };
}
