// ─── Types derived from backend API contracts ───
// Source: app/api/routes.py, app/core/schemas/enums.py,
//         app/services/agents/graph/state.py

// ─── Job Status (app/core/schemas/enums.py) ───

export type JobStatus =
  | "queued" | "processing" | "waiting_for_input" | "completed" | "failed";

// ─── HITL (app/services/agents/graph/state.py) ───

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

export interface JobCreateRequest {
  prompt: string;
}

export interface JobResumeRequest {
  human_response: string;
}

export interface JobContinueRequest {
  prompt: string;
}

export interface JobResponse {
  job_id: string;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  result: Record<string, unknown> | null;
  slides_html: string | null;
  error_log: string | null;
  created_at: string | null;
  completed_at: string | null;
  current_version: number;
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

// ─── Thinking steps ───

export interface ThinkingStepData {
  label: string;
}
