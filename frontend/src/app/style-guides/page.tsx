"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input, Textarea } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { api } from "@/lib/api";

interface StyleGuide {
  id: string;
  name: string;
  is_active: boolean;
  tone_of_voice: string | null;
  writing_rules: string[] | null;
  preferred_phrases: string[] | null;
  banned_phrases: string[] | null;
  additional_notes: string | null;
  brand_id: string | null;
}

interface CTAPattern {
  id: string;
  name: string;
  is_active: boolean;
  cta_text: string;
  cta_type: string | null;
  placement: string | null;
  platform_target: string | null;
  brand_id: string | null;
}

type Tab = "guides" | "cta";

export default function StyleGuidesPage() {
  const [tab, setTab] = useState<Tab>("guides");
  const [guides, setGuides] = useState<StyleGuide[]>([]);
  const [patterns, setPatterns] = useState<CTAPattern[]>([]);
  const [showGuideForm, setShowGuideForm] = useState(false);
  const [showCTAForm, setShowCTAForm] = useState(false);

  // Guide form
  const [guideForm, setGuideForm] = useState({
    name: "", tone_of_voice: "", writing_rules: "", preferred_phrases: "", banned_phrases: "", additional_notes: "",
  });
  // CTA form
  const [ctaForm, setCtaForm] = useState({
    name: "", cta_text: "", cta_type: "subscribe", placement: "outro", platform_target: "",
  });

  useEffect(() => { loadData(); }, []);

  const loadData = async () => {
    try {
      const [guidesRes, ctaRes] = await Promise.all([
        api.get<StyleGuide[]>("/style-guides/"),
        api.get<CTAPattern[]>("/style-guides/cta-patterns"),
      ]);
      setGuides(guidesRes.data);
      setPatterns(ctaRes.data);
    } catch (err) {}
  };

  const handleCreateGuide = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post<StyleGuide>("/style-guides/", {
        name: guideForm.name,
        tone_of_voice: guideForm.tone_of_voice || null,
        writing_rules: guideForm.writing_rules ? guideForm.writing_rules.split("\n").filter(Boolean) : null,
        preferred_phrases: guideForm.preferred_phrases ? guideForm.preferred_phrases.split(",").map((s) => s.trim()).filter(Boolean) : null,
        banned_phrases: guideForm.banned_phrases ? guideForm.banned_phrases.split(",").map((s) => s.trim()).filter(Boolean) : null,
        additional_notes: guideForm.additional_notes || null,
      });
      setGuides([res.data, ...guides]);
      setShowGuideForm(false);
      setGuideForm({ name: "", tone_of_voice: "", writing_rules: "", preferred_phrases: "", banned_phrases: "", additional_notes: "" });
    } catch (err) {}
  };

  const handleCreateCTA = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post<CTAPattern>("/style-guides/cta-patterns", {
        name: ctaForm.name,
        cta_text: ctaForm.cta_text,
        cta_type: ctaForm.cta_type || null,
        placement: ctaForm.placement || null,
        platform_target: ctaForm.platform_target || null,
      });
      setPatterns([res.data, ...patterns]);
      setShowCTAForm(false);
      setCtaForm({ name: "", cta_text: "", cta_type: "subscribe", placement: "outro", platform_target: "" });
    } catch (err) {}
  };

  const toggleGuide = async (id: string) => {
    try {
      const res = await api.patch<{ is_active: boolean }>(`/style-guides/${id}/toggle`);
      setGuides(guides.map((g) => g.id === id ? { ...g, is_active: res.data.is_active } : g));
    } catch (err) {}
  };

  const toggleCTA = async (id: string) => {
    try {
      const res = await api.patch<{ is_active: boolean }>(`/style-guides/cta-patterns/${id}/toggle`);
      setPatterns(patterns.map((p) => p.id === id ? { ...p, is_active: res.data.is_active } : p));
    } catch (err) {}
  };

  const deleteGuide = async (id: string) => {
    if (!confirm("Delete this style guide?")) return;
    try { await api.delete(`/style-guides/${id}`); setGuides(guides.filter((g) => g.id !== id)); } catch (err) {}
  };

  const deleteCTA = async (id: string) => {
    if (!confirm("Delete this CTA pattern?")) return;
    try { await api.delete(`/style-guides/cta-patterns/${id}`); setPatterns(patterns.filter((p) => p.id !== id)); } catch (err) {}
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Style Guides & CTA Patterns</h1>
        <p className="text-sm text-gray-500 mt-1">Kelola konsistensi gaya dan CTA untuk content generation</p>
      </div>

      {/* Tabs */}
      <div className="flex items-center gap-1 bg-gray-100 rounded-lg p-1 w-fit mb-6">
        <button onClick={() => setTab("guides")} className={`px-4 py-2 text-sm font-medium rounded-md ${tab === "guides" ? "bg-white shadow-sm text-gray-900" : "text-gray-600"}`}>
          Style Guides ({guides.length})
        </button>
        <button onClick={() => setTab("cta")} className={`px-4 py-2 text-sm font-medium rounded-md ${tab === "cta" ? "bg-white shadow-sm text-gray-900" : "text-gray-600"}`}>
          CTA Patterns ({patterns.length})
        </button>
      </div>

      {/* Style Guides Tab */}
      {tab === "guides" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setShowGuideForm(!showGuideForm)}>
              {showGuideForm ? "Cancel" : "+ New Style Guide"}
            </Button>
          </div>

          {showGuideForm && (
            <Card>
              <CardContent className="py-4">
                <form onSubmit={handleCreateGuide} className="space-y-3">
                  <Input label="Name" placeholder="e.g. Brand Voice - Casual Tech" value={guideForm.name} onChange={(e) => setGuideForm({ ...guideForm, name: e.target.value })} required />
                  <Input label="Tone of Voice" placeholder="e.g. Friendly, casual, tapi tetap informatif" value={guideForm.tone_of_voice} onChange={(e) => setGuideForm({ ...guideForm, tone_of_voice: e.target.value })} />
                  <Textarea label="Writing Rules (satu per baris)" placeholder="Gunakan 'kamu' bukan 'Anda'\nKalimat pendek, max 20 kata" value={guideForm.writing_rules} onChange={(e) => setGuideForm({ ...guideForm, writing_rules: e.target.value })} rows={3} />
                  <Input label="Preferred Phrases (comma-separated)" placeholder="yuk, simpel banget, let's go" value={guideForm.preferred_phrases} onChange={(e) => setGuideForm({ ...guideForm, preferred_phrases: e.target.value })} />
                  <Input label="Banned Phrases (comma-separated)" placeholder="halo guys, jangan lupa subscribe" value={guideForm.banned_phrases} onChange={(e) => setGuideForm({ ...guideForm, banned_phrases: e.target.value })} />
                  <Textarea label="Additional Notes" placeholder="Catatan tambahan..." value={guideForm.additional_notes} onChange={(e) => setGuideForm({ ...guideForm, additional_notes: e.target.value })} rows={2} />
                  <Button type="submit" size="sm">Create Style Guide</Button>
                </form>
              </CardContent>
            </Card>
          )}

          {guides.length === 0 ? (
            <Card><CardContent className="py-8 text-center"><p className="text-sm text-gray-400">No style guides yet</p></CardContent></Card>
          ) : (
            guides.map((guide) => (
              <Card key={guide.id} className={!guide.is_active ? "opacity-60" : ""}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h3 className="text-sm font-semibold text-gray-900">{guide.name}</h3>
                        <Badge variant={guide.is_active ? "success" : "default"}>
                          {guide.is_active ? "Active" : "Inactive"}
                        </Badge>
                      </div>
                      {guide.tone_of_voice && <p className="text-xs text-gray-600 mb-1"><span className="font-medium">Tone:</span> {guide.tone_of_voice}</p>}
                      {guide.writing_rules && guide.writing_rules.length > 0 && (
                        <div className="text-xs text-gray-500 mb-1">
                          <span className="font-medium">Rules:</span> {guide.writing_rules.slice(0, 3).join(" | ")}{guide.writing_rules.length > 3 && ` +${guide.writing_rules.length - 3} more`}
                        </div>
                      )}
                      {guide.banned_phrases && guide.banned_phrases.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-1">
                          {guide.banned_phrases.slice(0, 5).map((p, i) => (
                            <span key={i} className="text-xs bg-red-50 text-red-600 px-1.5 py-0.5 rounded">{p}</span>
                          ))}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      <Button size="sm" variant="ghost" onClick={() => toggleGuide(guide.id)}>
                        {guide.is_active ? "Deactivate" : "Activate"}
                      </Button>
                      <button onClick={() => deleteGuide(guide.id)} className="text-xs text-gray-400 hover:text-red-500">Delete</button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}

      {/* CTA Patterns Tab */}
      {tab === "cta" && (
        <div className="space-y-4">
          <div className="flex justify-end">
            <Button size="sm" onClick={() => setShowCTAForm(!showCTAForm)}>
              {showCTAForm ? "Cancel" : "+ New CTA Pattern"}
            </Button>
          </div>

          {showCTAForm && (
            <Card>
              <CardContent className="py-4">
                <form onSubmit={handleCreateCTA} className="space-y-3">
                  <Input label="Name" placeholder="e.g. Subscribe CTA - Outro" value={ctaForm.name} onChange={(e) => setCtaForm({ ...ctaForm, name: e.target.value })} required />
                  <Textarea label="CTA Text" placeholder="Kalau konten ini helpful, tap follow buat tips lainnya" value={ctaForm.cta_text} onChange={(e) => setCtaForm({ ...ctaForm, cta_text: e.target.value })} required rows={2} />
                  <div className="grid grid-cols-3 gap-3">
                    <Select label="Type" options={[
                      { value: "subscribe", label: "Subscribe" }, { value: "like", label: "Like" },
                      { value: "comment", label: "Comment" }, { value: "share", label: "Share" },
                      { value: "link", label: "Link/Click" }, { value: "other", label: "Other" },
                    ]} value={ctaForm.cta_type} onChange={(e) => setCtaForm({ ...ctaForm, cta_type: e.target.value })} />
                    <Select label="Placement" options={[
                      { value: "intro", label: "Intro" }, { value: "mid", label: "Mid" }, { value: "outro", label: "Outro" },
                    ]} value={ctaForm.placement} onChange={(e) => setCtaForm({ ...ctaForm, placement: e.target.value })} />
                    <Select label="Platform" options={[
                      { value: "", label: "All Platforms" }, { value: "youtube", label: "YouTube" },
                      { value: "tiktok", label: "TikTok" }, { value: "blog", label: "Blog" }, { value: "x", label: "X" },
                    ]} value={ctaForm.platform_target} onChange={(e) => setCtaForm({ ...ctaForm, platform_target: e.target.value })} />
                  </div>
                  <Button type="submit" size="sm">Create CTA Pattern</Button>
                </form>
              </CardContent>
            </Card>
          )}

          {patterns.length === 0 ? (
            <Card><CardContent className="py-8 text-center"><p className="text-sm text-gray-400">No CTA patterns yet</p></CardContent></Card>
          ) : (
            patterns.map((cta) => (
              <Card key={cta.id} className={!cta.is_active ? "opacity-60" : ""}>
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-sm font-medium text-gray-900">{cta.name}</h3>
                        <Badge variant={cta.is_active ? "success" : "default"}>
                          {cta.is_active ? "Active" : "Inactive"}
                        </Badge>
                        {cta.cta_type && <Badge variant="info">{cta.cta_type}</Badge>}
                        {cta.placement && <Badge>{cta.placement}</Badge>}
                        {cta.platform_target && <Badge variant="warning">{cta.platform_target}</Badge>}
                      </div>
                      <p className="text-sm text-gray-700 bg-gray-50 rounded p-2 mt-2">"{cta.cta_text}"</p>
                    </div>
                    <div className="flex items-center gap-2 ml-4">
                      <Button size="sm" variant="ghost" onClick={() => toggleCTA(cta.id)}>
                        {cta.is_active ? "Deactivate" : "Activate"}
                      </Button>
                      <button onClick={() => deleteCTA(cta.id)} className="text-xs text-gray-400 hover:text-red-500">Delete</button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>
      )}
    </DashboardLayout>
  );
}
