// ─── Types derived from backend API contracts ───
// Source: app/api/routes.py, app/core/schemas/enums.py,
//         app/services/orchestration/graph/state.py

// ─── Job Status (app/core/schemas/enums.py) ───

export type JobStatus =
  | "queued" | "processing" | "waiting_for_input" | "completed" | "failed";

// ─── HITL (app/services/orchestration/graph/state.py) ───

export interface HITLRequest {
  question: string;
  options: string[] | null;
  form_type: "single_choice" | "multi_choice";
}

export interface HITLSubmitData {
  selected: string[];
  custom: string;
}

// ─── API Request/Response (app/api/routes.py) ───

export interface JobRequest {
  prompt: string;
  job_id?: string;
}

export interface JobResumeRequest {
  human_response: string;
}

export interface JobResponse {
  job_id: string;
}

export interface MessageOut {
  id: string;
  message_type: "human" | "ai";
  message_content: string;
  created_at: string | null;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  result: Record<string, unknown> | null;
  messages: MessageOut[];
  hitl_request: HITLRequest | null;
  slides_html: string | null;
  slide_count: number;
  error_log: string | null;
  created_at: string | null;
  completed_at: string | null;
  current_version: number;
}

// ─── UI Phase (client-side state machine) ───

export type Phase =
  | "idle"
  | "submitting"
  | "queued"
  | "processing"
  | "waiting_for_input"
  | "hitl_submitting"
  | "completed"
  | "failed"
  | "reconnecting";

// ─── Pusher event payloads ───

export interface AgentStatusEvent {
  stage: string;
  message: string;
}

export interface SlidesUpdatedEvent {
  slide_count: number;
}

export interface HitlRequestEvent {
  hitl_request: HITLRequest;
}

// ─── Chat UI types ───

export interface ChatMessageItem {
  type: "message";
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export interface ChatHITLItem {
  type: "hitl";
  id: string;
  hitl: HITLRequest;
  submitted: boolean;
  submittedData: HITLSubmitData | null;
}

export type ChatItem = ChatMessageItem | ChatHITLItem;


