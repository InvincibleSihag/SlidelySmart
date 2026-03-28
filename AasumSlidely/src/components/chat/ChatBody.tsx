import type { ChatItem, HITLSubmitData } from "../../types";
import { ChatMessage } from "./ChatMessage";
import { EmptyState } from "./EmptyState";
import { ThinkingBlock } from "./ThinkingBlock";
import { HITLForm } from "../hitl/HITLForm";

interface ChatBodyProps {
  chatItems: ChatItem[];
  isGenerating: boolean;
  thinkingText: string;
  onSuggestionClick: (text: string) => void;
  onHITLSubmit: (hitlId: string, data: HITLSubmitData) => void;
  chatEndRef: React.RefObject<HTMLDivElement | null>;
}

export function ChatBody({
  chatItems, isGenerating, thinkingText,
  onSuggestionClick, onHITLSubmit, chatEndRef,
}: ChatBodyProps) {
  return (
    <div className="chat-scroll" style={{
      flex: 1, overflowY: "auto", padding: "24px 28px",
      display: "flex", flexDirection: "column", gap: 16,
    }}>
      {/* Empty state */}
      {chatItems.length === 0 && !isGenerating && (
        <EmptyState onSuggestionClick={onSuggestionClick} />
      )}

      {/* Chat items */}
      {chatItems.map((item, i) => {
        if (item.type === "message") {
          return (
            <ChatMessage
              key={i}
              role={item.role}
              content={item.content}
              timestamp={item.timestamp}
            />
          );
        }

        if (item.type === "hitl") {
          return (
            <HITLForm
              key={item.id}
              hitl={item.hitl}
              isSubmitted={item.submitted}
              submittedData={item.submittedData}
              onSubmit={(data) => onHITLSubmit(item.id, data)}
            />
          );
        }

        return null;
      })}

      {/* Thinking block */}
      {isGenerating && <ThinkingBlock text={thinkingText} />}

      <div ref={chatEndRef} />
    </div>
  );
}
