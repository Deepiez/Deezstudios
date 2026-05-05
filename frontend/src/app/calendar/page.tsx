"use client";

import { useEffect, useState, useMemo } from "react";
import { useRouter } from "next/navigation";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { CalendarGrid } from "@/components/calendar/calendar-grid";
import { WeekView } from "@/components/calendar/week-view";
import { CalendarEventCard } from "@/components/calendar/calendar-event-card";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardContent } from "@/components/ui/card";
import { useCalendar, type CalendarEvent } from "@/hooks/use-calendar";

type ViewMode = "month" | "week";

export default function CalendarPage() {
  const router = useRouter();
  const { events, loading, fetchCalendar } = useCalendar();

  const [viewMode, setViewMode] = useState<ViewMode>("month");
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  // Calculate date range for fetching
  const { startDate, endDate } = useMemo(() => {
    if (viewMode === "month") {
      const start = new Date(year, month, 1);
      const end = new Date(year, month + 1, 0);
      return {
        startDate: start.toISOString().split("T")[0],
        endDate: end.toISOString().split("T")[0],
      };
    } else {
      // Week view - get Monday of current week
      const d = new Date(currentDate);
      const day = d.getDay();
      const diff = d.getDate() - day + (day === 0 ? -6 : 1);
      const monday = new Date(d.setDate(diff));
      const sunday = new Date(monday);
      sunday.setDate(sunday.getDate() + 6);
      return {
        startDate: monday.toISOString().split("T")[0],
        endDate: sunday.toISOString().split("T")[0],
      };
    }
  }, [year, month, viewMode, currentDate]);

  useEffect(() => {
    fetchCalendar(startDate, endDate);
  }, [startDate, endDate]);

  // Navigation
  const goNext = () => {
    const d = new Date(currentDate);
    if (viewMode === "month") {
      d.setMonth(d.getMonth() + 1);
    } else {
      d.setDate(d.getDate() + 7);
    }
    setCurrentDate(d);
  };

  const goPrev = () => {
    const d = new Date(currentDate);
    if (viewMode === "month") {
      d.setMonth(d.getMonth() - 1);
    } else {
      d.setDate(d.getDate() - 7);
    }
    setCurrentDate(d);
  };

  const goToday = () => setCurrentDate(new Date());

  // Get Monday of current week for week view
  const weekStart = useMemo(() => {
    const d = new Date(currentDate);
    const day = d.getDay();
    const diff = d.getDate() - day + (day === 0 ? -6 : 1);
    return new Date(d.setDate(diff));
  }, [currentDate]);

  const monthLabel = currentDate.toLocaleDateString("id-ID", {
    month: "long",
    year: "numeric",
  });

  const weekLabel = `${weekStart.toLocaleDateString("id-ID", { day: "numeric", month: "short" })} - ${new Date(
    weekStart.getTime() + 6 * 86400000
  ).toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" })}`;

  // Upcoming events (next 7 days)
  const upcomingEvents = useMemo(() => {
    const now = new Date();
    const nextWeek = new Date(now.getTime() + 7 * 86400000);
    return events
      .filter((e) => {
        const d = new Date(e.scheduled_at);
        return d >= now && d <= nextWeek;
      })
      .sort((a, b) => new Date(a.scheduled_at).getTime() - new Date(b.scheduled_at).getTime());
  }, [events]);

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Content Calendar</h1>
          <p className="text-sm text-gray-500 mt-1">
            Jadwal publish dan rencana konten
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Main Calendar (3/4) */}
        <div className="lg:col-span-3">
          {/* Calendar Controls */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <Button variant="outline" size="sm" onClick={goPrev}>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5L8.25 12l7.5-7.5" />
                </svg>
              </Button>
              <h2 className="text-lg font-semibold text-gray-900 min-w-[200px] text-center">
                {viewMode === "month" ? monthLabel : weekLabel}
              </h2>
              <Button variant="outline" size="sm" onClick={goNext}>
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
                </svg>
              </Button>
              <Button variant="ghost" size="sm" onClick={goToday}>
                Today
              </Button>
            </div>

            {/* View Toggle */}
            <div className="flex items-center bg-gray-100 rounded-lg p-0.5">
              <button
                onClick={() => setViewMode("month")}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  viewMode === "month"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Month
              </button>
              <button
                onClick={() => setViewMode("week")}
                className={`px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                  viewMode === "week"
                    ? "bg-white text-gray-900 shadow-sm"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Week
              </button>
            </div>
          </div>

          {/* Calendar View */}
          {loading ? (
            <div className="flex items-center justify-center py-20 bg-white rounded-xl border border-gray-200">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
            </div>
          ) : viewMode === "month" ? (
            <CalendarGrid
              year={year}
              month={month}
              events={events}
              onEventClick={setSelectedEvent}
              onDayClick={(date) => {
                // Could open schedule modal for that date
              }}
            />
          ) : (
            <WeekView
              startDate={weekStart}
              events={events}
              onEventClick={setSelectedEvent}
            />
          )}
        </div>

        {/* Sidebar (1/4) */}
        <div className="space-y-6">
          {/* Selected Event Detail */}
          {selectedEvent && (
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-semibold text-gray-900">Event Detail</h3>
                  <button
                    onClick={() => setSelectedEvent(null)}
                    className="text-gray-400 hover:text-gray-600"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm font-medium text-gray-900">{selectedEvent.title}</p>
                  <p className="text-xs text-gray-500 capitalize mt-1">
                    {selectedEvent.content_type.replace("_", " ")} - {selectedEvent.platform}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Scheduled</p>
                  <p className="text-sm text-gray-700">
                    {new Date(selectedEvent.scheduled_at).toLocaleString("id-ID", {
                      weekday: "long",
                      day: "numeric",
                      month: "long",
                      year: "numeric",
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Status</p>
                  <p className="text-sm font-medium text-gray-700 capitalize">{selectedEvent.status}</p>
                </div>
                <div className="flex gap-2 pt-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="flex-1"
                    onClick={() => router.push(`/content/${selectedEvent.content_item_id}`)}
                  >
                    View Content
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upcoming */}
          <Card>
            <CardHeader>
              <h3 className="text-sm font-semibold text-gray-900">Upcoming (7 days)</h3>
            </CardHeader>
            <CardContent>
              {upcomingEvents.length === 0 ? (
                <p className="text-sm text-gray-400 text-center py-4">
                  Tidak ada jadwal dalam 7 hari ke depan
                </p>
              ) : (
                <div className="space-y-2">
                  {upcomingEvents.slice(0, 8).map((event) => (
                    <div
                      key={event.id}
                      className="flex items-center gap-2 cursor-pointer hover:bg-gray-50 rounded p-1.5 -mx-1.5"
                      onClick={() => setSelectedEvent(event)}
                    >
                      <div className="w-1.5 h-1.5 rounded-full bg-primary-500" />
                      <div className="flex-1 min-w-0">
                        <p className="text-xs font-medium text-gray-700 truncate">
                          {event.title}
                        </p>
                        <p className="text-xs text-gray-400">
                          {new Date(event.scheduled_at).toLocaleDateString("id-ID", {
                            weekday: "short",
                            day: "numeric",
                            month: "short",
                            hour: "2-digit",
                            minute: "2-digit",
                          })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Legend */}
          <Card>
            <CardContent className="py-3">
              <p className="text-xs font-medium text-gray-500 mb-2">Platform</p>
              <div className="space-y-1.5">
                <LegendItem color="bg-red-500" label="YouTube" />
                <LegendItem color="bg-pink-500" label="TikTok" />
                <LegendItem color="bg-gray-500" label="X (Twitter)" />
                <LegendItem color="bg-blue-500" label="Blog" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}

function LegendItem({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-2">
      <div className={`w-3 h-1.5 rounded-full ${color}`} />
      <span className="text-xs text-gray-600">{label}</span>
    </div>
  );
}
