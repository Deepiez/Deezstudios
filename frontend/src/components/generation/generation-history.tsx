"use client";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { formatDateTime } from "@/lib/utils";
import type { GenerationRun } from "@/types";

interface GenerationHistoryProps {
  runs: GenerationRun[];
  onRetry?: (runId: string) => void;
}

export function GenerationHistory({ runs, onRetry }: GenerationHistoryProps) {
  if (runs.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Generation History</h3>
          <span className="text-xs text-gray-500">{runs.length} runs</span>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {runs.map((run) => (
            <GenerationRunItem key={run.id} run={run} onRetry={onRetry} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

function GenerationRunItem({
  run,
  onRetry,
}: {
  run: GenerationRun;
  onRetry?: (runId: string) => void;
}) {
  const statusColors: Record<string, string> = {
    completed: "bg-green-500",
    failed: "bg-red-500",
    running: "bg-yellow-500 animate-pulse",
    pending: "bg-gray-400",
  };

  const providerLabels: Record<string, string> = {
    openai: "OpenAI",
    anthropic: "Anthropic",
    google_gemini: "Gemini",
  };

  return (
    <div className="flex items-center justify-between py-3 px-4 bg-gray-50 rounded-lg">
      <div className="flex items-center gap-3">
        {/* Status dot */}
        <div className={`w-2.5 h-2.5 rounded-full ${statusColors[run.status] || "bg-gray-400"}`} />

        {/* Provider & Model */}
        <div>
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-gray-900">
              {providerLabels[run.provider] || run.provider}
            </span>
            <span className="text-xs text-gray-500">{run.model}</span>
          </div>
          <span className="text-xs text-gray-400">{formatDateTime(run.created_at)}</span>
        </div>
      </div>

      {/* Metrics */}
      <div className="flex items-center gap-4">
        {run.status === "completed" && (
          <>
            {run.latency_ms && (
              <div className="text-right">
                <p className="text-xs text-gray-500">Latency</p>
                <p className="text-sm font-medium text-gray-700">
                  {(run.latency_ms / 1000).toFixed(1)}s
                </p>
              </div>
            )}
            {run.input_tokens != null && run.output_tokens != null && (
              <div className="text-right">
                <p className="text-xs text-gray-500">Tokens</p>
                <p className="text-sm font-medium text-gray-700">
                  {run.input_tokens + run.output_tokens}
                </p>
              </div>
            )}
            {run.cost_usd != null && (
              <div className="text-right">
                <p className="text-xs text-gray-500">Cost</p>
                <p className="text-sm font-medium text-gray-700">
                  ${run.cost_usd.toFixed(4)}
                </p>
              </div>
            )}
          </>
        )}

        {run.status === "failed" && (
          <div className="flex items-center gap-2">
            <Badge variant="error">Failed</Badge>
            {onRetry && (
              <Button size="sm" variant="outline" onClick={() => onRetry(run.id)}>
                Retry
              </Button>
            )}
          </div>
        )}

        {run.status === "running" && <Badge variant="warning">Running...</Badge>}
      </div>
    </div>
  );
}
