import { useState, useRef, useCallback, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import type { HITLSubmitData } from "../types";
import { useJobStore } from "../stores/job-store";
import { usePusherJob } from "../hooks/usePusherJob";
import { useJobRecovery } from "../hooks/useJobRecovery";
import { postJob, postResumeJob } from "../lib/api";
import { ChatHeader } from "./chat/ChatHeader";
import { ChatBody } from "./chat/ChatBody";
import { ChatInput } from "./chat/ChatInput";
import { SlidePanel } from "./slides/SlidePanel";

export function SlideAgent() {
  const [input, setInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();

  const {
    deckId, phase, chatItems, slidesHtml, slideCount,
    showSlidePanel, lastThinkingText,
    appendChatItem, setPhase, startJob,
    markHitlSubmitted, handleJobFailed,
  } = useJobStore();

  // Recover state on page refresh
  useJobRecovery();

  // Subscribe to Pusher events for active job
  usePusherJob(deckId);

  // Auto-scroll to bottom when chat updates
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatItems, lastThinkingText, phase]);

  const isGenerating = phase === "processing" || phase === "queued" || phase === "submitting";
  const isWaitingHITL = phase === "waiting_for_input";
  const inputDisabled = isGenerating || isWaitingHITL || phase === "hitl_submitting";

  const handleSend = useCallback(async () => {
    if (!input.trim() || inputDisabled) return;
    const msg = input.trim();
    setInput("");

    // Optimistic: add user message immediately
    appendChatItem({
      type: "message",
      role: "user",
      content: msg,
      timestamp: new Date(),
    });

    setPhase("submitting");

    try {
      const response = await postJob({
        prompt: msg,
        job_id: phase === "completed" ? deckId ?? undefined : undefined,
      });

      startJob(response.job_id);
      navigate(`/${response.job_id}`, { replace: true });
    } catch {
      handleJobFailed("Failed to create job. Please try again.");
    }
  }, [input, inputDisabled, deckId, phase, appendChatItem, setPhase, startJob, handleJobFailed, navigate]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleSuggestionClick = useCallback((text: string) => {
    setInput(text);
  }, []);

  const handleHITLSubmit = useCallback(async (hitlId: string, data: HITLSubmitData) => {
    if (!deckId) return;

    markHitlSubmitted(hitlId, data);
    setPhase("hitl_submitting");

    const humanResponse = data.custom || data.selected.join(", ");
    try {
      await postResumeJob(deckId, { human_response: humanResponse });
      setPhase("processing");
    } catch {
      handleJobFailed("Failed to submit response. Please try again.");
    }
  }, [deckId, markHitlSubmitted, setPhase, handleJobFailed]);

  return (
    <div style={{
      width: "100vw", height: "100vh", display: "flex",
      background: "#fff", fontFamily: "'DM Sans', sans-serif", overflow: "hidden",
    }}>
      {/* Left: Chat */}
      <div style={{
        width: showSlidePanel ? "45%" : "100%",
        transition: "width 0.6s cubic-bezier(0.16, 1, 0.3, 1)",
        display: "flex", flexDirection: "column", height: "100%",
      }}>
        <ChatHeader slideCount={slideCount} />

        <ChatBody
          chatItems={chatItems}
          isGenerating={isGenerating}
          thinkingText={lastThinkingText}
          onSuggestionClick={handleSuggestionClick}
          onHITLSubmit={handleHITLSubmit}
          chatEndRef={chatEndRef}
        />

        <ChatInput
          input={input}
          onInputChange={setInput}
          onSend={handleSend}
          onKeyDown={handleKeyDown}
          disabled={inputDisabled}
          isWaitingHITL={isWaitingHITL}
        />
      </div>

      {/* Divider */}
      {showSlidePanel && (
        <div style={{ width: 1, background: "rgba(0,0,0,0.06)", flexShrink: 0 }} />
      )}

      {/* Right: Slide Preview */}
      {showSlidePanel && (
        <SlidePanel
          slidesHtml={slidesHtml}
          isGenerating={isGenerating}
          slideCount={slideCount}
        />
      )}
    </div>
  );
}
