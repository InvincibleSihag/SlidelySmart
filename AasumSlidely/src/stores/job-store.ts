import { create } from "zustand";
import type {
  AgentStatusEvent,
  ChatItem,
  HITLSubmitData,
  HitlRequestEvent,
  JobStatusResponse,
  Phase,
  SlidesUpdatedEvent,
} from "../types";

interface JobStore {
  // --- State ---
  deckId: string | null;
  phase: Phase;
  chatItems: ChatItem[];
  slidesHtml: string | null;
  slideCount: number;
  showSlidePanel: boolean;
  lastThinkingText: string;
  errorMessage: string | null;

  // --- Actions ---
  setPhase: (phase: Phase) => void;
  setDeckId: (deckId: string) => void;
  appendChatItem: (item: ChatItem) => void;
  markHitlSubmitted: (hitlId: string, data: HITLSubmitData) => void;
  setSlidesHtml: (html: string | null) => void;
  setSlideCount: (count: number) => void;

  startJob: (deckId: string) => void;
  handleAgentStatus: (data: AgentStatusEvent) => void;
  handleSlidesUpdated: (data: SlidesUpdatedEvent) => void;
  handleHitlRequest: (data: HitlRequestEvent) => void;
  handleJobCompleted: () => void;
  handleJobFailed: (error: string) => void;
  hydrateFromServer: (state: JobStatusResponse) => void;
  reset: () => void;
}

export const useJobStore = create<JobStore>((set) => ({
  deckId: null,
  phase: "idle",
  chatItems: [],
  slidesHtml: null,
  slideCount: 0,
  showSlidePanel: false,
  lastThinkingText: "",
  errorMessage: null,

  setPhase: (phase) => set({ phase }),
  setDeckId: (deckId) => set({ deckId }),

  appendChatItem: (item) =>
    set((s) => ({ chatItems: [...s.chatItems, item] })),

  markHitlSubmitted: (hitlId, data) =>
    set((s) => ({
      chatItems: s.chatItems.map((item) =>
        item.type === "hitl" && item.id === hitlId
          ? { ...item, submitted: true, submittedData: data }
          : item,
      ),
    })),

  setSlidesHtml: (html) => set({ slidesHtml: html }),
  setSlideCount: (count) => set({ slideCount: count }),

  startJob: (deckId) =>
    set({
      deckId,
      phase: "queued",
      showSlidePanel: true,
      lastThinkingText: "",
      errorMessage: null,
    }),

  handleAgentStatus: (data) =>
    set((s) => ({
      phase: s.phase === "queued" || s.phase === "hitl_submitting"
        ? "processing"
        : s.phase,
      lastThinkingText: data.message,
    })),

  handleSlidesUpdated: (data) =>
    set({ slideCount: data.slide_count }),

  handleHitlRequest: (data) =>
    set((s) => ({
      phase: "waiting_for_input",
      lastThinkingText: "",
      chatItems: [
        ...s.chatItems,
        {
          type: "hitl" as const,
          id: `hitl-${Date.now()}`,
          hitl: data.hitl_request,
          submitted: false,
          submittedData: null,
        },
      ],
    })),

  handleJobCompleted: () =>
    set({ phase: "completed", lastThinkingText: "" }),

  handleJobFailed: (error) =>
    set({ phase: "failed", lastThinkingText: "", errorMessage: error }),

  hydrateFromServer: (serverState) => {
    const chatItems: ChatItem[] = serverState.messages.map((m) => ({
      type: "message" as const,
      role: m.message_type === "human" ? ("user" as const) : ("assistant" as const),
      content: m.message_content,
      timestamp: new Date(m.created_at ?? ""),
    }));

    // Reconstruct HITL form if waiting for input
    if (
      serverState.hitl_request &&
      serverState.status === "waiting_for_input"
    ) {
      chatItems.push({
        type: "hitl",
        id: `hitl-${Date.now()}`,
        hitl: serverState.hitl_request,
        submitted: false,
        submittedData: null,
      });
    }

    const phase: Phase =
      serverState.status === "waiting_for_input"
        ? "waiting_for_input"
        : serverState.status === "processing"
          ? "processing"
          : serverState.status === "completed"
            ? "completed"
            : serverState.status === "failed"
              ? "failed"
              : serverState.status === "queued"
                ? "queued"
                : "idle";

    set({
      deckId: serverState.job_id,
      chatItems,
      phase,
      slidesHtml: serverState.slides_html,
      slideCount: serverState.slide_count,
      showSlidePanel:
        !!serverState.slides_html || serverState.status === "processing",
      lastThinkingText: "",
      errorMessage: serverState.error_log,
    });
  },

  reset: () =>
    set({
      deckId: null,
      phase: "idle",
      chatItems: [],
      slidesHtml: null,
      slideCount: 0,
      showSlidePanel: false,
      lastThinkingText: "",
      errorMessage: null,
    }),
}));
