"use client";

import { useMemo } from "react";
import { cn } from "@/lib/utils";
import type { CalendarEvent } from "@/hooks/use-calendar";
import { CalendarEventCard } from "./calendar-event-card";

interface WeekViewProps {
  startDate: Date; // Monday of the week
  events: CalendarEvent[];
  onEventClick?: (event: CalendarEvent) => void;
}

const HOURS = Array.from({ length: 16 }, (_, i) => i + 6); // 06:00 - 21:00

export function WeekView({ startDate, events, onEventClick }: WeekViewProps) {
  const weekDays = useMemo(() => {
    return Array.from({ length: 7 }, (_, i) => {
      const d = new Date(startDate);
      d.setDate(d.getDate() + i);
      return d;
    });
  }, [startDate]);

  const getEventsForDay = (date: Date): CalendarEvent[] => {
    const dateStr = date.toISOString().split("T")[0];
    return events.filter((e) => e.scheduled_at.startsWith(dateStr));
  };

  const today = new Date();
  const isToday = (date: Date) =>
    date.toISOString().split("T")[0] === today.toISOString().split("T")[0];

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
      {/* Day headers */}
      <div className="grid grid-cols-7 border-b border-gray-200">
        {weekDays.map((day, i) => (
          <div
            key={i}
            className={cn(
              "px-3 py-3 text-center border-r border-gray-100 last:border-r-0",
              isToday(day) && "bg-primary-50"
            )}
          >
            <p className="text-xs text-gray-500 uppercase">
              {day.toLocaleDateString("id-ID", { weekday: "short" })}
            </p>
            <p
              className={cn(
                "text-lg font-semibold mt-0.5",
                isToday(day) ? "text-primary-600" : "text-gray-900"
              )}
            >
              {day.getDate()}
            </p>
          </div>
        ))}
      </div>

      {/* Events per day */}
      <div className="grid grid-cols-7 min-h-[400px]">
        {weekDays.map((day, i) => {
          const dayEvents = getEventsForDay(day);
          return (
            <div
              key={i}
              className={cn(
                "border-r border-gray-100 last:border-r-0 p-2 space-y-2",
                isToday(day) && "bg-primary-50/30"
              )}
            >
              {dayEvents.length === 0 ? (
                <p className="text-xs text-gray-300 text-center mt-8">No events</p>
              ) : (
                dayEvents.map((event) => (
                  <CalendarEventCard
                    key={event.id}
                    event={event}
                    onClick={() => onEventClick?.(event)}
                  />
                ))
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
