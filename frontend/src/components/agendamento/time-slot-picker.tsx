"use client";

import { cn } from "@/lib/utils/cn";
import type { TimeSlot } from "@/types/professional";

interface TimeSlotPickerProps {
  slots: TimeSlot[];
  selectedTime: string;
  onSelect: (time: string) => void;
  isLoading?: boolean;
}

export function TimeSlotPicker({
  slots,
  selectedTime,
  onSelect,
  isLoading,
}: TimeSlotPickerProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-4 gap-2">
        {Array.from({ length: 12 }).map((_, i) => (
          <div
            key={i}
            className="h-10 rounded-md bg-gray-100 animate-pulse"
          />
        ))}
      </div>
    );
  }

  if (slots.length === 0) {
    return (
      <p className="text-sm text-gray-500 text-center py-4">
        Nenhum horário disponível para esta data.
      </p>
    );
  }

  return (
    <div className="grid grid-cols-4 gap-2">
      {slots.map((slot) => (
        <button
          key={slot.time}
          type="button"
          disabled={!slot.available}
          onClick={() => onSelect(slot.time)}
          className={cn(
            "h-10 rounded-md text-sm font-medium transition-colors",
            slot.available
              ? selectedTime === slot.time
                ? "bg-blue-600 text-white"
                : "bg-white border border-gray-300 hover:border-blue-400 hover:bg-blue-50 text-gray-700"
              : "bg-gray-100 text-gray-400 cursor-not-allowed line-through"
          )}
        >
          {slot.time}
        </button>
      ))}
    </div>
  );
}
