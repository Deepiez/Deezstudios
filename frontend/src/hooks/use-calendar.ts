"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { PublishJob, ContentItem } from "@/types";

export interface CalendarEvent {
  id: string;
  content_item_id: string;
  title: string;
  content_type: string;
  status: string;
  scheduled_at: string;
  platform: string;
  platform_account_id: string;
}

interface ScheduleRequest {
  content_item_id: string;
  platform_account_id: string;
  scheduled_publish_at: string;
  publish_data?: Record<string, unknown>;
}

export function useCalendar() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchCalendar = async (startDate: string, endDate: string, brandId?: string) => {
    setLoading(true);
    try {
      const params: Record<string, string> = { start_date: startDate, end_date: endDate };
      if (brandId) params.brand_id = brandId;
      const response = await api.get<CalendarEvent[]>("/calendar/", { params });
      setEvents(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to load calendar");
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const scheduleContent = async (data: ScheduleRequest): Promise<PublishJob | null> => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.post<PublishJob>("/calendar/schedule", data);
      return response.data;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to schedule content");
      return null;
    } finally {
      setLoading(false);
    }
  };

  const reschedule = async (jobId: string, newDate: string): Promise<boolean> => {
    try {
      await api.put(`/calendar/schedule/${jobId}`, { scheduled_publish_at: newDate });
      return true;
    } catch (err) {
      return false;
    }
  };

  const cancelSchedule = async (jobId: string): Promise<boolean> => {
    try {
      await api.delete(`/calendar/schedule/${jobId}`);
      return true;
    } catch (err) {
      return false;
    }
  };

  const publishNow = async (jobId: string): Promise<boolean> => {
    setLoading(true);
    try {
      await api.post(`/calendar/publish/${jobId}/run`);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.detail || "Failed to publish");
      return false;
    } finally {
      setLoading(false);
    }
  };

  return { events, loading, error, fetchCalendar, scheduleContent, reschedule, cancelSchedule, publishNow };
}
