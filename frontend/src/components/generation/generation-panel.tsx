"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Select } from "@/components/ui/select";
import { Textarea } from "@/components/ui/input";
import { useGeneration, useProviders } from "@/hooks/use-generation";

interface GenerationPanelProps {
  contentItemId: string;
  contentType: string;
  onGenerationComplete?: (result: any) => void;
}

const CUSTOM_PROVIDER_STORAGE_KEY = "custom_provider_config";

const MODEL_OPTIONS: Record<string, { value: string; label: string }[]> = {
  openai: [
    { value: "gpt-4o", label: "GPT-4o (Recommended)" },
    { value: "gpt-4o-mini", label: "GPT-4o Mini (Faster/Cheaper)" },
    { value: "gpt-4-turbo", label: "GPT-4 Turbo" },
  ],
  anthropic: [
    { value: "claude-sonnet-4-20250514", label: "Claude 3.5 Sonnet (Recommended)" },
    { value: "claude-3-5-haiku-20241022", label: "Claude 3.5 Haiku (Faster)" },
    { value: "claude-3-opus-20240229", label: "Claude 3 Opus (Most Capable)" },
  ],
  google_gemini: [
    { value: "gemini-2.0-flash", label: "Gemini 2.0 Flash (Recommended)" },
    { value: "gemini-1.5-pro", label: "Gemini 1.5 Pro" },
    { value: "gemini-1.5-flash", label: "Gemini 1.5 Flash (Fastest)" },
  ],
  custom: [],
};

