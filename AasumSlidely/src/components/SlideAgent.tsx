import { useState, useEffect, useRef, useCallback } from "react";
import type { ChatItem, HITLSubmitData, JobStatus, ThinkingStepData } from "../types";
import { ChatHeader } from "./chat/ChatHeader";
import { ChatBody } from "./chat/ChatBody";
import { ChatInput } from "./chat/ChatInput";
import { SlidePanel } from "./slides/SlidePanel";

const THINKING_STEPS: ThinkingStepData[] = [
  { label: "Understanding request" },
  { label: "Structuring narrative" },
  { label: "Designing layout" },
  { label: "Generating content" },
  { label: "Refining visuals" },
];

export function SlideAgent() {
  const [chatItems, setChatItems] = useState<ChatItem[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState<JobStatus | "ready">("ready");
  const [thinkingStep, setThinkingStep] = useState(-1);
  const [completedSteps, setCompletedSteps] = useState<Set<number>>(new Set());
  const [showSlidePanel, setShowSlidePanel] = useState(false);
  const [slidesHtml, setSlidesHtml] = useState<string | null>(null);
  const [slideCount, setSlideCount] = useState(0);
  const chatEndRef = useRef<HTMLDivElement | null>(null);

  const isGenerating = status === "processing";
  const isWaitingHITL = status === "waiting_for_input";
  const inputDisabled = isGenerating || isWaitingHITL;

  const scrollToBottom = useCallback(() => {
    setTimeout(() => chatEndRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
  }, []);

  useEffect(scrollToBottom, [chatItems, thinkingStep, isWaitingHITL, scrollToBottom]);

  // ─── Placeholder handlers (business logic will replace these) ───

  const handleSend = useCallback(() => {
    if (!input.trim() || inputDisabled) return;
    const msg = input.trim();
    setInput("");

    setChatItems((prev) => [
      ...prev,
      { type: "message", role: "user", content: msg, timestamp: new Date() },
    ]);

    // TODO: call API to create job, start polling
    // For now just show the panel
    setShowSlidePanel(true);
    setStatus("processing");
    setThinkingStep(0);

    // Simulate thinking steps (will be replaced by real polling)
    void (async () => {
      for (let i = 0; i < THINKING_STEPS.length; i++) {
        setThinkingStep(i);
        await new Promise((r) => setTimeout(r, 1200));
        setCompletedSteps((prev) => new Set([...prev, i]));
      }
      setThinkingStep(-1);
      setStatus("completed");
      setChatItems((prev) => [
        ...prev,
        {
          type: "message", role: "assistant",
          content: "Your presentation is ready. Click any slide to preview it, or ask me to adjust anything.",
          timestamp: new Date(),
        },
      ]);
    })();
  }, [input, inputDisabled]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }, [handleSend]);

  const handleSuggestionClick = useCallback((text: string) => {
    setInput(text);
  }, []);

  const handleHITLSubmit = useCallback((_hitlId: string, _data: HITLSubmitData) => {
    // TODO: call API to resume job with human response
  }, []);

  // Reset for new conversation — exposed for future use
  void setSlidesHtml;
  void setSlideCount;

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
        <ChatHeader status={status} slideCount={slideCount} />

        <ChatBody
          chatItems={chatItems}
          isGenerating={isGenerating}
          thinkingSteps={THINKING_STEPS}
          activeThinkingStep={thinkingStep}
          completedSteps={completedSteps}
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
