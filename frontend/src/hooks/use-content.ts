"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ContentItem, ContentVersion } from "@/types";

interface CreateContentRequest {
  campaign_id: string;
  title: string;
  content_type: string;
  language: string;
  brief: {
    topic: string;
    audience: string;
    objective: string;
    key_message: string;
    tone: string;
    language: string;
    references?: string;
    target_duration?: string;
    target_word_count?: string;
    additional_context?: string;
  };
  tags?: string[];
}

export function useContent() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const createContent = async (data: CreateContentRequest): Promise<ContentItem | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post<ContentItem>("/content/", data);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to create content");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const getContent = async (id: string): Promise<ContentItem | null> => {
    try {
      const response = await api.get<ContentItem>(`/content/${id}`);
      return response.data;
    } catch (err) {
      return null;
    }
  };

  const listContent = async (params?: Record<string, string>): Promise<ContentItem[]> => {
    try {
      const response = await api.get<ContentItem[]>("/content/", { params });
      return response.data;
    } catch (err) {
      return [];
    }
  };

  const submitForReview = async (id: string): Promise<ContentItem | null> => {
    setLoading(true);
    try {
      const response = await api.post<ContentItem>(`/content/${id}/submit-review`);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to submit for review");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const approveContent = async (id: string, notes?: string): Promise<ContentItem | null> => {
    setLoading(true);
    try {
      const response = await api.post<ContentItem>(`/content/${id}/approve`, null, {
        params: { approval_notes: notes },
      });
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to approve");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const rejectContent = async (id: string, notes: string): Promise<ContentItem | null> => {
    setLoading(true);
    try {
      const response = await api.post<ContentItem>(`/content/${id}/reject`, null, {
        params: { revision_notes: notes },
      });
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to reject");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const getVersions = async (contentId: string): Promise<ContentVersion[]> => {
    try {
      const response = await api.get<ContentVersion[]>(`/content/${contentId}/versions`);
      return response.data;
    } catch (err) {
      return [];
    }
  };

  return {
    loading,
    error,
    createContent,
    getContent,
    listContent,
    submitForReview,
    approveContent,
    rejectContent,
    getVersions,
  };
}
