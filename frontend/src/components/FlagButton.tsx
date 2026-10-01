import { Flag as FlagIcon } from "lucide-react";
import { useState, type FormEvent } from "react";

import { api } from "../api/endpoints";
import type { Flag } from "../api/types";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

const REASONS = [
  ["spam", "Spam or advertising"],
  ["offensive", "Rude or offensive"],
  ["off_topic", "Off-topic"],
  ["other", "Something else"],
] as const;

export function FlagButton({ targetType, targetId }: { targetType: Flag["target_type"]; targetId: number }) {
  const { user } = useAuth();
  const toast = useToast();
  const [open, setOpen] = useState(false);
  const [reason, setReason] = useState<string>("spam");
  const [details, setDetails] = useState("");

  if (!user) return null;

  async function submit(event: FormEvent) {
    event.preventDefault();
    try {
      await api.moderation.flag(targetType, targetId, reason, details);
      toast.success("Thanks — a moderator will review this.");
      setOpen(false);
    } catch (error) {
      toast.error(error);
    }
  }

  return (
    <>
      <button className="btn-ghost px-2 py-1 text-xs" onClick={() => setOpen(true)}>
        <FlagIcon className="h-3.5 w-3.5" /> Flag
      </button>
      {open && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
          role="dialog"
          aria-modal="true"
        >
          <form onSubmit={submit} className="card w-full max-w-md space-y-4 p-6">
            <h2 className="text-lg font-semibold">Flag this {targetType}</h2>
            <div className="space-y-2">
              {REASONS.map(([value, label]) => (
                <label key={value} className="flex items-center gap-2 text-sm">
                  <input
                    type="radio"
                    name="reason"
                    value={value}
                    checked={reason === value}
                    onChange={() => setReason(value)}
                  />
                  {label}
                </label>
              ))}
            </div>
            <textarea
              className="input"
              rows={3}
              maxLength={1000}
              placeholder="Optional details for moderators"
              value={details}
              onChange={(event) => setDetails(event.target.value)}
            />
            <div className="flex justify-end gap-2">
              <button type="button" className="btn-secondary" onClick={() => setOpen(false)}>
                Cancel
              </button>
              <button className="btn-danger">Submit flag</button>
            </div>
          </form>
        </div>
      )}
    </>
  );
}
