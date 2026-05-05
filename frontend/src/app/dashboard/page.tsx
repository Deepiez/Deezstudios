"use client";

import Link from "next/link";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-sm text-gray-500 mt-1">
          Overview produksi konten dan aktivitas terbaru
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <StatCard label="Total Draft" value="--" color="gray" />
        <StatCard label="In Review" value="--" color="yellow" />
        <StatCard label="Scheduled" value="--" color="blue" />
        <StatCard label="Published" value="--" color="green" />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link href="/content/new" className="block">
              <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-primary-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-primary-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Buat Content Baru</p>
                  <p className="text-xs text-gray-500">Mulai dari brief, generate dengan AI</p>
                </div>
              </div>
            </Link>
            <Link href="/content" className="block">
              <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 12h16.5m-16.5 3.75h16.5M3.75 19.5h16.5M5.625 4.5h12.75a1.875 1.875 0 010 3.75H5.625a1.875 1.875 0 010-3.75z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Lihat Semua Content</p>
                  <p className="text-xs text-gray-500">Manage, review, dan approve content</p>
                </div>
              </div>
            </Link>
            <Link href="/calendar" className="block">
              <div className="flex items-center gap-3 p-3 rounded-lg border border-gray-200 hover:border-primary-200 hover:bg-primary-50 transition-colors">
                <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                  <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M6.75 3v2.25M17.25 3v2.25M3 18.75V7.5a2.25 2.25 0 012.25-2.25h13.5A2.25 2.25 0 0121 7.5v11.25m-18 0A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75m-18 0v-7.5A2.25 2.25 0 015.25 9h13.5A2.25 2.25 0 0121 11.25v7.5" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-medium text-gray-900">Content Calendar</p>
                  <p className="text-xs text-gray-500">Lihat jadwal publish mingguan/bulanan</p>
                </div>
              </div>
            </Link>
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <h2 className="text-lg font-semibold text-gray-900">Recent Activity</h2>
          </CardHeader>
          <CardContent>
            <div className="text-center py-8">
              <p className="text-sm text-gray-500">
                Belum ada aktivitas. Mulai dengan membuat content baru.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Provider Status */}
      <Card>
        <CardHeader>
          <h2 className="text-lg font-semibold text-gray-900">AI Providers</h2>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-3 gap-4">
            <ProviderCard name="OpenAI" models="GPT-4o, GPT-4o Mini" />
            <ProviderCard name="Anthropic" models="Claude 3.5 Sonnet, Haiku" />
            <ProviderCard name="Google Gemini" models="Gemini 2.0 Flash, 1.5 Pro" />
          </div>
        </CardContent>
      </Card>

      {/* Coming Soon Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
        <Card className="border-dashed border-2 border-gray-200 bg-gray-50/50">
          <CardContent className="py-6 text-center">
            <div className="w-12 h-12 rounded-full bg-purple-100 flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 15.75l5.159-5.159a2.25 2.25 0 013.182 0l5.159 5.159m-1.5-1.5l1.409-1.409a2.25 2.25 0 013.182 0l2.909 2.909M3.75 21h16.5a1.5 1.5 0 001.5-1.5V6a1.5 1.5 0 00-1.5-1.5H3.75A1.5 1.5 0 002.25 6v13.5A1.5 1.5 0 003.75 21z" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-gray-700">AI Image Generation</h3>
            <p className="text-xs text-gray-500 mt-1">
              Generate thumbnail, cover art, dan visual assets dari prompt
            </p>
            <span className="inline-block mt-3 px-3 py-1 bg-purple-100 text-purple-700 text-xs font-medium rounded-full">
              Coming Soon
            </span>
          </CardContent>
        </Card>

        <Card className="border-dashed border-2 border-gray-200 bg-gray-50/50">
          <CardContent className="py-6 text-center">
            <div className="w-12 h-12 rounded-full bg-indigo-100 flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-indigo-600" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" d="M3.375 19.5h17.25m-17.25 0a1.125 1.125 0 01-1.125-1.125M3.375 19.5h1.5C5.496 19.5 6 18.996 6 18.375m-3.75 0V5.625m0 12.75v-1.5c0-.621.504-1.125 1.125-1.125m18.375 2.625V5.625m0 12.75c0 .621-.504 1.125-1.125 1.125m1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125m0 3.75h-1.5A1.125 1.125 0 0118 18.375M20.625 4.5H3.375m17.25 0c.621 0 1.125.504 1.125 1.125M20.625 4.5h-1.5C18.504 4.5 18 5.004 18 5.625m3.75 0v1.5c0 .621-.504 1.125-1.125 1.125M3.375 4.5c-.621 0-1.125.504-1.125 1.125M3.375 4.5h1.5C5.496 4.5 6 5.004 6 5.625m-3.75 0v1.5c0 .621.504 1.125 1.125 1.125m0 0h1.5m-1.5 0c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125m1.5-3.75C5.496 8.25 6 7.746 6 7.125v-1.5M4.875 8.25C5.496 8.25 6 8.754 6 9.375v1.5m0-5.25v5.25m0-5.25C6 5.004 6.504 4.5 7.125 4.5h9.75c.621 0 1.125.504 1.125 1.125m1.125 2.625h1.5m-1.5 0A1.125 1.125 0 0118 7.125v-1.5m1.125 2.625c-.621 0-1.125.504-1.125 1.125v1.5m2.625-2.625c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125M18 5.625v5.25M7.125 12h9.75m-9.75 0A1.125 1.125 0 016 10.875M7.125 12C6.504 12 6 12.504 6 13.125m0-2.25C6 11.496 5.496 12 4.875 12M18 10.875c0 .621-.504 1.125-1.125 1.125M18 10.875c0 .621.504 1.125 1.125 1.125m-2.25 0c.621 0 1.125.504 1.125 1.125m-12 5.25v-5.25m0 5.25c0 .621.504 1.125 1.125 1.125h9.75c.621 0 1.125-.504 1.125-1.125m-12 0v-1.5c0-.621-.504-1.125-1.125-1.125M18 18.375v-5.25m0 5.25v-1.5c0-.621.504-1.125 1.125-1.125M18 13.125v1.5c0 .621.504 1.125 1.125 1.125M18 13.125c0-.621.504-1.125 1.125-1.125M6 13.125v1.5c0 .621-.504 1.125-1.125 1.125M6 13.125C6 12.504 5.496 12 4.875 12m-1.5 0h1.5m-1.5 0c-.621 0-1.125-.504-1.125-1.125v-1.5c0-.621.504-1.125 1.125-1.125M19.125 12h1.5m0 0c.621 0 1.125.504 1.125 1.125v1.5c0 .621-.504 1.125-1.125 1.125m-17.25 0h1.5m14.25 0h1.5" />
              </svg>
            </div>
            <h3 className="text-sm font-semibold text-gray-700">AI Video Generation</h3>
            <p className="text-xs text-gray-500 mt-1">
              Generate short video clips dan B-roll dari script
            </p>
            <span className="inline-block mt-3 px-3 py-1 bg-indigo-100 text-indigo-700 text-xs font-medium rounded-full">
              Coming Soon
            </span>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

function StatCard({ label, value, color }: { label: string; value: string; color: string }) {
  const colors: Record<string, string> = {
    gray: "bg-gray-50 border-gray-200",
    yellow: "bg-yellow-50 border-yellow-200",
    blue: "bg-blue-50 border-blue-200",
    green: "bg-green-50 border-green-200",
  };

  return (
    <div className={`rounded-xl border p-4 ${colors[color]}`}>
      <p className="text-sm text-gray-600">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}

function ProviderCard({ name, models }: { name: string; models: string }) {
  return (
    <div className="p-4 rounded-lg border border-gray-200">
      <div className="flex items-center gap-2 mb-2">
        <div className="w-2 h-2 rounded-full bg-gray-300" />
        <p className="text-sm font-medium text-gray-900">{name}</p>
      </div>
      <p className="text-xs text-gray-500">{models}</p>
      <p className="text-xs text-gray-400 mt-1">Configure in .env</p>
    </div>
  );
}
