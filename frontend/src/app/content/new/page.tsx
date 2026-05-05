"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent, CardFooter } from "@/components/ui/card";
import { Input, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { useContent } from "@/hooks/use-content";

const contentTypeOptions = [
  { value: "youtube_shorts", label: "YouTube Shorts" },
  { value: "youtube_longform", label: "YouTube Long-form" },
  { value: "tiktok_short", label: "TikTok Short Video" },
  { value: "blog_article", label: "Blog Article" },
  { value: "x_post", label: "X (Twitter) Post" },
];

const languageOptions = [
  { value: "id", label: "Bahasa Indonesia" },
  { value: "en", label: "English" },
];

const toneOptions = [
  { value: "Casual informatif", label: "Casual Informatif" },
  { value: "Professional", label: "Professional" },
  { value: "Friendly dan energetic", label: "Friendly & Energetic" },
  { value: "Serius dan mendalam", label: "Serius & Mendalam" },
  { value: "Humor ringan", label: "Humor Ringan" },
  { value: "Inspiratif dan motivasi", label: "Inspiratif" },
];

export default function NewContentPage() {
  const router = useRouter();
  const { createContent, loading, error } = useContent();

  const [form, setForm] = useState({
    title: "",
    content_type: "youtube_shorts",
    language: "id",
    campaign_id: "", // TODO: select from campaigns
    brief: {
      topic: "",
      audience: "",
      objective: "",
      key_message: "",
      tone: "Casual informatif",
      language: "id",
      references: "",
      target_duration: "",
      target_word_count: "",
      additional_context: "",
    },
    tags: "",
  });

  const updateForm = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const updateBrief = (field: string, value: string) => {
    setForm((prev) => ({
      ...prev,
      brief: { ...prev.brief, [field]: value },
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const result = await createContent({
      campaign_id: form.campaign_id,
      title: form.title,
      content_type: form.content_type,
      language: form.language,
      brief: {
        ...form.brief,
        language: form.language,
      },
      tags: form.tags ? form.tags.split(",").map((t) => t.trim()) : undefined,
    });

    if (result) {
      router.push(`/content/${result.id}`);
    }
  };

  const showDuration = ["youtube_shorts", "youtube_longform", "tiktok_short"].includes(
    form.content_type
  );
  const showWordCount = form.content_type === "blog_article";

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Buat Content Baru</h1>
          <p className="text-sm text-gray-500 mt-1">
            Isi brief untuk memulai content generation
          </p>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Basic Info */}
          <Card className="mb-6">
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">Informasi Dasar</h2>
            </CardHeader>
            <CardContent className="space-y-4">
              <Input
                label="Judul Content"
                placeholder="e.g. 5 Tips Produktivitas Developer WFH"
                value={form.title}
                onChange={(e) => updateForm("title", e.target.value)}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Select
                  label="Tipe Content"
                  options={contentTypeOptions}
                  value={form.content_type}
                  onChange={(e) => updateForm("content_type", e.target.value)}
                />
                <Select
                  label="Bahasa Output"
                  options={languageOptions}
                  value={form.language}
                  onChange={(e) => {
                    updateForm("language", e.target.value);
                    updateBrief("language", e.target.value);
                  }}
                />
              </div>

              <Input
                label="Campaign ID"
                placeholder="UUID campaign (akan diganti dropdown)"
                value={form.campaign_id}
                onChange={(e) => updateForm("campaign_id", e.target.value)}
                required
              />

              <Input
                label="Tags (comma-separated)"
                placeholder="productivity, developer, wfh"
                value={form.tags}
                onChange={(e) => updateForm("tags", e.target.value)}
              />
            </CardContent>
          </Card>

          {/* Brief */}
          <Card className="mb-6">
            <CardHeader>
              <h2 className="text-lg font-semibold text-gray-900">Brief</h2>
              <p className="text-sm text-gray-500">
                Brief adalah panduan untuk AI dalam menghasilkan konten
              </p>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                label="Topik"
                placeholder="Jelaskan topik utama konten yang ingin dibuat..."
                value={form.brief.topic}
                onChange={(e) => updateBrief("topic", e.target.value)}
                required
                rows={3}
              />

              <Textarea
                label="Target Audience"
                placeholder="e.g. Developer Indonesia usia 22-35 yang kerja remote"
                value={form.brief.audience}
                onChange={(e) => updateBrief("audience", e.target.value)}
                rows={2}
              />

              <Textarea
                label="Objective"
                placeholder="e.g. Edukasi + engagement, dorong subscribe"
                value={form.brief.objective}
                onChange={(e) => updateBrief("objective", e.target.value)}
                rows={2}
              />

              <Textarea
                label="Key Message"
                placeholder="Pesan utama yang ingin disampaikan..."
                value={form.brief.key_message}
                onChange={(e) => updateBrief("key_message", e.target.value)}
                rows={2}
              />

              <Select
                label="Tone of Voice"
                options={toneOptions}
                value={form.brief.tone}
                onChange={(e) => updateBrief("tone", e.target.value)}
              />

              {showDuration && (
                <Input
                  label="Target Durasi"
                  placeholder="e.g. 45-60 detik atau 8-12 menit"
                  value={form.brief.target_duration}
                  onChange={(e) => updateBrief("target_duration", e.target.value)}
                />
              )}

              {showWordCount && (
                <Input
                  label="Target Word Count"
                  placeholder="e.g. 1500-2000"
                  value={form.brief.target_word_count}
                  onChange={(e) => updateBrief("target_word_count", e.target.value)}
                />
              )}

              <Textarea
                label="Referensi / Notes (opsional)"
                placeholder="Link referensi, catatan tambahan, inspirasi..."
                value={form.brief.references}
                onChange={(e) => updateBrief("references", e.target.value)}
                rows={2}
              />

              <Textarea
                label="Instruksi Tambahan (opsional)"
                placeholder="Instruksi spesifik untuk AI, misalnya: fokus pada hook yang provokatif..."
                value={form.brief.additional_context}
                onChange={(e) => updateBrief("additional_context", e.target.value)}
                rows={2}
              />
            </CardContent>
          </Card>

          {/* Error */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-3">
            <Button
              type="button"
              variant="outline"
              onClick={() => router.back()}
            >
              Batal
            </Button>
            <Button type="submit" loading={loading}>
              Buat Content
            </Button>
          </div>
        </form>
      </div>
    </DashboardLayout>
  );
}
