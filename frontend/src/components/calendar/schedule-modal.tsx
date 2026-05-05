"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";

interface ScheduleModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSchedule: (data: {
    content_item_id: string;
    platform_account_id: string;
    scheduled_publish_at: string;
  }) => void;
  contentItemId: string;
  contentTitle: string;
  platformAccounts: { id: string; platform: string; account_name: string }[];
  loading?: boolean;
}

export function ScheduleModal({
  isOpen,
  onClose,
  onSchedule,
  contentItemId,
  contentTitle,
  platformAccounts,
  loading,
}: ScheduleModalProps) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("09:00");
  const [platformAccountId, setPlatformAccountId] = useState(
    platformAccounts[0]?.id || ""
  );

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!date || !time || !platformAccountId) return;

    const scheduledAt = new Date(`${date}T${time}:00`).toISOString();
    onSchedule({
      content_item_id: contentItemId,
      platform_account_id: platformAccountId,
      scheduled_publish_at: scheduledAt,
    });
  };

  const accountOptions = platformAccounts.map((a) => ({
    value: a.id,
    label: `${a.platform.toUpperCase()} - ${a.account_name}`,
  }));

  // Default to tomorrow
  const tomorrow = new Date();
  tomorrow.setDate(tomorrow.getDate() + 1);
  const minDate = tomorrow.toISOString().split("T")[0];

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 w-full max-w-md mx-4 shadow-xl">
        <h3 className="text-lg font-semibold text-gray-900 mb-1">Schedule Publish</h3>
        <p className="text-sm text-gray-500 mb-6 truncate">
          {contentTitle}
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Platform Account */}
          {accountOptions.length > 0 ? (
            <Select
              label="Platform Account"
              options={accountOptions}
              value={platformAccountId}
              onChange={(e) => setPlatformAccountId(e.target.value)}
            />
          ) : (
            <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
              <p className="text-sm text-yellow-700">
                Belum ada platform account yang terhubung. Connect YouTube terlebih dahulu di Settings.
              </p>
            </div>
          )}

          {/* Date & Time */}
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Tanggal"
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              min={minDate}
              required
            />
            <Input
              label="Waktu (WIB)"
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              required
            />
          </div>

          {/* Preview */}
          {date && time && (
            <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-700">
                Akan dipublish pada:{" "}
                <span className="font-medium">
                  {new Date(`${date}T${time}`).toLocaleString("id-ID", {
                    weekday: "long",
                    year: "numeric",
                    month: "long",
                    day: "numeric",
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </span>
              </p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-2">
            <Button type="button" variant="outline" onClick={onClose}>
              Batal
            </Button>
            <Button
              type="submit"
              loading={loading}
              disabled={!date || !time || !platformAccountId}
            >
              Schedule
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