export function GenerationPanel({
  contentItemId,
  contentType,
  onGenerationComplete,
}: GenerationPanelProps) {
  const { loading, error, result, runGeneration, regenerate, reset } = useGeneration();
  const { providers, fetchProviders } = useProviders();

  const [provider, setProvider] = useState("openai");
  const [model, setModel] = useState("gpt-4o");
  const [temperature, setTemperature] = useState(0.7);
  const [maxTokens, setMaxTokens] = useState(4096);
  const [customInstructions, setCustomInstructions] = useState("");
  const [customEndpoint, setCustomEndpoint] = useState("");
  const [customApiKey, setCustomApiKey] = useState("");
  const [customModel, setCustomModel] = useState("");
  const [revisionNotes, setRevisionNotes] = useState("");
  const [isRegenMode, setIsRegenMode] = useState(false);
  const [defaultsLoaded, setDefaultsLoaded] = useState(false);

  useEffect(() => {
    fetchProviders();
    // Load defaults for this content type
    loadDefaults();
    loadCustomProviderConfig();
  }, []);

  const loadCustomProviderConfig = () => {
    try {
      const rawConfig = localStorage.getItem(CUSTOM_PROVIDER_STORAGE_KEY);
      if (!rawConfig) return;

      const config = JSON.parse(rawConfig);
      if (typeof config.endpoint === "string") setCustomEndpoint(config.endpoint);
      if (typeof config.apiKey === "string") setCustomApiKey(config.apiKey);
      if (typeof config.model === "string") setCustomModel(config.model);
    } catch {
      // Ignore malformed local config
    }
  };

  const persistCustomProviderConfig = (endpoint: string, apiKey: string, modelName: string) => {
    if (!endpoint.trim() || !apiKey.trim() || !modelName.trim()) return;
    localStorage.setItem(
      CUSTOM_PROVIDER_STORAGE_KEY,
      JSON.stringify({
        endpoint: endpoint.trim(),
        apiKey: apiKey.trim(),
        model: modelName.trim(),
      })
    );
  };

  const loadDefaults = async () => {
    if (defaultsLoaded) return;
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_URL || "/api/v1";
      const res = await fetch(`${apiBase}/generation/defaults/${contentType}`);
      if (res.ok) {
        const data = await res.json();
        if (data.provider) setProvider(data.provider);
        if (data.model) setModel(data.model);
        setDefaultsLoaded(true);
      }
    } catch (err) {
      // Silently fail - use hardcoded defaults
    }
  };

  // Update model when provider changes
  useEffect(() => {
    const models = MODEL_OPTIONS[provider];
    if (models && models.length > 0) {
      setModel(models[0].value);
    }
  }, [provider]);

  const handleGenerate = async () => {
    const selectedModel = provider === "custom" ? customModel.trim() : model;

    if (provider === "custom") {
      persistCustomProviderConfig(customEndpoint, customApiKey, selectedModel);
    }

    const request = {
      content_item_id: contentItemId,
      provider,
      model: selectedModel,
      temperature,
      max_tokens: maxTokens,
      custom_instructions: customInstructions || null,
      custom_endpoint: provider === "custom" ? customEndpoint.trim() || null : null,
      custom_api_key: provider === "custom" ? customApiKey.trim() || null : null,
    };

    let genResult;
    if (isRegenMode && revisionNotes) {
      genResult = await regenerate({
        ...request,
        revision_notes: revisionNotes,
      });
    } else {
      genResult = await runGeneration(request);
    }

    if (genResult?.success && onGenerationComplete) {
      onGenerationComplete(genResult);
    }
  };

  const availableProviders = providers
    .filter((p) => p.configured)
    .map((p) => ({ value: p.provider, label: p.provider.replace("_", " ").toUpperCase() }));

  if (providers.length > 0 && !availableProviders.find((p) => p.value === "custom")) {
    availableProviders.push({ value: "custom", label: "CUSTOM" });
  }

  const currentModels = MODEL_OPTIONS[provider] || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            {isRegenMode ? "Regenerate Content" : "Generate Content"}
          </h3>
          <div className="flex items-center gap-2">
            <button
              onClick={() => {
                setIsRegenMode(!isRegenMode);
                reset();
              }}
              className="text-xs text-primary-600 hover:text-primary-700 font-medium"
            >
              {isRegenMode ? "Switch to Generate" : "Switch to Regenerate"}
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Provider & Model Selection */}
        <div className="grid grid-cols-2 gap-4">
          <Select
            label="AI Provider"
            options={
              availableProviders.length > 0
                ? availableProviders
                : [
                    { value: "openai", label: "OpenAI" },
                    { value: "anthropic", label: "Anthropic" },
                    { value: "google_gemini", label: "Google Gemini" },
                    { value: "custom", label: "Custom" },
                  ]
            }
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
          />
          {provider === "custom" ? (
            <input
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              placeholder="Model (contoh: gpt-4o-mini)"
              value={customModel}
              onChange={(e) => setCustomModel(e.target.value)}
            />
          ) : (
            <Select
              label="Model"
              options={currentModels}
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          )}
        </div>

        {provider === "custom" && (
          <div className="grid grid-cols-1 gap-4">
            <input
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              placeholder="Custom Endpoint (contoh: https://api.openai.com/v1)"
              value={customEndpoint}
              onChange={(e) => setCustomEndpoint(e.target.value)}
            />
            <input
              type="password"
              className="block w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-primary-500 focus:ring-1 focus:ring-primary-500"
              placeholder="Custom API Key"
              value={customApiKey}
              onChange={(e) => setCustomApiKey(e.target.value)}
            />
          </div>
        )}

        {/* Advanced Settings */}
        <details className="group">
          <summary className="text-sm font-medium text-gray-600 cursor-pointer hover:text-gray-900">
            Advanced Settings
          </summary>
          <div className="mt-3 grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Temperature: {temperature}
              </label>
              <input
                type="range"
                min="0"
                max="1.5"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>Focused</span>
                <span>Creative</span>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max Tokens: {maxTokens}
              </label>
              <input
                type="range"
                min="1024"
                max="8192"
                step="512"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
              />
              <div className="flex justify-between text-xs text-gray-400 mt-1">
                <span>1K</span>
                <span>8K</span>
              </div>
            </div>
          </div>
        </details>

        {/* Custom Instructions */}
        <Textarea
          label="Instruksi Tambahan (opsional)"
          placeholder="Tambahkan instruksi spesifik untuk generation ini..."
          value={customInstructions}
          onChange={(e) => setCustomInstructions(e.target.value)}
          rows={2}
        />

        {/* Revision Notes (Regen mode) */}
        {isRegenMode && (
          <Textarea
            label="Catatan Revisi"
            placeholder="Jelaskan apa yang perlu diperbaiki dari versi sebelumnya..."
            value={revisionNotes}
            onChange={(e) => setRevisionNotes(e.target.value)}
            rows={3}
          />
        )}

        {/* Error Display */}
        {error && (
          <div className="p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-sm text-red-700">{error}</p>
          </div>
        )}

        {/* Success Metrics */}
        {result?.success && result.metrics && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <p className="text-sm font-medium text-green-800 mb-2">
              Generation berhasil! (Version {result.version_number})
            </p>
            <div className="grid grid-cols-4 gap-2 text-xs text-green-700">
              <div>
                <span className="font-medium">Provider:</span>{" "}
                {result.metrics.provider}
              </div>
              <div>
                <span className="font-medium">Latency:</span>{" "}
                {(result.metrics.latency_ms / 1000).toFixed(1)}s
              </div>
              <div>
                <span className="font-medium">Tokens:</span>{" "}
                {result.metrics.input_tokens + result.metrics.output_tokens}
              </div>
              <div>
                <span className="font-medium">Cost:</span> $
                {result.metrics.cost_usd.toFixed(4)}
              </div>
            </div>
          </div>
        )}

        {/* Parse Warning */}
        {result?.parse_warning && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <p className="text-sm text-yellow-700">{result.parse_warning}</p>
          </div>
        )}

        {/* Generate Button */}
        <Button
          onClick={handleGenerate}
          loading={loading}
          className="w-full"
          size="lg"
        >
          {loading
            ? "Generating..."
            : isRegenMode
            ? "Regenerate Content"
            : "Generate Content"}
        </Button>
      </CardContent>
    </Card>
  );
}
