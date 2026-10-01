export type Role = "user" | "moderator" | "admin";

export interface User {
  id: number;
  username: string;
  bio: string;
  reputation: number;
  role: Role;
  created_at: string;
}

export interface CurrentUser extends User {
  email: string;
}

export interface UserProfile extends User {
  question_count: number;
  answer_count: number;
  badges: string[];
}

export interface QuestionSummary {
  id: number;
  title: string;
  excerpt: string;
  author: User;
  tags: string[];
  score: number;
  views: number;
  answer_count: number;
  has_accepted_answer: boolean;
  created_at: string;
}

export interface QuestionDetail {
  id: number;
  title: string;
  body: string;
  author: User;
  tags: string[];
  score: number;
  views: number;
  answer_count: number;
  accepted_answer_id: number | null;
  created_at: string;
  updated_at: string;
  my_vote: number;
  bookmarked: boolean;
}

export interface Answer {
  id: number;
  question_id: number;
  body: string;
  author: User | null;
  is_ai: boolean;
  is_accepted: boolean;
  score: number;
  created_at: string;
  updated_at: string;
  my_vote: number;
}

export interface Comment {
  id: number;
  body: string;
  author: User;
  question_id: number | null;
  answer_id: number | null;
  created_at: string;
}

export interface Page<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export interface Tag {
  id: number;
  name: string;
  description: string;
  question_count: number;
}

export interface SimilarQuestion {
  id: number;
  title: string;
  score: number;
}

export interface Notification {
  id: number;
  kind: string;
  message: string;
  link: string;
  is_read: boolean;
  created_at: string;
}

export interface Flag {
  id: number;
  reporter: User;
  target_type: "question" | "answer" | "comment";
  target_id: number;
  reason: string;
  details: string;
  status: string;
  created_at: string;
}

export interface SiteStats {
  users: number;
  questions: number;
  answers: number;
  ai_answers: number;
  tags: number;
  answered_ratio: number;
}

export interface LeaderboardEntry {
  username: string;
  reputation: number;
  answer_count: number;
}

export interface ChatMessage {
  id: number;
  role: "user" | "assistant";
  content: string;
  created_at: string;
}

export interface Conversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: ChatMessage[];
}

export interface ImprovedQuestion {
  title: string;
  body: string;
  tips: string[];
}

export type QuestionSort = "newest" | "votes" | "views" | "unanswered" | "active";
