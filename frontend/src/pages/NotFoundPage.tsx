import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center gap-4 py-24 text-center">
      <p className="text-6xl font-bold text-brand-600">404</p>
      <h1 className="text-xl font-semibold">Page not found</h1>
      <p className="text-slate-500">The page you're looking for doesn't exist or was removed.</p>
      <Link to="/" className="btn-primary">
        Back to home
      </Link>
    </div>
  );
}
