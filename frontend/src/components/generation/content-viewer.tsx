"use client";

import { useState } from "react";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ContentVersion } from "@/types";

interface ContentViewerProps {
  versions: ContentVersion[];
  contentType: string;
  currentVersion: number;
}

export function ContentViewer({ versions, contentType, currentVersion }: ContentViewerProps) {
  const [selectedVersion, setSelectedVersion] = useState<number>(currentVersion);

  const version = versions.find((v) => v.version_number === selectedVersion);
  const data = version?.content_data;

  if (!version || !data) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-gray-500">
            Belum ada content version. Jalankan generation untuk membuat versi pertama.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Content Output</h3>
          {/* Version Selector */}
          <div className="flex items-center gap-2">
            {versions.map((v) => (
              <button
                key={v.version_number}
                onClick={() => setSelectedVersion(v.version_number)}
                className={`px-3 py-1 text-xs font-medium rounded-full transition-colors ${
                  selectedVersion === v.version_number
                    ? "bg-primary-100 text-primary-700"
                    : "bg-gray-100 text-gray-600 hover:bg-gray-200"
                }`}
              >
                v{v.version_number}
                {v.approved_at && " ✓"}
              </button>
            ))}
          </div>
        </div>
        {version.approved_at && (
          <Badge variant="success">Approved</Badge>
        )}
      </CardHeader>

      <CardContent>
        {/* Render based on content type */}
        {contentType === "youtube_shorts" && <YouTubeShortsView data={data} />}
        {contentType === "youtube_longform" && <YouTubeLongformView data={data} />}
        {contentType === "tiktok_short" && <TikTokView data={data} />}
        {contentType === "blog_article" && <BlogView data={data} />}
        {contentType === "x_post" && <XPostView data={data} />}
      </CardContent>
    </Card>
  );
}

// =============================================================================
// Content Type Specific Views
// =============================================================================

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h4 className="text-sm font-semibold text-gray-700 mb-2 mt-4 first:mt-0">{children}</h4>;
}

function TextBlock({ text, className = "" }: { text: string; className?: string }) {
  return (
    <div className={`bg-gray-50 rounded-lg p-3 text-sm text-gray-800 whitespace-pre-wrap ${className}`}>
      {text}
    </div>
  );
}

function OptionsList({ items, label }: { items: string[]; label: string }) {
  if (!items || items.length === 0) return null;
  return (
    <div>
      <SectionTitle>{label}</SectionTitle>
      <div className="space-y-2">
        {items.map((item, i) => (
          <div key={i} className="flex items-start gap-2">
            <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded mt-0.5">
              {i + 1}
            </span>
            <p className="text-sm text-gray-800">{item}</p>
          </div>
        ))}
      </div>
    </div>
  );
}

function YouTubeShortsView({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-4">
      <OptionsList items={data.titles} label="Title Options" />
      <OptionsList items={data.hooks} label="Hook Options" />

      {data.script && (
        <div>
          <SectionTitle>Script</SectionTitle>
          <div className="space-y-2">
            <div className="border-l-4 border-yellow-400 pl-3">
              <p className="text-xs font-medium text-yellow-700 mb-1">HOOK (3 detik pertama)</p>
              <p className="text-sm text-gray-800">{data.script.hook}</p>
            </div>
            <div className="border-l-4 border-blue-400 pl-3">
              <p className="text-xs font-medium text-blue-700 mb-1">BODY</p>
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{data.script.body}</p>
            </div>
            <div className="border-l-4 border-green-400 pl-3">
              <p className="text-xs font-medium text-green-700 mb-1">CLOSING</p>
              <p className="text-sm text-gray-800">{data.script.closing}</p>
            </div>
          </div>
        </div>
      )}

      {data.description_draft && (
        <div>
          <SectionTitle>Description Draft</SectionTitle>
          <TextBlock text={data.description_draft} />
        </div>
      )}

      {data.thumbnail_prompt && (
        <div>
          <SectionTitle>Thumbnail Prompt</SectionTitle>
          <TextBlock text={data.thumbnail_prompt} className="bg-purple-50 text-purple-800" />
        </div>
      )}

      {data.tags && (
        <div>
          <SectionTitle>Tags</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {data.tags.map((tag: string, i: number) => (
              <Badge key={i}>{tag}</Badge>
            ))}
          </div>
        </div>
      )}

      {data.visual_notes && (
        <div>
          <SectionTitle>Visual Notes</SectionTitle>
          <TextBlock text={data.visual_notes} className="bg-indigo-50 text-indigo-800" />
        </div>
      )}
    </div>
  );
}

