// Core types matching backend models

export type ContentType =
  | "youtube_shorts"
  | "youtube_longform"
  | "tiktok_short"
  | "blog_article"
  | "x_post";

export type ContentStatus =
  | "draft"
  | "in_review"
  | "approved"
  | "scheduled"
  | "publishing"
  | "published"
  | "failed"
  | "archived";

export type CampaignStatus =
  | "planning"
  | "active"
  | "paused"
  | "completed"
  | "archived";

export type AIProvider = "openai" | "anthropic" | "google_gemini" | "local";

export type PlatformType = "youtube" | "tiktok" | "x" | "blog";

export interface User {
  id: string;
  username: string;
  is_active: boolean;
  last_login: string | null;
  created_at: string;
}

export interface Brand {
  id: string;
  name: string;
  description: string | null;
  niche: string | null;
  target_audience: string | null;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: string;
  brand_id: string;
  name: string;
  description: string | null;
  objective: string | null;
  status: CampaignStatus;
  start_date: string | null;
  end_date: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContentItem {
  id: string;
  campaign_id: string;
  title: string;
  content_type: ContentType;
  status: ContentStatus;
  language: "id" | "en";
  brief: Record<string, unknown> | null;
  current_version: number;
  scheduled_at: string | null;
  published_at: string | null;
  tags: string[] | null;
  created_at: string;
  updated_at: string;
}

export interface ContentVersion {
  id: string;
  content_item_id: string;
  version_number: number;
  content_data: Record<string, unknown>;
  generation_run_id: string | null;
  approved_at: string | null;
  approval_notes: string | null;
  revision_notes: string | null;
  created_at: string;
}

export interface GenerationRun {
  id: string;
  content_item_id: string;
  provider: AIProvider;
  model: string;
  status: "pending" | "running" | "completed" | "failed";
  input_tokens: number | null;
  output_tokens: number | null;
  latency_ms: number | null;
  cost_usd: number | null;
  error_message: string | null;
  created_at: string;
}

export interface StyleGuide {
  id: string;
  brand_id: string | null;
  campaign_id: string | null;
  name: string;
  is_active: boolean;
  tone_of_voice: string | null;
  writing_rules: string[] | null;
  preferred_phrases: string[] | null;
  banned_phrases: string[] | null;
  brand_examples: Record<string, unknown>[] | null;
  additional_notes: string | null;
}

export interface CTAPattern {
  id: string;
  brand_id: string | null;
  campaign_id: string | null;
  name: string;
  is_active: boolean;
  cta_text: string;
  cta_type: string | null;
  placement: string | null;
  platform_target: string | null;
}

export interface PlatformAccount {
  id: string;
  brand_id: string;
  platform: PlatformType;
  account_name: string;
  account_id: string | null;
  is_connected: boolean;
  is_active: boolean;
  connected_at: string | null;
}

export interface PublishJob {
  id: string;
  content_item_id: string;
  platform_account_id: string;
  status: string;
  scheduled_publish_at: string | null;
  platform_post_id: string | null;
  platform_url: string | null;
  error_message: string | null;
  retry_count: number;
  created_at: string;
}

export interface AnalyticsOverview {
  total_drafts: number;
  total_in_review: number;
  total_approved: number;
  total_scheduled: number;
  total_published: number;
  total_failed: number;
  generation_runs_count: number;
  avg_generation_latency_ms: number | null;
  total_tokens_used: number;
  total_cost_usd: number;
}
