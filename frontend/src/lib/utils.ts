import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("id-ID", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

export function formatDateTime(dateString: string): string {
  return new Date(dateString).toLocaleString("id-ID", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: "bg-gray-100 text-gray-800",
    in_review: "bg-yellow-100 text-yellow-800",
    approved: "bg-green-100 text-green-800",
    scheduled: "bg-blue-100 text-blue-800",
    publishing: "bg-indigo-100 text-indigo-800",
    published: "bg-emerald-100 text-emerald-800",
    failed: "bg-red-100 text-red-800",
    archived: "bg-gray-100 text-gray-600",
  };
  return colors[status] || "bg-gray-100 text-gray-800";
}

export function getContentTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    youtube_shorts: "YouTube Shorts",
    youtube_longform: "YouTube Long-form",
    tiktok_short: "TikTok Short",
    blog_article: "Blog Article",
    x_post: "X Post",
  };
  return labels[type] || type;
}
