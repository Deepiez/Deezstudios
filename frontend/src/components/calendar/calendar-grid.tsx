"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";
import type { CalendarEvent } from "@/hooks/use-calendar";
import { CalendarEventCard } from "./calendar-event-card";

interface CalendarGridProps {
  year: number;
  month: number; // 0-indexed
  events: CalendarEvent[];
  onEventClick?: (event: CalendarEvent) => void;
  onDayClick?: (date: Date) => void;
}

const DAYS = ["Sen", "Sel", "Rab", "Kam", "Jum", "Sab", "Min"];

export function CalendarGrid({ year, month, events, onEventClick, onDayClick }: CalendarGridProps) {
  const calendarDays = useMemo(() => {
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);

    // Get Monday-based start (0=Mon, 6=Sun)
    let startDayOfWeek = firstDay.getDay() - 1;
    if (startDayOfWeek < 0) startDayOfWeek = 6;

    const days: { date: Date; isCurrentMonth: boolean }[] = [];

    // Previous month padding
    for (let i = startDayOfWeek - 1; i >= 0; i--) {
      const d = new Date(year, month, -i);
      days.push({ date: d, isCurrentMonth: false });
    }

    // Current month
    for (let i = 1; i <= lastDay.getDate(); i++) {
      days.push({ date: new Date(year, month, i), isCurrentMonth: true });
    }

    // Next month padding (fill to 6 rows)
    const remaining = 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({ date: new Date(year, month + 1, i), isCurrentMonth: false });
    }

    return days;
  }, [year, month]);

  const getEventsForDate = (date: Date): CalendarEvent[] => {
    const dateStr = date.toISOString().split("T")[0];
    return events.filter((e) => e.scheduled_at.startsWith(dateStr));
  };

  const today = new Date();
  const isToday = (date: Date) =>
    date.getDate() === today.getDate() &&
    date.getMonth() === today.getMonth() &&
    date.getFullYear() === today.getFullYear();

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Day headers */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {DAYS.map((day) => (
          <div key={day} className="px-2 py-3 text-center text-xs font-medium text-gray-500 uppercase">
            {day}
          </div>
        ))}
      </div>

      {/* Calendar grid */}
      <div className="grid grid-cols-7">
        {calendarDays.map(({ date, isCurrentMonth }, idx) => {
          const dayEvents = getEventsForDate(date);
          return (
            <div
              key={idx}
              className={cn(
                "min-h-[120px] border-b border-r border-gray-100 p-1.5 transition-colors",
                !isCurrentMonth && "bg-gray-50",
                isCurrentMonth && "hover:bg-blue-50/30 cursor-pointer"
              )}
              onClick={() => isCurrentMonth && onDayClick?.(date)}
            >
              {/* Date number */}
              <div className="flex items-center justify-between mb-1">
                <span
                  className={cn(
                    "text-sm font-medium w-7 h-7 flex items-center justify-center rounded-full",
                    !isCurrentMonth && "text-gray-300",
                    isCurrentMonth && "text-gray-700",
                    isToday(date) && "bg-primary-600 text-white"
                  )}
                >
                  {date.getDate()}
                </span>
                {dayEvents.length > 0 && (
                  <span className="text-xs text-gray-400">{dayEvents.length}</span>
                )}
              </div>

              {/* Events */}
              <div className="space-y-1">
                {dayEvents.slice(0, 3).map((event) => (
                  <CalendarEventCard
                    key={event.id}
                    event={event}
                    compact
                    onClick={() => onEventClick?.(event)}
                  />
                ))}
                {dayEvents.length > 3 && (
                  <p className="text-xs text-gray-400 pl-1">+{dayEvents.length - 3} more</p>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
