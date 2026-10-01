import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";

import { ErrorMessage } from "../components/Feedback";
import { useAuth } from "../context/AuthContext";

export function validatePassword(password: string): string | undefined {
  if (password.length < 8) return "Password must be at least 8 characters";
  if (!/[a-z]/i.test(password) || !/\d/.test(password)) return "Password must contain a letter and a digit";
  return undefined;
}

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState<string>();
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    const problem = validatePassword(form.password);
    if (!/^[A-Za-z0-9_]{3,32}$/.test(form.username)) {
      setError("Username must be 3–32 letters, digits or underscores");
      return;
    }
    if (problem) {
      setError(problem);
      return;
    }
    setBusy(true);
    setError(undefined);
    try {
      await register(form.username, form.email, form.password);
      navigate("/");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  const field = (name: keyof typeof form) => ({
    id: name,
    value: form[name],
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => setForm({ ...form, [name]: e.target.value }),
  });

  return (
    <div className="mx-auto max-w-md py-8">
      <div className="card p-8">
        <h1 className="text-2xl font-bold">Create your account</h1>
        <p className="mt-1 text-sm text-slate-500">Join the community and get AI-assisted answers.</p>
        <form onSubmit={submit} className="mt-6 space-y-4">
          {error && <ErrorMessage error={error} />}
          <div>
            <label htmlFor="username" className="label">
              Username
            </label>
            <input className="input" autoComplete="username" required {...field("username")} />
          </div>
          <div>
            <label htmlFor="email" className="label">
              Email
            </label>
            <input type="email" className="input" autoComplete="email" required {...field("email")} />
          </div>
          <div>
            <label htmlFor="password" className="label">
              Password
            </label>
            <input type="password" className="input" autoComplete="new-password" required {...field("password")} />
            <p className="mt-1 text-xs text-slate-500">At least 8 characters, including a letter and a digit.</p>
          </div>
          <button className="btn-primary w-full" disabled={busy}>
            {busy ? "Creating account…" : "Sign up"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          Already have an account?{" "}
          <Link to="/login" className="font-medium text-brand-600 hover:underline">
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
