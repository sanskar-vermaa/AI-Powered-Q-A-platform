import { query, request } from "./client";
import type {
  Answer,
  ChatMessage,
  Comment,
  Conversation,
  ConversationDetail,
  CurrentUser,
  Flag,
  ImprovedQuestion,
  LeaderboardEntry,
  Notification,
  Page,
  QuestionDetail,
  QuestionSort,
  QuestionSummary,
  SimilarQuestion,
  SiteStats,
  Tag,
  User,
  UserProfile,
} from "./types";

export interface QuestionInput {
  title: string;
  body: string;
  tags: string[];
}

export interface QuestionListParams {
  page?: number;
  page_size?: number;
  sort?: QuestionSort;
  tag?: string;
  q?: string;
  author?: string;
}

export const api = {
  auth: {
    register: (username: string, email: string, password: string) =>
      request<CurrentUser>("POST", "/api/auth/register", { username, email, password }),
    login: (username: string, password: string) =>
      request<{ access_token: string }>("POST", "/api/auth/login", { username, password }),
    me: () => request<CurrentUser>("GET", "/api/auth/me"),
    changePassword: (current_password: string, new_password: string) =>
      request<void>("POST", "/api/auth/change-password", { current_password, new_password }),
  },
  questions: {
    list: (params: QuestionListParams = {}) =>
      request<Page<QuestionSummary>>("GET", `/api/questions${query({ ...params })}`),
    get: (id: number) => request<QuestionDetail>("GET", `/api/questions/${id}`),
    create: (input: QuestionInput) => request<QuestionDetail>("POST", "/api/questions", input),
    update: (id: number, input: Partial<QuestionInput>) =>
      request<QuestionDetail>("PATCH", `/api/questions/${id}`, input),
    remove: (id: number) => request<void>("DELETE", `/api/questions/${id}`),
    vote: (id: number, value: number) =>
      request<{ score: number; my_vote: number }>("POST", `/api/questions/${id}/vote`, { value }),
    accept: (id: number, answerId: number) =>
      request<QuestionDetail>("POST", `/api/questions/${id}/accept/${answerId}`),
    similar: (title: string, body = "") =>
      request<SimilarQuestion[]>("GET", `/api/questions/similar${query({ title, body: body.slice(0, 2000) })}`),
    related: (id: number) => request<SimilarQuestion[]>("GET", `/api/questions/${id}/related`),
    bookmark: (id: number, on: boolean) => request<void>(on ? "PUT" : "DELETE", `/api/questions/${id}/bookmark`),
    comments: (id: number) => request<Comment[]>("GET", `/api/questions/${id}/comments`),
    addComment: (id: number, body: string) => request<Comment>("POST", `/api/questions/${id}/comments`, { body }),
  },
  answers: {
    list: (questionId: number) => request<Answer[]>("GET", `/api/questions/${questionId}/answers`),
    create: (questionId: number, body: string) =>
      request<Answer>("POST", `/api/questions/${questionId}/answers`, { body }),
    update: (id: number, body: string) => request<Answer>("PATCH", `/api/answers/${id}`, { body }),
    remove: (id: number) => request<void>("DELETE", `/api/answers/${id}`),
    vote: (id: number, value: number) =>
      request<{ score: number; my_vote: number }>("POST", `/api/answers/${id}/vote`, { value }),
    comments: (id: number) => request<Comment[]>("GET", `/api/answers/${id}/comments`),
    addComment: (id: number, body: string) => request<Comment>("POST", `/api/answers/${id}/comments`, { body }),
  },
  comments: {
    remove: (id: number) => request<void>("DELETE", `/api/comments/${id}`),
  },
  tags: {
    list: (params: { q?: string; sort?: "popular" | "name"; limit?: number } = {}) =>
      request<Tag[]>("GET", `/api/tags${query(params)}`),
    get: (name: string) => request<Tag>("GET", `/api/tags/${encodeURIComponent(name)}`),
  },
  users: {
    list: (q?: string) => request<User[]>("GET", `/api/users${query({ q })}`),
    profile: (username: string) => request<UserProfile>("GET", `/api/users/${encodeURIComponent(username)}`),
    answers: (username: string) => request<Answer[]>("GET", `/api/users/${encodeURIComponent(username)}/answers`),
    updateMe: (data: { bio?: string; email?: string }) => request<CurrentUser>("PATCH", "/api/users/me", data),
    bookmarks: () => request<QuestionSummary[]>("GET", "/api/me/bookmarks"),
  },
  notifications: {
    list: () => request<Notification[]>("GET", "/api/notifications"),
    unreadCount: () => request<{ unread: number }>("GET", "/api/notifications/unread-count"),
    markRead: (id: number) => request<void>("POST", `/api/notifications/${id}/read`),
    markAllRead: () => request<void>("POST", "/api/notifications/read-all"),
  },
  moderation: {
    flag: (target_type: Flag["target_type"], target_id: number, reason: string, details = "") =>
      request<Flag>("POST", "/api/flags", { target_type, target_id, reason, details }),
    queue: (status = "open") => request<Flag[]>("GET", `/api/moderation/flags${query({ status })}`),
    resolve: (id: number, status: "resolved" | "dismissed", delete_content = false) =>
      request<Flag>("POST", `/api/moderation/flags/${id}`, { status, delete_content }),
    setUser: (id: number, data: { role?: string; is_active?: boolean }) =>
      request<CurrentUser>("PATCH", `/api/admin/users/${id}`, data),
  },
  ai: {
    status: () => request<{ provider: string; live: boolean }>("GET", "/api/ai/status"),
    answer: (questionId: number) => request<Answer>("POST", `/api/ai/questions/${questionId}/answer`),
    suggestTags: (title: string, body: string) =>
      request<{ tags: string[] }>("POST", "/api/ai/suggest-tags", { title, body }),
    improve: (title: string, body: string) =>
      request<ImprovedQuestion>("POST", "/api/ai/improve-question", { title, body }),
    summary: (questionId: number) => request<{ summary: string }>("POST", `/api/ai/questions/${questionId}/summary`),
  },
  chat: {
    conversations: () => request<Conversation[]>("GET", "/api/chat/conversations"),
    conversation: (id: number) => request<ConversationDetail>("GET", `/api/chat/conversations/${id}`),
    remove: (id: number) => request<void>("DELETE", `/api/chat/conversations/${id}`),
    send: (message: string, conversation_id?: number) =>
      request<{ conversation_id: number; reply: ChatMessage }>("POST", "/api/chat", { message, conversation_id }),
  },
  stats: {
    site: () => request<SiteStats>("GET", "/api/stats"),
    leaderboard: (limit = 10) => request<LeaderboardEntry[]>("GET", `/api/stats/leaderboard${query({ limit })}`),
  },
};
