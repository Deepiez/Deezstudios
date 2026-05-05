"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/badge";
import { useContent } from "@/hooks/use-content";
import { getContentTypeLabel, formatDateTime } from "@/lib/utils";
import type { ContentItem } from "@/types";

export default function ContentListPage() {
  const [items, setItems] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const { listContent } = useContent();

  useEffect(() => {
    loadContent();
  }, []);

  const loadContent = async () => {
    setLoading(true);
    const data = await listContent();
    setItems(data);
    setLoading(false);
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content</h1>
          <p className="text-sm text-gray-500 mt-1">
            Kelola semua content items dan jalankan generation
          </p>
        </div>
        <Link href="/content/new">
          <Button>+ Buat Content Baru</Button>
        </Link>
      </div>

      {/* Content List */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
        </div>
      ) : items.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              strokeWidth={1}
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m3.75 9v6m3-3H9m1.5-12H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
            <h3 className="mt-4 text-lg font-medium text-gray-900">Belum ada content</h3>
            <p className="mt-2 text-sm text-gray-500">
              Mulai dengan membuat content baru dan brief-nya.
            </p>
            <Link href="/content/new" className="mt-6 inline-block">
              <Button>+ Buat Content Pertama</Button>
            </Link>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <Link key={item.id} href={`/content/${item.id}`}>
              <Card className="hover:border-primary-200 hover:shadow-md transition-all cursor-pointer">
                <CardContent className="flex items-center justify-between py-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3">
                      <h3 className="text-sm font-medium text-gray-900 truncate">
                        {item.title}
                      </h3>
                      <StatusBadge status={item.status} />
                    </div>
                    <div className="flex items-center gap-4 mt-1.5">
                      <span className="text-xs text-gray-500">
                        {getContentTypeLabel(item.content_type)}
                      </span>
                      <span className="text-xs text-gray-400">
                        v{item.current_version}
                      </span>
                      <span className="text-xs text-gray-400">
                        {formatDateTime(item.updated_at)}
                      </span>
                    </div>
                  </div>
                  <svg
                    className="w-5 h-5 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    strokeWidth={1.5}
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                  </svg>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
