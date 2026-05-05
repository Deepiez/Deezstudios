"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { GenerationRun } from "@/types";

interface GenerationRequest {
  content_item_id: string;
  provider: string;
  model: string;
  temperature?: number;
  max_tokens?: number;
  fallback_provider?: string | null;
  custom_instructions?: string | null;
}

interface RegenerationRequest extends GenerationRequest {
  revision_notes?: string | null;
}

interface GenerationResult {
  success: boolean;
  generation_run_id: string;
  content_version_id?: string;
  version_number?: number;
  content_data?: Record<string, unknown>;
  parse_warning?: string;
  metrics?: {
    provider: string;
    model: string;
    input_tokens: number;
    output_tokens: number;
    latency_ms: number;
    cost_usd: number;
  };
  error?: string;
}

interface ProviderInfo {
  provider: string;
  configured: boolean;
  models: string[];
}

export function useGeneration() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResult | null>(null);

  const runGeneration = async (request: GenerationRequest): Promise<GenerationResult | null> => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post<GenerationResult>("/generation/run", request);
      setResult(response.data);
      if (!response.data.success) {
        setError(response.data.error || "Generation failed");
      }
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || "Generation request failed";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const regenerate = async (request: RegenerationRequest): Promise<GenerationResult | null> => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post<GenerationResult>("/generation/regenerate", request);
      setResult(response.data);
      if (!response.data.success) {
        setError(response.data.error || "Regeneration failed");
      }
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || "Regeneration request failed";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const retryRun = async (runId: string): Promise<GenerationResult | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await api.post<GenerationResult>(`/generation/runs/${runId}/retry`);
      setResult(response.data);
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || "Retry failed";
      setError(message);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setLoading(false);
    setError(null);
    setResult(null);
  };

  return { loading, error, result, runGeneration, regenerate, retryRun, reset };
}

export function useProviders() {
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchProviders = async () => {
    setLoading(true);
    try {
      const response = await api.get<{ providers: ProviderInfo[]; available_count: number }>(
        "/generation/providers"
      );
      setProviders(response.data.providers);
    } catch (err) {
      console.error("Failed to fetch providers:", err);
    } finally {
      setLoading(false);
    }
  };

  return { providers, loading, fetchProviders };
}

export function useGenerationRuns(contentItemId?: string) {
  const [runs, setRuns] = useState<GenerationRun[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchRuns = async () => {
    setLoading(true);
    try {
      const params = contentItemId ? { content_item_id: contentItemId } : {};
      const response = await api.get<GenerationRun[]>("/generation/runs", { params });
      setRuns(response.data);
    } catch (err) {
      console.error("Failed to fetch runs:", err);
    } finally {
      setLoading(false);
    }
  };

  return { runs, loading, fetchRuns };
}
