import { useState, type FormEvent } from "react";

import { api } from "../api/endpoints";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { validatePassword } from "./RegisterPage";

export function SettingsPage() {
  const { user, refresh } = useAuth();
  const toast = useToast();
  const [bio, setBio] = useState(user?.bio ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [passwords, setPasswords] = useState({ current: "", next: "" });

  async function saveProfile(event: FormEvent) {
    event.preventDefault();
    try {
      await api.users.updateMe({ bio, email });
      await refresh();
      toast.success("Profile saved");
    } catch (error) {
      toast.error(error);
    }
  }

  async function changePassword(event: FormEvent) {
    event.preventDefault();
    const problem = validatePassword(passwords.next);
    if (problem) {
      toast.error(problem);
      return;
    }
    try {
      await api.auth.changePassword(passwords.current, passwords.next);
      setPasswords({ current: "", next: "" });
      toast.success("Password changed");
    } catch (error) {
      toast.error(error);
    }
  }

  return (
    <div className="max-w-2xl space-y-6">
      <h1 className="text-2xl font-bold">Settings</h1>
      <form onSubmit={saveProfile} className="card space-y-4 p-6">
        <h2 className="font-semibold">Profile</h2>
        <div>
          <label htmlFor="email" className="label">
            Email
          </label>
          <input id="email" type="email" className="input" value={email} onChange={(e) => setEmail(e.target.value)} />
        </div>
        <div>
          <label htmlFor="bio" className="label">
            Bio
          </label>
          <textarea
            id="bio"
            className="input"
            rows={4}
            maxLength={1000}
            value={bio}
            onChange={(e) => setBio(e.target.value)}
          />
        </div>
        <button className="btn-primary">Save profile</button>
      </form>
      <form onSubmit={changePassword} className="card space-y-4 p-6">
        <h2 className="font-semibold">Change password</h2>
        <div>
          <label htmlFor="current" className="label">
            Current password
          </label>
          <input
            id="current"
            type="password"
            className="input"
            autoComplete="current-password"
            value={passwords.current}
            onChange={(e) => setPasswords({ ...passwords, current: e.target.value })}
          />
        </div>
        <div>
          <label htmlFor="next" className="label">
            New password
          </label>
          <input
            id="next"
            type="password"
            className="input"
            autoComplete="new-password"
            value={passwords.next}
            onChange={(e) => setPasswords({ ...passwords, next: e.target.value })}
          />
        </div>
        <button className="btn-primary" disabled={!passwords.current || !passwords.next}>
          Update password
        </button>
      </form>
    </div>
  );
}
