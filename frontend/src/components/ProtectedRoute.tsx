import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { Spinner } from "./Feedback";

export function ProtectedRoute({ children, staff = false }: { children: ReactNode; staff?: boolean }) {
  const { user, loading } = useAuth();
  const location = useLocation();
  if (loading) return <Spinner />;
  if (!user) return <Navigate to={`/login?next=${encodeURIComponent(location.pathname + location.search)}`} replace />;
  if (staff && user.role === "user") return <Navigate to="/" replace />;
  return <>{children}</>;
}