function YouTubeLongformView({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-4">
      <OptionsList items={data.titles} label="Title Options" />
      <OptionsList items={data.hooks} label="Hook Options" />

      {data.outline && (
        <div>
          <SectionTitle>Outline</SectionTitle>
          <div className="space-y-3">
            {data.outline.map((section: any, i: number) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-sm font-medium text-gray-900">{section.section}</p>
                  {section.duration_minutes && (
                    <span className="text-xs text-gray-500">{section.duration_minutes} min</span>
                  )}
                </div>
                {section.key_points && (
                  <ul className="list-disc list-inside text-xs text-gray-600 space-y-0.5">
                    {section.key_points.map((point: string, j: number) => (
                      <li key={j}>{point}</li>
                    ))}
                  </ul>
                )}
                {section.retention_hook && (
                  <p className="text-xs text-primary-600 mt-1 italic">
                    Retention: {section.retention_hook}
                  </p>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {data.full_script && (
        <div>
          <SectionTitle>Full Script</SectionTitle>
          <TextBlock text={data.full_script} />
        </div>
      )}

      {data.description_draft && (
        <div>
          <SectionTitle>Description</SectionTitle>
          <TextBlock text={data.description_draft} />
        </div>
      )}

      {data.thumbnail_prompt && (
        <div>
          <SectionTitle>Thumbnail Prompt</SectionTitle>
          <TextBlock text={data.thumbnail_prompt} className="bg-purple-50 text-purple-800" />
        </div>
      )}
    </div>
  );
}

function TikTokView({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-4">
      <OptionsList items={data.hooks} label="Hook Options" />

      {data.script && (
        <div>
          <SectionTitle>Script</SectionTitle>
          <div className="space-y-2">
            <div className="border-l-4 border-pink-400 pl-3">
              <p className="text-xs font-medium text-pink-700 mb-1">HOOK (1-2 detik)</p>
              <p className="text-sm text-gray-800">{data.script.hook}</p>
            </div>
            <div className="border-l-4 border-blue-400 pl-3">
              <p className="text-xs font-medium text-blue-700 mb-1">BODY</p>
              <p className="text-sm text-gray-800 whitespace-pre-wrap">{data.script.body}</p>
            </div>
            <div className="border-l-4 border-green-400 pl-3">
              <p className="text-xs font-medium text-green-700 mb-1">CLOSING</p>
              <p className="text-sm text-gray-800">{data.script.closing}</p>
            </div>
          </div>
        </div>
      )}

      {data.caption && (
        <div>
          <SectionTitle>Caption</SectionTitle>
          <TextBlock text={data.caption} />
        </div>
      )}

      {data.visual_cues && (
        <div>
          <SectionTitle>Visual Cues</SectionTitle>
          <div className="space-y-2">
            {data.visual_cues.map((cue: any, i: number) => (
              <div key={i} className="flex items-start gap-3 bg-indigo-50 rounded-lg p-2">
                <span className="text-xs font-mono font-medium text-indigo-600 whitespace-nowrap">
                  {cue.timestamp}
                </span>
                <p className="text-sm text-gray-800">{cue.action}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.sound_suggestion && (
        <div>
          <SectionTitle>Sound Suggestion</SectionTitle>
          <TextBlock text={data.sound_suggestion} />
        </div>
      )}
    </div>
  );
}

function BlogView({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-4">
      <OptionsList items={data.titles} label="Title Options" />

      {data.meta_description && (
        <div>
          <SectionTitle>Meta Description</SectionTitle>
          <TextBlock text={data.meta_description} className="bg-green-50 text-green-800" />
        </div>
      )}

      {data.outline && (
        <div>
          <SectionTitle>Outline</SectionTitle>
          <div className="space-y-2">
            {data.outline.map((section: any, i: number) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3">
                <p className="text-sm font-medium text-gray-900">{section.heading}</p>
                {section.subheadings && (
                  <ul className="list-disc list-inside text-xs text-gray-600 mt-1">
                    {section.subheadings.map((sub: string, j: number) => (
                      <li key={j}>{sub}</li>
                    ))}
                  </ul>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {data.article_body && (
        <div>
          <SectionTitle>Article Body</SectionTitle>
          <div className="prose prose-sm max-w-none bg-white border border-gray-200 rounded-lg p-4">
            <div className="whitespace-pre-wrap text-sm text-gray-800">
              {data.article_body}
            </div>
          </div>
        </div>
      )}

      {data.cta_placement && (
        <div>
          <SectionTitle>CTA Placement</SectionTitle>
          <div className="space-y-2">
            {data.cta_placement.mid_article_cta && (
              <TextBlock text={`Mid: ${data.cta_placement.mid_article_cta}`} className="bg-orange-50 text-orange-800" />
            )}
            {data.cta_placement.end_article_cta && (
              <TextBlock text={`End: ${data.cta_placement.end_article_cta}`} className="bg-orange-50 text-orange-800" />
            )}
          </div>
        </div>
      )}

      {data.target_keywords && (
        <div>
          <SectionTitle>Target Keywords</SectionTitle>
          <div className="flex flex-wrap gap-1.5">
            {data.target_keywords.map((kw: string, i: number) => (
              <Badge key={i} variant="info">{kw}</Badge>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function XPostView({ data }: { data: Record<string, any> }) {
  return (
    <div className="space-y-4">
      {data.single_posts && (
        <div>
          <SectionTitle>Single Post Options</SectionTitle>
          <div className="space-y-2">
            {data.single_posts.map((post: string, i: number) => (
              <div key={i} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-sm text-gray-800">{post}</p>
                  <span className="text-xs text-gray-400 whitespace-nowrap">
                    {post.length}/280
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.thread && (
        <div>
          <SectionTitle>Thread</SectionTitle>
          <div className="space-y-1">
            {data.thread.map((tweet: string, i: number) => (
              <div key={i} className="flex gap-3">
                <div className="flex flex-col items-center">
                  <div className="w-6 h-6 rounded-full bg-primary-100 flex items-center justify-center text-xs font-medium text-primary-700">
                    {i + 1}
                  </div>
                  {i < data.thread.length - 1 && (
                    <div className="w-0.5 flex-1 bg-gray-200 mt-1" />
                  )}
                </div>
                <div className="flex-1 bg-gray-50 rounded-lg p-3 mb-2">
                  <p className="text-sm text-gray-800">{tweet}</p>
                  <span className="text-xs text-gray-400">{tweet.length}/280</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {data.cta_variants && (
        <OptionsList items={data.cta_variants} label="CTA Variants" />
      )}

      {data.engagement_hook && (
        <div>
          <SectionTitle>Engagement Hook</SectionTitle>
          <TextBlock text={data.engagement_hook} className="bg-blue-50 text-blue-800" />
        </div>
      )}
    </div>
  );
}
