"use client";

import { cn } from "@/lib/utils";
import type { CalendarEvent } from "@/hooks/use-calendar";

interface CalendarEventCardProps {
  event: CalendarEvent;
  compact?: boolean;
  onClick?: () => void;
}

const platformColors: Record<string, { bg: string; text: string; border: string }> = {
  youtube: { bg: "bg-red-50", text: "text-red-700", border: "border-l-red-500" },
  tiktok: { bg: "bg-pink-50", text: "text-pink-700", border: "border-l-pink-500" },
  x: { bg: "bg-gray-50", text: "text-gray-700", border: "border-l-gray-500" },
  blog: { bg: "bg-blue-50", text: "text-blue-700", border: "border-l-blue-500" },
};

const statusIcons: Record<string, string> = {
  queued: "⏳",
  processing: "⚙️",
  scheduled: "📅",
  published: "✅",
  failed: "❌",
};

export function CalendarEventCard({ event, compact = false, onClick }: CalendarEventCardProps) {
  const colors = platformColors[event.platform] || platformColors.blog;
  const time = new Date(event.scheduled_at).toLocaleTimeString("id-ID", {
    hour: "2-digit",
    minute: "2-digit",
  });

  if (compact) {
    return (
      <div
        onClick={(e) => {
          e.stopPropagation();
          onClick?.();
        }}
        className={cn(
          "px-1.5 py-0.5 rounded text-xs truncate cursor-pointer border-l-2",
          colors.bg,
          colors.text,
          colors.border
        )}
        title={`${event.title} - ${time}`}
      >
        {event.title}
      </div>
    );
  }

  return (
    <div
      onClick={onClick}
      className={cn(
        "p-3 rounded-lg border-l-4 cursor-pointer transition-shadow hover:shadow-md",
        colors.bg,
        colors.border
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex-1 min-w-0">
          <p className={cn("text-sm font-medium truncate", colors.text)}>{event.title}</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-gray-500">{time}</span>
            <span className="text-xs text-gray-400 capitalize">{event.platform}</span>
            <span className="text-xs text-gray-400 capitalize">{event.content_type.replace("_", " ")}</span>
          </div>
        </div>
        <span className="text-sm" title={event.status}>
          {statusIcons[event.status] || "📄"}
        </span>
      </div>
    </div>
  );
}
