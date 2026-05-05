"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { GenerationPanel } from "@/components/generation/generation-panel";
import { ContentViewer } from "@/components/generation/content-viewer";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { StatusBadge, Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/input";
import { useContent } from "@/hooks/use-content";
import { useGenerationRuns } from "@/hooks/use-generation";
import { getContentTypeLabel, formatDateTime } from "@/lib/utils";
import type { ContentItem, ContentVersion } from "@/types";

export default function ContentDetailPage() {
  const params = useParams();
  const router = useRouter();
  const contentId = params.id as string;

  const { getContent, getVersions, submitForReview, approveContent, rejectContent, loading } =
    useContent();
  const { runs, fetchRuns } = useGenerationRuns(contentId);

  const [content, setContent] = useState<ContentItem | null>(null);
  const [versions, setVersions] = useState<ContentVersion[]>([]);
  const [pageLoading, setPageLoading] = useState(true);
  const [showRejectModal, setShowRejectModal] = useState(false);
  const [rejectNotes, setRejectNotes] = useState("");

  useEffect(() => {
    loadData();
  }, [contentId]);

  const loadData = async () => {
    setPageLoading(true);
    const [contentData, versionsData] = await Promise.all([
      getContent(contentId),
      getVersions(contentId),
    ]);
    setContent(contentData);
    setVersions(versionsData);
    fetchRuns();
    setPageLoading(false);
  };

  const handleGenerationComplete = async () => {
    // Reload content and versions after generation
    await loadData();
  };

  const handleSubmitReview = async () => {
    if (!content) return;
    const result = await submitForReview(content.id);
    if (result) setContent(result);
  };

  const handleApprove = async () => {
    if (!content) return;
    const result = await approveContent(content.id);
    if (result) setContent(result);
  };

  const handleReject = async () => {
    if (!content) return;
    const result = await rejectContent(content.id, rejectNotes);
    if (result) {
      setContent(result);
      setShowRejectModal(false);
      setRejectNotes("");
    }
  };

  if (pageLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      </DashboardLayout>
    );
  }

  if (!content) {
    return (
      <DashboardLayout>
        <div className="text-center py-20">
          <h2 className="text-xl font-medium text-gray-900">Content not found</h2>
          <Button variant="outline" className="mt-4" onClick={() => router.push("/content")}>
            Back to Content List
          </Button>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <button
          onClick={() => router.push("/content")}
          className="text-sm text-gray-500 hover:text-gray-700 mb-3 flex items-center gap-1"
        >
          <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
          </svg>
          Back to Content
        </button>

        <div className="flex items-start justify-between">
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-bold text-gray-900">{content.title}</h1>
              <StatusBadge status={content.status} />
            </div>
            <div className="flex items-center gap-4 mt-2">
              <Badge>{getContentTypeLabel(content.content_type)}</Badge>
              <span className="text-sm text-gray-500">
                Version {content.current_version}
              </span>
              <span className="text-sm text-gray-400">
                Updated {formatDateTime(content.updated_at)}
              </span>
            </div>
          </div>

          {/* Workflow Actions */}
          <div className="flex items-center gap-2">
            {/* Clone button - always available */}
            <Button
              variant="ghost"
              size="sm"
              onClick={async () => {
                try {
                  const res = await (await import("@/lib/api")).api.post(
                    `/content/${content.id}/clone`
                  );
                  router.push(`/content/${res.data.id}`);
                } catch (err) {}
              }}
            >
              Clone
            </Button>

            {content.status === "draft" && content.current_version > 0 && (
              <Button onClick={handleSubmitReview} loading={loading} size="sm">
                Submit for Review
              </Button>
            )}
            {content.status === "in_review" && (
              <>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowRejectModal(true)}
                >
                  Reject
                </Button>
                <Button onClick={handleApprove} loading={loading} size="sm">
                  Approve
                </Button>
              </>
            )}
            {content.status === "approved" && (
              <Button size="sm" onClick={() => router.push(`/calendar?content=${content.id}`)}>
                Schedule Publish
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Content Output (2/3) */}
        <div className="lg:col-span-2 space-y-6">
          {/* Content Viewer */}
          <ContentViewer
            versions={versions}
            contentType={content.content_type}
            currentVersion={content.current_version}
          />

          {/* Generation History */}
          {runs.length > 0 && (
            <Card>
              <CardHeader>
                <h3 className="text-lg font-semibold text-gray-900">Generation History</h3>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  {runs.slice(0, 10).map((run) => (
                    <div
                      key={run.id}
                      className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0"
                    >
                      <div className="flex items-center gap-3">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            run.status === "completed"
                              ? "bg-green-500"
                              : run.status === "failed"
                              ? "bg-red-500"
                              : "bg-yellow-500"
                          }`}
                        />
                        <span className="text-sm text-gray-700">
                          {run.provider} / {run.model}
                        </span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-500">
                        {run.latency_ms && (
                          <span>{(run.latency_ms / 1000).toFixed(1)}s</span>
                        )}
                        {run.cost_usd && <span>${run.cost_usd.toFixed(4)}</span>}
                        <span>{formatDateTime(run.created_at)}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right: Generation Panel + Brief (1/3) */}
        <div className="space-y-6">
          {/* Generation Panel */}
          {(content.status === "draft" || content.status === "in_review") && (
            <GenerationPanel
              contentItemId={content.id}
              contentType={content.content_type}
              onGenerationComplete={handleGenerationComplete}
            />
          )}

          {/* Brief Summary */}
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">Brief</h3>
            </CardHeader>
            <CardContent>
              {content.brief ? (
                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-medium text-gray-700">Topik:</span>
                    <p className="text-gray-600 mt-0.5">
                      {(content.brief as any).topic}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Audience:</span>
                    <p className="text-gray-600 mt-0.5">
                      {(content.brief as any).audience}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Objective:</span>
                    <p className="text-gray-600 mt-0.5">
                      {(content.brief as any).objective}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Key Message:</span>
                    <p className="text-gray-600 mt-0.5">
                      {(content.brief as any).key_message}
                    </p>
                  </div>
                  <div>
                    <span className="font-medium text-gray-700">Tone:</span>
                    <p className="text-gray-600 mt-0.5">
                      {(content.brief as any).tone}
                    </p>
                  </div>
                  {(content.brief as any).references && (
                    <div>
                      <span className="font-medium text-gray-700">References:</span>
                      <p className="text-gray-600 mt-0.5">
                        {(content.brief as any).references}
                      </p>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-sm text-gray-500">No brief attached</p>
              )}
            </CardContent>
          </Card>

          {/* Tags */}
          {content.tags && content.tags.length > 0 && (
            <Card>
              <CardContent className="py-3">
                <div className="flex flex-wrap gap-1.5">
                  {content.tags.map((tag, i) => (
                    <Badge key={i}>{tag}</Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      {/* Reject Modal */}
      {showRejectModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Reject Content</h3>
            <Textarea
              label="Catatan Revisi"
              placeholder="Jelaskan apa yang perlu diperbaiki..."
              value={rejectNotes}
              onChange={(e) => setRejectNotes(e.target.value)}
              rows={4}
            />
            <div className="flex justify-end gap-3 mt-4">
              <Button variant="outline" onClick={() => setShowRejectModal(false)}>
                Batal
              </Button>
              <Button variant="danger" onClick={handleReject} loading={loading}>
                Reject & Request Revision
              </Button>
            </div>
          </div>
        </div>
      )}
    </DashboardLayout>
  );
}
