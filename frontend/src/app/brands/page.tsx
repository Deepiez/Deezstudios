"use client";

import { useEffect, useState } from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Input, Textarea } from "@/components/ui/input";
import { api } from "@/lib/api";
import { formatDateTime } from "@/lib/utils";

interface Brand {
  id: string;
  name: string;
  description: string | null;
  niche: string | null;
  target_audience: string | null;
  created_at: string;
}

interface Campaign {
  id: string;
  brand_id: string;
  name: string;
  description: string | null;
  objective: string | null;
  status: string;
  start_date: string | null;
  end_date: string | null;
}

export default function BrandsPage() {
  const [brands, setBrands] = useState<Brand[]>([]);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedBrand, setSelectedBrand] = useState<Brand | null>(null);
  const [showBrandForm, setShowBrandForm] = useState(false);
  const [showCampaignForm, setShowCampaignForm] = useState(false);
  const [loading, setLoading] = useState(true);

  // Brand form
  const [brandForm, setBrandForm] = useState({ name: "", description: "", niche: "", target_audience: "" });
  // Campaign form
  const [campaignForm, setCampaignForm] = useState({ name: "", description: "", objective: "" });

  useEffect(() => { loadBrands(); }, []);

  const loadBrands = async () => {
    setLoading(true);
    try {
      const res = await api.get<Brand[]>("/brands/");
      setBrands(res.data);
      if (res.data.length > 0 && !selectedBrand) {
        setSelectedBrand(res.data[0]);
        loadCampaigns(res.data[0].id);
      }
    } catch (err) {}
    setLoading(false);
  };

  const loadCampaigns = async (brandId: string) => {
    try {
      const res = await api.get<Campaign[]>("/campaigns/", { params: { brand_id: brandId } });
      setCampaigns(res.data);
    } catch (err) { setCampaigns([]); }
  };

  const handleSelectBrand = (brand: Brand) => {
    setSelectedBrand(brand);
    loadCampaigns(brand.id);
  };

  const handleCreateBrand = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await api.post<Brand>("/brands/", brandForm);
      setBrands([res.data, ...brands]);
      setSelectedBrand(res.data);
      loadCampaigns(res.data.id);
      setShowBrandForm(false);
      setBrandForm({ name: "", description: "", niche: "", target_audience: "" });
    } catch (err) {}
  };

  const handleCreateCampaign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedBrand) return;
    try {
      const res = await api.post<Campaign>("/campaigns/", {
        brand_id: selectedBrand.id,
        ...campaignForm,
      });
      setCampaigns([res.data, ...campaigns]);
      setShowCampaignForm(false);
      setCampaignForm({ name: "", description: "", objective: "" });
    } catch (err) {}
  };

  const handleDeleteBrand = async (id: string) => {
    if (!confirm("Delete this brand and all its campaigns?")) return;
    try {
      await api.delete(`/brands/${id}`);
      setBrands(brands.filter((b) => b.id !== id));
      if (selectedBrand?.id === id) { setSelectedBrand(null); setCampaigns([]); }
    } catch (err) {}
  };

  const handleDeleteCampaign = async (id: string) => {
    if (!confirm("Delete this campaign?")) return;
    try {
      await api.delete(`/campaigns/${id}`);
      setCampaigns(campaigns.filter((c) => c.id !== id));
    } catch (err) {}
  };

  const statusVariant = (s: string) => {
    const map: Record<string, "default" | "success" | "warning" | "info"> = {
      planning: "default", active: "success", paused: "warning", completed: "info", archived: "default",
    };
    return map[s] || "default";
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Brands & Campaigns</h1>
        <p className="text-sm text-gray-500 mt-1">Kelola brand dan campaign konten</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Brands List */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-sm font-semibold text-gray-700">Brands</h2>
            <Button size="sm" onClick={() => setShowBrandForm(true)}>+ Brand</Button>
          </div>

          {showBrandForm && (
            <Card>
              <CardContent className="py-4">
                <form onSubmit={handleCreateBrand} className="space-y-3">
                  <Input placeholder="Brand name" value={brandForm.name} onChange={(e) => setBrandForm({ ...brandForm, name: e.target.value })} required />
                  <Input placeholder="Niche (e.g. Tech)" value={brandForm.niche} onChange={(e) => setBrandForm({ ...brandForm, niche: e.target.value })} />
                  <Textarea placeholder="Description" value={brandForm.description} onChange={(e) => setBrandForm({ ...brandForm, description: e.target.value })} rows={2} />
                  <div className="flex gap-2">
                    <Button type="submit" size="sm">Save</Button>
                    <Button type="button" size="sm" variant="ghost" onClick={() => setShowBrandForm(false)}>Cancel</Button>
                  </div>
                </form>
              </CardContent>
            </Card>
          )}

          {brands.map((brand) => (
            <div
              key={brand.id}
              onClick={() => handleSelectBrand(brand)}
              className={`p-4 rounded-lg border cursor-pointer transition-colors ${
                selectedBrand?.id === brand.id
                  ? "border-primary-300 bg-primary-50"
                  : "border-gray-200 bg-white hover:border-gray-300"
              }`}
            >
              <div className="flex items-center justify-between">
                <h3 className="text-sm font-medium text-gray-900">{brand.name}</h3>
                <button onClick={(e) => { e.stopPropagation(); handleDeleteBrand(brand.id); }} className="text-gray-400 hover:text-red-500 text-xs">Delete</button>
              </div>
              {brand.niche && <p className="text-xs text-gray-500 mt-1">{brand.niche}</p>}
            </div>
          ))}

          {!loading && brands.length === 0 && !showBrandForm && (
            <p className="text-sm text-gray-400 text-center py-4">No brands yet</p>
          )}
        </div>

        {/* Campaigns */}
        <div className="lg:col-span-2 space-y-4">
          {selectedBrand ? (
            <>
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">{selectedBrand.name}</h2>
                  {selectedBrand.description && <p className="text-sm text-gray-500">{selectedBrand.description}</p>}
                </div>
                <Button size="sm" onClick={() => setShowCampaignForm(true)}>+ Campaign</Button>
              </div>

              {showCampaignForm && (
                <Card>
                  <CardContent className="py-4">
                    <form onSubmit={handleCreateCampaign} className="space-y-3">
                      <Input placeholder="Campaign name" value={campaignForm.name} onChange={(e) => setCampaignForm({ ...campaignForm, name: e.target.value })} required />
                      <Input placeholder="Objective" value={campaignForm.objective} onChange={(e) => setCampaignForm({ ...campaignForm, objective: e.target.value })} />
                      <Textarea placeholder="Description" value={campaignForm.description} onChange={(e) => setCampaignForm({ ...campaignForm, description: e.target.value })} rows={2} />
                      <div className="flex gap-2">
                        <Button type="submit" size="sm">Create Campaign</Button>
                        <Button type="button" size="sm" variant="ghost" onClick={() => setShowCampaignForm(false)}>Cancel</Button>
                      </div>
                    </form>
                  </CardContent>
                </Card>
              )}

              {campaigns.length === 0 ? (
                <Card><CardContent className="py-8 text-center"><p className="text-sm text-gray-400">No campaigns yet for this brand</p></CardContent></Card>
              ) : (
                <div className="space-y-3">
                  {campaigns.map((c) => (
                    <Card key={c.id}>
                      <CardContent className="py-4 flex items-center justify-between">
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="text-sm font-medium text-gray-900">{c.name}</h3>
                            <Badge variant={statusVariant(c.status)}>{c.status}</Badge>
                          </div>
                          {c.objective && <p className="text-xs text-gray-500 mt-1">{c.objective}</p>}
                        </div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-gray-400 font-mono">{c.id.slice(0, 8)}</span>
                          <button onClick={() => handleDeleteCampaign(c.id)} className="text-xs text-gray-400 hover:text-red-500">Delete</button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </>
          ) : (
            <Card><CardContent className="py-12 text-center"><p className="text-gray-400">Select a brand to view campaigns</p></CardContent></Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
