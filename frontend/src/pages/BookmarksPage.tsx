import { api } from "../api/endpoints";
import { EmptyState, ErrorMessage, Spinner } from "../components/Feedback";
import { QuestionCard } from "../components/QuestionCard";
import { useAsync } from "../hooks/useAsync";

export function BookmarksPage() {
  const bookmarks = useAsync(() => api.users.bookmarks(), []);
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Bookmarks</h1>
      <div className="card">
        {bookmarks.loading ? (
          <Spinner />
        ) : bookmarks.error ? (
          <div className="p-4">
            <ErrorMessage error={bookmarks.error} onRetry={bookmarks.reload} />
          </div>
        ) : bookmarks.data?.length ? (
          bookmarks.data.map((q) => <QuestionCard key={q.id} question={q} />)
        ) : (
          <EmptyState title="No bookmarks yet">
            <p className="text-sm">Use the bookmark icon on a question to save it for later.</p>
          </EmptyState>
        )}
      </div>
    </div>
  );
}
